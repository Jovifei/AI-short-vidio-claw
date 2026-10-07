#!/usr/bin/env python3
"""Isolated single-image requests from V5. No network, GPU, or user approvals.

Build prepares requests and copies real input crops, not completed keyframes.
Request emits one prompt only after its dependency images pass recorded art QA.
Inspect checks bytes/layout and explicit remote QA; it never grants user approval.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from PIL import Image, ImageOps
from preproduction import check_plan, read_json, sha256_file, require, ContractError

CONFIG = 'config/remote_image_jobs.json'
REGISTRY = 'assets/registry/generated_assets_v5.json'
FACE = {'DAIYU': 'DAIYU_FACE_CROP', 'WUKONG': 'WUKONG_FACE_CROP'}
SEMANTIC_KEYS = ('single_scene', 'identity_matches_direction', 'costume_matches_task',
                 'anatomy_and_continuity', 'no_text_or_watermark')


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def safe(root, relative):
    require(isinstance(relative, str) and relative, 'missing path')
    require(not re.search(r'[:\\\x00-\x1f]', relative), 'unsafe path')
    parts = relative.split('/')
    require(all(p not in ('', '.', '..') and not p.endswith((' ', '.')) for p in parts), 'unsafe path')
    p = Path(root).resolve()
    for part in parts:
        p /= part
        require(not p.is_symlink() and not getattr(p, 'is_junction', lambda: False)(), 'link forbidden')
    require(p.resolve().is_relative_to(Path(root).resolve()), 'path escape')
    return p


def unique(items):
    return list(dict.fromkeys(items))


def validate_dag(tasks):
    ids = [t['id'] for t in tasks]
    require(len(ids) == len(set(ids)), 'duplicate task ID')
    table = {t['id']: t for t in tasks}
    visiting, done = set(), set()
    def walk(k):
        require(k in table, 'missing dependency: ' + k)
        require(k not in visiting, 'cyclic dependency: ' + k)
        if k in done:
            return
        visiting.add(k)
        for dep in table[k]['depends_on']:
            walk(dep)
        visiting.remove(k)
        done.add(k)
    for k in ids:
        walk(k)
    return table


def image_check(path, contract):
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        w, h = im.size
        require(getattr(im, 'n_frames', 1) == 1, 'animated/multi-frame output rejected')
        require(min(w, h) >= contract['min_short_edge'], 'thumbnail/low-resolution output rejected')
        ratio = contract['width'] / contract['height']
        require(abs(w / h - ratio) / ratio <= contract['aspect_tolerance'], 'wrong aspect/layout: not independent vertical scene')
        return {'width': w, 'height': h, 'sha256': sha256_file(path), 'bytes': path.stat().st_size}


def compile_tasks(config, plans):
    tasks = []
    for r in config['wardrobe']:
        tasks.append(dict(r, kind='REFERENCE_CANDIDATE', source_asset_ids=[FACE[c] for c in r['characters']],
                          output_contract=config['output'], user_approved=False))
    for project, plan in plans.items():
        check_plan(plan)
        for shot in plan['shots']:
            deps = [config['stage_dependencies'][v] for v in shot['costume_stages'].values()]
            sid = shot['shot_id']
            if project == 'EP001':
                n = int(sid[2:])
                deps += ['STATE_W_HAND_PRE' if n < 5 else 'STATE_W_HAND_BANDAGED']
                if n == 19:
                    deps += ['STATE_W_RAIN']
                brief = '\n'.join(f'{k}：{shot[k]}' for k in ('location', 'composition', 'start_state', 'visible_action', 'continuity_lock') if k in shot)
            else:
                brief = config['look_details'].get(sid, '')
            if project == 'LOOKREEL01' and sid == 'COMP10':
                for i, brief in enumerate(config['comp10_panels'], 1):
                    tasks.append({'id': f'LOOKREEL01_COMP10_P{i}', 'kind': 'KEYFRAME_PANEL_CANDIDATE',
                                  'project_id': project, 'shot_id': sid, 'panel': i,
                                  'characters': shot['characters'], 'depends_on': unique(deps),
                                  'source_asset_ids': [FACE[c] for c in shot['characters']],
                                  'brief': brief, 'source_shot': shot, 'output_contract': config['output'],
                                  'user_approved': False})
                continue
            require(bool(brief), 'missing single-frame description: ' + sid)
            tasks.append({'id': f'{project}_{sid}', 'kind': 'KEYFRAME_CANDIDATE',
                          'project_id': project, 'shot_id': sid, 'characters': shot['characters'],
                          'depends_on': unique(deps), 'source_asset_ids': [FACE[c] for c in shot['characters']],
                          'brief': brief, 'source_shot': shot, 'output_contract': config['output'],
                          'user_approved': False})
    validate_dag(tasks)
    for t in tasks:
        require(re.fullmatch('[A-Z0-9_]+', t['id']), 'unsafe task id')
        t['scope'] = 'CANDIDATE_CREATION_ONLY'
        t['attempt_limit'] = 3
        t['expected_output'] = f'outputs/{t["id"]}.png'
    return tasks


def prompt(task):
    return ('只制作一张完整的写实竖版照片；一个相机视角、一个连续场景。'
            '禁止海报、设定板、分镜表、拼贴、图片里的小图、色卡、标题、字幕、编号和任何文字。'
            '本请求不是项目介绍或文档排版。\n'
            '脸部参考只约束人物外观；服装/状态参考只约束衣服和伤手，不照搬其背景或姿势。'
            '所有人物为成年角色。保留古典人物气质和原参考脸，不现代网红化，不把猴脸改成人脸。\n'
            '本张画面：\n' + task['brief'] + '\n'
            '实景摄影、自然光与布料纹理，生活感而非宣传海报。只交付这张图，不加额外镜头。')


def build(root, output):
    root = Path(root).resolve()
    out = safe(root, output)
    require(not out.exists(), 'output already exists; do not overwrite prior work')
    config = read_json(root / CONFIG)
    planpaths = {p: f'episodes/{p}/production_plan_v5.json' for p in ('EP001', 'LOOKREEL01')}
    plans = {p: read_json(root / rel) for p, rel in planpaths.items()}
    registry = read_json(root / REGISTRY)
    tasks = compile_tasks(config, plans)
    aids = unique([*FACE.values(), 'DAIYU_COSTUME_CROP', 'WUKONG_COSTUME_CROP'])
    sources = []
    for aid in aids:
        a = registry['assets'][aid]
        src = safe(root, a['path'])
        require(src.is_file() and sha256_file(src) == a['sha256'], 'missing/changed source: ' + aid)
        sources.append(dict(a, asset_id=aid, source_repo_path=a['path'], path=f'inputs/{aid}{src.suffix.lower()}',
                            use='STYLE_DIRECTION_REFERENCE_NOT_NEW_APPROVAL'))
    for t in tasks:
        if t['id'] == 'WARD_W_FORMAL':
            t['source_asset_ids'].append('WUKONG_COSTUME_CROP')
        if t['id'] == 'WARD_D_OUTDOOR':
            t['source_asset_ids'].append('DAIYU_COSTUME_CROP')
    out.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='.image-packets-', dir=out.parent))
    try:
        for a in sources:
            dst = safe(temp, a['path'])
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(safe(root, a['source_repo_path']), dst)
        snapshots = {CONFIG: sha256_file(root / CONFIG), REGISTRY: sha256_file(root / REGISTRY),
                     **{rel: sha256_file(root / rel) for rel in planpaths.values()}}
        index = {'schema_version': 1, 'owner': 'REMOTE_IMAGE_PRODUCTION',
                 'source_files': snapshots, 'input_assets': sources,
                 'tasks': [], 'image_request_count': len(tasks), 'product_shot_count': 30,
                 'generated_images': 0, 'production_ready': False, 'user_approvals_written': 0,
                 'cpu_assembly': {'LOOKREEL01_COMP10': [f'LOOKREEL01_COMP10_P{i}' for i in range(1, 5)]}}
        for t in tasks:
            rel = f'tasks/{t["id"]}/task.json'
            dump(safe(temp, rel), t)
            (safe(temp, rel).parent / 'single_image_prompt.txt').write_text(prompt(t), encoding='utf-8')
            index['tasks'].append({'id': t['id'], 'path': rel, 'sha256': sha256_file(safe(temp, rel)),
                                   'depends_on': t['depends_on'], 'status': 'PENDING_RENDER'})
        dump(temp / 'INDEX.json', index)
        (temp / 'README.md').write_text(
            '# 独立出图任务包\n\n42个单图请求：9个服装/状态、20个剧情镜头、9个情侣镜头、四格镜头的4个单独画面。'
            '四格最终以CPU排版合成，不给图像模型整张项目板。\n\n这是已完成的请求与输入准备，不是42张成图。'
            '输入4张真实裁片仅继承已有方向，不写入用户批准。生成负责人仍为远端。'
            '输出每次只有一张，通过技术检查和远端视觉QA后才能成为下游候选参考；V5用户批准与视频Gate不变。\n', encoding='utf-8')
        os.replace(temp, out)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return index


def load_task(packet, tid):
    require(re.fullmatch('[A-Z0-9_]+', tid) is not None, 'unsafe task id')
    index = read_json(packet / 'INDEX.json')
    entries = [x for x in index['tasks'] if x['id'] == tid]
    require(len(entries) == 1, 'task not found')
    e = entries[0]
    path = safe(packet, e['path'])
    require(sha256_file(path) == e['sha256'], 'task bytes changed; rebuild from the plan')
    return index, read_json(path), e['sha256']


def checked_result(packet, tid, visiting=None):
    visiting = set() if visiting is None else set(visiting)
    require(tid not in visiting, 'result dependency cycle')
    visiting.add(tid)
    _, task, task_hash = load_task(packet, tid)
    record = read_json(safe(packet, f'results/{tid}.json'))
    require(record.get('task_sha256') == task_hash, 'stale result task')
    image = safe(packet, record['image']['path'])
    actual = image_check(image, task['output_contract'])
    require(actual['sha256'] == record['image']['sha256'], 'dependency image changed')
    qa = record['remote_art_qa']
    require(qa.get('image_sha256') == actual['sha256'] and all(qa.get(k) is True for k in SEMANTIC_KEYS), 'dependency QA failed')
    current = prepare_request(packet, tid, visiting)
    require(current['ready_to_request'], 'parent dependency is missing')
    require(sorted({x['sha256'] for x in current['reference_images']}) == record['input_hashes'], 'result input lineage changed')
    return record, image


def prepare_request(packet, tid, visiting=None):
    packet = Path(packet).resolve()
    index, t, h = load_task(packet, tid)
    require(tid not in t['depends_on'], 'self-dependency')
    refs, missing = [], []
    for aid in t['source_asset_ids']:
        found = [a for a in index['input_assets'] if a['asset_id'] == aid]
        require(len(found) == 1, 'unknown input ref')
        a = found[0]
        p = safe(packet, a['path'])
        require(p.is_file() and sha256_file(p) == a['sha256'], 'input reference changed')
        refs.append({'id': aid, 'path': str(p), 'sha256': a['sha256'], 'role': 'face' if 'FACE' in aid else 'costume'})
    for dep in t['depends_on']:
        if not safe(packet, f'results/{dep}.json').is_file():
            missing.append(dep)
            continue
        result, image = checked_result(packet, dep, visiting)
        refs.append({'id': dep, 'path': str(image), 'sha256': result['image']['sha256'], 'role': 'costume_or_continuity'})
    return {'id': tid, 'task_sha256': h, 'ready_to_request': not missing, 'missing_outputs': missing,
            'n': 1, 'width': t['output_contract']['width'], 'height': t['output_contract']['height'],
            'prompt': prompt(t) if not missing else None, 'reference_images': refs if not missing else [],
            'scope': 'CANDIDATE_ONLY', 'production_ready': False, 'network_requests_sent': 0}


def inspect_result(packet, tid, image_rel, qa_rel):
    packet = Path(packet).resolve()
    _, t, h = load_task(packet, tid)
    request = prepare_request(packet, tid)
    require(request['ready_to_request'], 'dependencies incomplete')
    image = safe(packet, image_rel)
    meta = image_check(image, t['output_contract'])
    qa = read_json(safe(packet, qa_rel))
    require(qa.get('task_id') == tid and qa.get('image_sha256') == meta['sha256'], 'QA is not bound to this result')
    require(bool(qa.get('reviewer')) and bool(qa.get('method')), 'missing remote review attribution')
    require(all(qa.get(k) is True for k in SEMANTIC_KEYS), 'remote visual QA not passed')
    source_hashes = {x['sha256'] for x in request['reference_images']}
    require(meta['sha256'] not in source_hashes, 'input copied as output')
    record = {'id': tid, 'task_sha256': h, 'image': dict(meta, path=image_rel),
              'input_hashes': sorted(source_hashes), 'remote_art_qa': qa,
              'status': 'REMOTE_QA_CANDIDATE', 'user_approved': False, 'production_ready': False}
    dest = safe(packet, f'results/{tid}.json')
    require(not dest.exists(), 'result already registered; create an explicit new version')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('x', encoding='utf-8') as out:
        json.dump(record, out, ensure_ascii=False, indent=2)
        out.write('\n')
    return record


def assemble_comp10(packet):
    packet = Path(packet).resolve()
    index = read_json(packet / 'INDEX.json')
    ids = index['cpu_assembly']['LOOKREEL01_COMP10']
    require(len(ids) == 4 and len(set(ids)) == 4, 'expected four distinct panel tasks')
    panels = [checked_result(packet, tid) for tid in ids]
    require(len({r['image']['sha256'] for r, _ in panels}) == 4, 'four-grid cannot duplicate one picture')
    output = safe(packet, 'outputs/LOOKREEL01_COMP10.png')
    require(not output.exists(), 'composite exists; do not overwrite')
    canvas = Image.new('RGB', (1080, 1920), 'white')
    for i, (_, path) in enumerate(panels):
        with Image.open(path) as im:
            panel = ImageOps.contain(im.convert('RGB'), (540, 960), Image.Resampling.LANCZOS)
        x = (i % 2) * 540 + (540 - panel.width) // 2
        y = (i // 2) * 960 + (960 - panel.height) // 2
        canvas.paste(panel, (x, y))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        canvas.save(stream, format='PNG')
    record = {'id': 'LOOKREEL01_COMP10', 'kind': 'CPU_FOUR_GRID_CANDIDATE',
              'path': output.relative_to(packet).as_posix(), 'sha256': sha256_file(output),
              'panel_ids': ids, 'panel_hashes': [r['image']['sha256'] for r, _ in panels],
              'user_approved': False, 'production_ready': False, 'i2v_eligible': False}
    dump(packet / 'composites/LOOKREEL01_COMP10.json', record)
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build')
    b.add_argument('--root', default='.')
    b.add_argument('--out', required=True)
    r = sub.add_parser('request')
    r.add_argument('--packet', required=True)
    r.add_argument('--task', required=True)
    i = sub.add_parser('inspect')
    i.add_argument('--packet', required=True)
    i.add_argument('--task', required=True)
    i.add_argument('--image', required=True)
    i.add_argument('--qa', required=True)
    c = sub.add_parser('assemble-comp10')
    c.add_argument('--packet', required=True)
    a = p.parse_args()
    try:
        if a.cmd == 'build':
            result = build(a.root, a.out)
            result = {k: result[k] for k in ('image_request_count', 'product_shot_count', 'generated_images', 'production_ready', 'user_approvals_written')}
        elif a.cmd == 'request':
            result = prepare_request(a.packet, a.task)
        elif a.cmd == 'inspect':
            result = inspect_result(a.packet, a.task, a.image, a.qa)
        else:
            result = assemble_comp10(a.packet)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('ready_to_request', True) else 3
    except (ContractError, OSError, ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e), 'production_ready': False}, ensure_ascii=False))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
