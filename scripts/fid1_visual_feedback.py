"""Build an offline, unapproved feedback page for one completed FID1 source job."""
from __future__ import annotations

import base64
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

try:
    from .fid1_deploy import is_junction
    from .fid1_qa_report import PROJECT, SCOPE, pending_visual_review, sha256_file, validate_fid1_job_contract, verified_run_output
    from .preproduction import read_json, require, write_json
    from .sync_repo_media import safe
except ImportError:
    from fid1_deploy import is_junction
    from fid1_qa_report import PROJECT, SCOPE, pending_visual_review, sha256_file, validate_fid1_job_contract, verified_run_output
    from preproduction import read_json, require, write_json
    from sync_repo_media import safe


SESSIONS = f"local/production/{PROJECT}/review_sessions"
KIT = f"episodes/{PROJECT}/source_kit.json"


def _path(root, relative):
    path = safe(root, relative)
    current = root
    for part in relative.split("/"):
        current /= part
        require(not is_junction(current), "review path contains a junction/reparse point")
    return path


def _data_url(raw, mime):
    return "data:" + mime + ";base64," + base64.b64encode(raw).decode("ascii")


def render_feedback_page(metadata, source_url, video_url, sheets, references):
    """No user decision is selected or persisted by this presentation function."""
    fixed = json.dumps(metadata, ensure_ascii=False).replace("<", "\\u003c").replace("&", "\\u0026")
    detail_html = "".join(
        '<figure><img src="' + url + '" alt="' + html.escape(label, quote=True) + '"><figcaption>'
        + html.escape(label) + '</figcaption></figure>' for label, url in references
    )
    criteria = (("full_playback", "完整播放与动作"), ("identity", "人物身份与脸部"),
                ("costume", "服装与饰品"), ("limbs", "手、牵手关系与四肢"))
    choices = "".join(
        f'<label>{label}<select id="{key}"><option value="">请选择</option>'
        '<option value="PASS">接受</option><option value="CHANGES_REQUIRED">需要修改</option>'
        '<option value="NOT_RUN">尚未审核</option></select></label>' for key, label in criteria
    )
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(metadata['shot_id'])} 视频审片</title>
<style>body{{font:16px system-ui;color:#e9edf5;background:#111827;max-width:1250px;margin:auto;padding:24px}}h1,h2{{margin-top:0}}section{{margin:24px 0;padding:20px;background:#1f2937;border-radius:14px}}.compare,.refs,.fields{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}}img,video{{display:block;max-width:100%;max-height:70vh;margin:auto}}figure{{margin:0}}figcaption{{padding:8px;text-align:center}}.refs{{grid-template-columns:repeat(4,minmax(0,1fr))}}.refs img{{max-height:240px}}label{{display:flex;flex-direction:column;gap:8px}}input,select,textarea,button{{font:inherit;padding:10px;border:1px solid #64748b;border-radius:7px;background:#0f172a;color:white}}textarea{{min-height:100px;width:100%;box-sizing:border-box}}button{{cursor:pointer;background:#2563eb}}code{{overflow-wrap:anywhere}}#feedback-status{{white-space:pre-wrap}}@media(max-width:760px){{.compare,.fields{{grid-template-columns:1fr}}.refs{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}</style></head><body>
<h1>{html.escape(metadata['shot_id'])} / {html.escape(metadata['profile_id'])} 视频审片</h1>
<p>同源保真小样。请完整播放，并与原图逐项比较。当前没有记录任何视觉批准。</p>
<section><div class="compare"><figure><img src="{source_url}" alt="批准原图"><figcaption>批准原图</figcaption></figure><figure><video id="trial-video" controls preload="metadata" src="{video_url}"></video><figcaption>实际输出 · 49帧 / 24fps</figcaption><button id="play-video" type="button">从头播放整段视频</button><p id="playback-status">尚未播放到结尾；播放状态不会代替你的审片判断。</p></figure></div></section>
<section><h2>人物与服装参考</h2><div class="refs">{detail_html}</div></section>
<section><h2>首帧 / 中间帧 / 末帧</h2><img src="{sheets['first_middle_last']}" alt="首中尾实际帧"></section>
<section><details><summary>展开全部49帧</summary><img src="{sheets['all49']}" alt="全部49帧"></details></section>
<section><h2>你的审片意见</h2><div class="fields">{choices}
<label>本次结论<select id="decision"><option value="">请选择</option><option value="ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL">接受此视频，用于下一张源图试拍</option><option value="CHANGES_REQUIRED">需要修改，暂不进入下一张</option></select></label>
<label>审核人<input id="reviewer" placeholder="请填写 Jovi" autocomplete="off"></label></div>
<p><label>具体意见<textarea id="user_quote" maxlength="2048" placeholder="请写下你实际看完后的判断；需要修改时说明人物、服装、手脚或动作的问题。"></textarea></label></p>
<button id="export-feedback" type="button">导出我的审片反馈</button><p id="feedback-status" role="status">所有选择均未填写；页面不会自动批准。</p>
<p>请保存导出的 JSON，交回本地执行方预览校验。导出不会自动写入项目批准记录。</p></section>
<section><details><summary>视频绑定信息</summary><p>输出 SHA256：<code>{metadata['output_sha256']}</code></p><p>范围：T1_SOURCE_ONLY</p></details></section>
<script id="fixed-review-metadata" type="application/json">{fixed}</script>
<script>
const fixed = JSON.parse(document.getElementById('fixed-review-metadata').textContent);
const keys = ['full_playback','identity','costume','limbs'];
function collectFeedback() {{
  const result = {{...fixed}};
  for (const key of [...keys,'decision','reviewer','user_quote']) result[key] = document.getElementById(key).value;
  if (!keys.every(key => ['PASS','CHANGES_REQUIRED','NOT_RUN'].includes(result[key]))) throw new Error('请逐项填写审片结果。');
  if (!['ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL','CHANGES_REQUIRED'].includes(result.decision)) throw new Error('请选择本次结论。');
  if (result.reviewer !== 'Jovi' || !result.user_quote.trim()) throw new Error('请填写审核人 Jovi 和你的具体审片意见。');
  if (result.decision === 'ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL' && !keys.every(key => result[key] === 'PASS')) throw new Error('接受下一张试拍需要四项均接受，包括完整播放。');
  if (result.decision === 'CHANGES_REQUIRED' && keys.every(key => result[key] === 'PASS')) throw new Error('需要修改的结论应有至少一项未接受。');
  result.recorded_at = new Date().toISOString();
  return result;
}}
document.getElementById('export-feedback').addEventListener('click', () => {{
  const status = document.getElementById('feedback-status');
  try {{
    const result = collectFeedback();
    const url = URL.createObjectURL(new Blob([JSON.stringify(result,null,2)+'\\n'], {{type:'application/json'}}));
    const link = document.createElement('a'); link.href = url;
    link.download = 'FID1_'+fixed.shot_id+'_'+fixed.profile_id+'_'+fixed.output_sha256.slice(0,12)+'_FEEDBACK.json';
    link.click(); setTimeout(() => URL.revokeObjectURL(url),1000);
    status.textContent = '已导出你填写的反馈。项目批准记录尚未修改。';
  }} catch (error) {{ status.textContent = error.message; }}
}});
const video = document.getElementById('trial-video');
document.getElementById('play-video').addEventListener('click', () => {{ video.currentTime=0; video.play().catch(() => {{ document.getElementById('playback-status').textContent='请使用视频控件播放。'; }}); }});
video.addEventListener('ended', () => {{ document.getElementById('playback-status').textContent='视频已播放到结尾。请自行填写身份、服装、手脚和动作的判断。'; }});
</script></body></html>'''


def build_review_page(root, job_dir, out):
    root = Path(root).resolve(strict=True)
    job_rel = Path(job_dir).as_posix()
    if Path(job_dir).is_absolute():
        job_rel = Path(job_dir).relative_to(root).as_posix()
    match = re.fullmatch(f"local/production/{PROJECT}/video/(SH90[123])/jobs/(take[0-9]{{2,}})", job_rel)
    require(match is not None, "feedback job must name one canonical source-pilot take")
    directory = _path(root, job_rel)
    hashes = {}

    def bound(relative, expected=None):
        path = _path(root, relative)
        require(path.is_file(), "missing feedback material: " + relative)
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        require(expected is None or digest == expected, "feedback material hash changed: " + relative)
        hashes[relative] = digest
        return raw

    job = json.loads(bound(job_rel + '/job.json'))
    require(job.get('project_id') == PROJECT and job.get('purpose') == SCOPE
            and job.get('eligible_for_final_cut') is False and job.get('shot_id') == match[1],
            "feedback job must be the specified source-only shot")
    validate_fid1_job_contract(job)
    integrity = json.loads(bound(job_rel + '/job_integrity.json'))
    require(set(integrity) == {'schema_version', 'job_sha256', 'workflow_sha256', 'input_sha256'}
            and integrity.get('schema_version') == 1 and integrity.get('job_sha256') == hashes[job_rel+'/job.json']
            and integrity.get('workflow_sha256') == job.get('workflow_sha256')
            and integrity.get('input_sha256') == job.get('input_sha256'), "historic job integrity changed")
    bound(job_rel + '/workflow.json', job['workflow_sha256'])
    run = json.loads(bound(job_rel + '/run_record.json'))
    report = json.loads(bound(job_rel + '/qa/qa_report.json'))
    output, record = verified_run_output(root, directory, run)
    require(run.get('prompt_id') and run.get('queued_new_job') is True
            and run.get('workflow_sha256') == job['workflow_sha256']
            and report.get('scope') == SCOPE and report.get('shot_id') == job['shot_id']
            and report.get('profile_id') == job['trial_profile']['profile_id']
            and report.get('workflow_sha256') == job['workflow_sha256'] and report.get('seed') == job['seed']
            and report.get('runtime_success') is True and report.get('media_contract_ok') is True
            and report.get('full_decode') == 'PASS', "feedback QA is not bound to the completed job")
    require(report.get('visual_review') == pending_visual_review(),
            "this job already has human feedback; do not create a competing approval")
    profile = job['trial_profile']
    media = report.get('media', {})
    require(profile.get('frames') == 49 and profile.get('fps') == 24
            and media.get('frame_count') == 49 and media.get('fps') == 24
            and (media.get('width'), media.get('height')) == (profile.get('width'), profile.get('height'))
            and report.get('frames', {}).get('count') == 49, "feedback media contract differs from the frozen profile")
    require(report.get('output', {}) == {'path': output.relative_to(directory).as_posix(),
                                         'sha256': record['sha256'], 'bytes': record['bytes']},
            "feedback QA output is stale")
    require(report.get('input') == {'path': job['input_file'], 'sha256': job['input_sha256']},
            "feedback QA input is stale")
    source_raw = bound(job_rel + '/' + job['input_file'], job['input_sha256'])
    video_raw = bound(output.relative_to(root).as_posix(), record['sha256'])
    sheets = {name: _data_url(bound(job_rel+'/'+rel), 'image/png')
              for name, rel in [('first_middle_last', report['frames']['first_middle_last']),
                                ('all49', report['frames']['all49_contact_sheet'])]}

    # References come from this completed job's frozen source-review registry.
    sources = job.get('sources', {})
    require(KIT in sources, "job has no frozen source kit")
    kit = json.loads(bound(KIT, sources[KIT]))
    registries = [p for p in sources if re.fullmatch(f"local/production/{PROJECT}/reviews/[a-f0-9]{{64}}/registry.json", p)]
    require(len(registries) == 1, "job must name one frozen reference registry")
    registry = json.loads(bound(registries[0], sources[registries[0]]))['assets']
    bindings = kit['shots'][job['shot_id']]['bindings']
    references = []
    for character, label in [('WUKONG', '悟空'), ('DAIYU', '黛玉')]:
        ids = [(aid, label+'人脸参考') for aid in bindings['identity_refs'][character]]
        ids.append((bindings['costume_refs'][character]['asset_id'], label+'服装细节'))
        for aid, caption in ids:
            asset = registry[aid]
            references.append((caption, _data_url(bound(asset['path'], asset['sha256']), 'image/png')))

    metadata = {'schema_version': 1, 'scope': SCOPE, 'shot_id': job['shot_id'],
                'profile_id': job['trial_profile']['profile_id'], 'output_sha256': record['sha256']}
    page = render_feedback_page(metadata, _data_url(source_raw, 'image/png'),
                                _data_url(video_raw, 'video/mp4'), sheets, references)
    destination_rel = Path(out).as_posix()
    require(destination_rel.startswith(SESSIONS+'/'), "feedback page must be under source-pilot review_sessions")
    destination = _path(root, destination_rel)
    require(not destination.exists(), "feedback session already exists; choose a new directory")
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.visual-feedback-', dir=destination.parent))
    try:
        (stage/'review.html').write_text(page, encoding='utf-8')
        receipt = {'schema_version': 1, 'scope': SCOPE, 'job_dir': job_rel,
                   'feedback_binding': metadata, 'sources': hashes,
                   'page_sha256': sha256_file(stage/'review.html'),
                   'default_approvals': 0, 'approval_records_changed': 0}
        write_json(stage/'page_receipt.json', receipt)
        for relative, expected in hashes.items():
            require(sha256_file(_path(root, relative)) == expected, "feedback material changed during page generation")
        require(not destination.exists(), "concurrent feedback session writer")
        os.rename(stage, destination)
        stage = None
        return {'review_page': str(destination/'review.html'), 'receipt': str(destination/'page_receipt.json'),
                'scope': SCOPE, 'default_approvals': 0, 'approval_records_changed': 0}
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)
