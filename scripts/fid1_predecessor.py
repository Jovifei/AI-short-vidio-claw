"""Explicit, immutable admission receipt for SH903 -> SH901 -> SH902 source trials."""
from pathlib import Path
import re

try:
    from .preproduction import FID1_NODE_CLASS_BY_STRATEGY, read_json, require
    from .sync_repo_media import safe, digest
    from .fid1_deploy import is_junction
    from .fid1_qa_report import verified_run_output
    from .fid1_review_contract import validate_visual_review_payload, VISUAL_CRITERIA
    from .fid1_job_paths import canonical_job_directory, safe_project_path
except ImportError:
    from preproduction import FID1_NODE_CLASS_BY_STRATEGY, read_json, require
    from sync_repo_media import safe, digest
    from fid1_deploy import is_junction
    from fid1_qa_report import verified_run_output
    from fid1_review_contract import validate_visual_review_payload, VISUAL_CRITERIA
    from fid1_job_paths import canonical_job_directory, safe_project_path


PROJECT = 'T1_SOURCE_PILOT'
SCOPE = 'T1_SOURCE_ONLY'
LOCAL = 'local/production/' + PROJECT
PREVIOUS_SHOT = {'SH901': 'SH903', 'SH902': 'SH901'}


def _path(root, relative):
    return safe_project_path(root, relative)


def _recorded_path(root, directory, value):
    require(isinstance(value, str) and value, 'previous runtime file path is missing')
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = directory / candidate
    require(candidate.is_relative_to(root), 'previous runtime file is outside project')
    return _path(root, candidate.relative_to(root).as_posix())


def _recorded_job_file(root, directory, value, expected):
    recorded = _recorded_path(root, directory, value)
    require(recorded == expected, 'previous runtime workflow/image path differs from the frozen job')


def validate_predecessor(root, shot_id, previous_job):
    """Validate completed predecessor bytes, never its historical implementation versions."""
    root = Path(root).resolve(strict=True)
    require(shot_id in {'SH901', 'SH902', 'SH903'}, 'unknown FID1 source shot')
    previous_shot = PREVIOUS_SHOT.get(shot_id)
    if previous_shot is None:
        require(previous_job is None, 'SH903 must not select a previous job')
        return None
    expected_prefix = f'{LOCAL}/video/{previous_shot}/jobs/'
    require(isinstance(previous_job, str)
            and re.fullmatch(re.escape(expected_prefix) + r'take[0-9]{2,}', previous_job),
            f'{shot_id} requires an explicit {previous_shot} takeNN previous job')
    directory = canonical_job_directory(root, previous_job, previous_shot)
    require(directory.is_dir(), 'previous FID1 job does not exist')
    def require_review_complete():
        for marker in ('.fid1-review.lock','.fid1-review-recovery.json'):
            path=_path(root,previous_job+'/qa/'+marker)
            require(not path.exists(), 'previous review transaction is active or RECOVERY_REQUIRED')
    require_review_complete()
    # safe() rejects links, junctions and traversal; keep the receipt paths canonical.
    files = {name: _path(root, previous_job + '/' + name) for name in (
        'job.json', 'job_integrity.json', 'workflow.json', 'run_record.json', 'qa/qa_report.json')}
    require(all(path.is_file() for path in files.values()),
            f'{previous_shot} prepared job, integrity, workflow, run and QA are required')
    hashes = {path.relative_to(root).as_posix(): digest(path) for path in files.values()}
    job = read_json(files['job.json'])
    integrity = read_json(files['job_integrity.json'])
    report = read_json(files['qa/qa_report.json'])
    run = read_json(files['run_record.json'])
    require(job.get('project_id') == PROJECT and job.get('shot_id') == previous_shot
            and job.get('purpose') == SCOPE and job.get('eligible_for_final_cut') is False,
            'previous job is not the expected isolated source-only shot')
    require(isinstance(integrity, dict)
            and set(integrity) == {'schema_version', 'job_sha256', 'workflow_sha256', 'input_sha256'}
            and type(integrity.get('schema_version')) is int and integrity['schema_version'] == 1,
            'previous job integrity receipt is invalid')
    require(integrity.get('job_sha256') == hashes[previous_job + '/job.json']
            and integrity.get('workflow_sha256') == job.get('workflow_sha256')
            == hashes[previous_job + '/workflow.json']
            and integrity.get('input_sha256') == job.get('input_sha256'),
            'previous job/workflow integrity hash changed')
    input_name = job.get('input_file')
    require(isinstance(input_name, str) and re.fullmatch(r'[^/\\]+\.png', input_name),
            'previous prepared input must be a direct PNG in its job')
    input_rel = previous_job + '/' + input_name
    input_path = _path(root, input_rel)
    require(input_path.is_file(), 'previous prepared input is missing')
    hashes[input_rel] = digest(input_path)
    require(hashes[input_rel] == job.get('input_sha256'), 'previous prepared input hash changed')
    profile = job.get('trial_profile') or {}
    profile_id = profile.get('profile_id')
    require(isinstance(profile_id, str) and re.fullmatch(r'[A-Z0-9_]{1,64}', profile_id)
            and profile.get('scope') == SCOPE and profile.get('shot_id') == previous_shot
            and profile.get('input_sha256') == job.get('input_sha256')
            and profile.get('seed') == job.get('seed'), 'previous frozen profile/input/seed binding changed')
    require(all(type(profile.get(key)) is int for key in ('width', 'height', 'frames', 'fps'))
            and (profile['width'], profile['height']) in {(480, 832), (576, 1024)}
            and (profile['frames'], profile['fps']) == (49, 24),
            'previous frozen profile is outside the source-only size/frame/fps budget')
    contract = job.get('fid1_contract') or {}
    strategy = profile.get('anchor_strategy')
    require(isinstance(strategy, str) and strategy in FID1_NODE_CLASS_BY_STRATEGY
            and type(contract.get('schema_version')) is int and contract['schema_version'] in (1, 2)
            and contract.get('strategy') == strategy
            and contract.get('node_class') == FID1_NODE_CLASS_BY_STRATEGY[strategy],
            'previous FID1 strategy/node contract differs from its frozen profile')
    require(report.get('scope') == SCOPE and report.get('shot_id') == previous_shot
            and report.get('profile_id') == profile_id and report.get('runtime_success') is True
            and report.get('media_contract_ok') is True and report.get('full_decode') == 'PASS',
            'previous runtime/media QA is not complete or belongs to another job')
    media = report.get('media') or {}
    require((media.get('width'), media.get('height'), media.get('frame_count'), media.get('fps'))
            == (profile['width'], profile['height'], 49, 24)
            and all(type(media.get(key)) is int for key in ('width', 'height', 'frame_count', 'fps')),
            'previous QA media dimensions/frames/fps differ from its frozen source profile')
    require(report.get('input', {}).get('path') == input_name
            and report.get('input', {}).get('sha256') == job.get('input_sha256')
            and report.get('workflow_sha256') == run.get('workflow_sha256') == job.get('workflow_sha256')
            and report.get('seed') == job.get('seed'), 'previous QA/input/workflow/run binding changed')
    _recorded_job_file(root, directory, run.get('workflow'), files['workflow.json'])
    _recorded_job_file(root, directory, (run.get('args') or {}).get('image'), input_path)
    require(run.get('result') == 'success' and run.get('queued_new_job') is True
            and isinstance(run.get('prompt_id'), str) and run['prompt_id'],
            'previous ComfyUI runtime did not succeed')
    outputs = run.get('outputs')
    require(isinstance(outputs, list) and len(outputs) == 1 and isinstance(outputs[0], dict),
            'previous runtime must contain one output')
    guarded_output = _recorded_path(root, directory, outputs[0].get('saved_path'))
    require(guarded_output.parent == _path(root, previous_job + '/run_record_media'),
            'previous runtime output is outside its media directory')
    output_path, output_record = verified_run_output(root, directory, run)
    output_rel = output_path.relative_to(root).as_posix()
    require(report.get('output', {}).get('path') == output_path.relative_to(directory).as_posix()
            and report.get('output', {}).get('sha256') == output_record.get('sha256')
            and report.get('output', {}).get('bytes') == output_record.get('bytes'),
            'previous QA does not match the current ComfyUI output')
    hashes[output_rel] = output_record['sha256']
    review = report.get('visual_review') or {}
    evidence_rel = review.get('evidence_path')
    evidence_sha = review.get('evidence_sha256')
    require(isinstance(evidence_rel, str)
            and re.fullmatch(r'local/review_evidence/FID1_[A-Za-z0-9_]+\.json', evidence_rel),
            'previous Jovi visual review evidence is missing or outside its directory')
    evidence_file = _path(root, evidence_rel)
    require(evidence_file.is_file() and digest(evidence_file) == evidence_sha,
            'previous Jovi visual review evidence hash changed')
    evidence = read_json(evidence_file)
    validate_visual_review_payload(evidence, scope=SCOPE, shot_id=previous_shot,
                                   profile_id=profile_id, output_sha256=output_record['sha256'])
    require(evidence['decision'] == 'ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL',
            f'{previous_shot} requires Jovi visual acceptance before {shot_id}')
    require(all(review.get(key) == evidence[key] for key in (
        'decision', 'reviewer', 'user_quote', 'recorded_at', *VISUAL_CRITERIA)),
        'previous QA visual review differs from the actual evidence')
    hashes[evidence_rel] = evidence_sha
    # Catch changes between initial parsing and receipt publication, including self-consistent reseals.
    require(all(digest(_path(root, rel)) == sha for rel, sha in hashes.items()),
            'previous FID1 files changed during validation')
    require_review_complete()
    return {'schema_version': 1, 'shot_id': previous_shot, 'job_dir': previous_job,
            'profile_id': profile_id, 'prompt_id': run['prompt_id'],
            'output_sha256': output_record['sha256'], 'files': hashes}


def validate_predecessor_receipt(root, shot_id, receipt):
    if shot_id == 'SH903':
        require(receipt is None, 'SH903 predecessor receipt must be null')
        return validate_predecessor(root, shot_id, None)
    require(isinstance(receipt, dict) and set(receipt) == {
        'schema_version', 'shot_id', 'job_dir', 'profile_id', 'prompt_id', 'output_sha256', 'files'}
        and type(receipt.get('schema_version')) is int and receipt['schema_version'] == 1,
        'frozen FID1 predecessor receipt is missing or unsupported')
    actual = validate_predecessor(root, shot_id, receipt.get('job_dir'))
    require(actual == receipt, 'frozen FID1 predecessor receipt changed; prepare a new take')
    return actual
