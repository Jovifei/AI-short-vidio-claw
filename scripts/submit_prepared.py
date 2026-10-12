#!/usr/bin/env python3
"""Default dry-run; execute only one immutable prepared job through the existing probe."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from preproduction import checked_asset, read_json, relative_file, require, sha256_file, validate_graph, write_json


def validate_fid1_job(root, directory, job, graph):
    try:
        import source_pilot
    except ImportError:
        from scripts import source_pilot

    contract = job.get('fid1_contract')
    require(isinstance(contract, dict) and contract.get('schema_version') == 1,
            'FID1 job contract is missing or unsupported')
    integrity_path = directory / 'job_integrity.json'
    require(integrity_path.is_file(), 'FID1 immutable job-integrity receipt is missing')
    integrity = read_json(integrity_path)
    require(set(integrity) == {'schema_version', 'job_sha256', 'workflow_sha256', 'input_sha256'}
            and integrity.get('schema_version') == 1,
            'FID1 job-integrity receipt is invalid')
    require(integrity.get('job_sha256') == sha256_file(directory / 'job.json')
            and integrity.get('workflow_sha256') == job.get('workflow_sha256')
            and integrity.get('input_sha256') == job.get('input_sha256'),
            'FID1 job, workflow, or input integrity hash changed')
    require(job.get('project_id') == source_pilot.PROJECT and job.get('purpose') == source_pilot.SCOPE
            and job.get('eligible_for_final_cut') is False,
            'FID1 jobs must remain isolated source-only trials')
    expected_node_class = source_pilot.FID1_NODE_CLASS_BY_STRATEGY.get(contract.get('strategy'))
    require(expected_node_class is not None and contract.get('node_class') == expected_node_class
            and contract.get('noise_mask_semantics') == '1=denoise;0=preserve',
            'FID1 execution contract changed')

    kit, plan, _, _ = source_pilot.inputs(root)
    pointer = read_json(source_pilot.safe(root, source_pilot.POINTER))
    require(pointer.get('scope') == source_pilot.SCOPE
            and pointer.get('snapshot', '').startswith(source_pilot.LOCAL + '/reviews/'),
            'missing source-pilot approval snapshot')
    snapshot = source_pilot.safe(root, pointer['snapshot'])
    require(set(pointer.get('files', {})) == {'registry.json', 'approval.json', 'feedback.json'},
            'invalid source-pilot snapshot manifest')
    for name, expected in pointer['files'].items():
        require(source_pilot.digest(snapshot / name) == expected, 'source-pilot snapshot hash changed: ' + name)
    registry = read_json(snapshot / 'registry.json')
    approval = read_json(snapshot / 'approval.json')
    feedback = read_json(snapshot / 'feedback.json')
    source_pilot.choices(root, feedback)
    shot_id = job.get('shot_id')
    require(shot_id in kit['shots'], 'unknown FID1 shot')
    shot, entry, image = source_pilot.validate_keyframe(root, plan, approval, registry, shot_id)
    profile_path = job.get('trial_profile_path')
    require(isinstance(profile_path, str) and profile_path.startswith('config/source_fidelity_trials/'),
            'FID1 trial profile path is missing or outside the trial config')
    profile, profile_hash = source_pilot.load_trial_profile(root, shot_id, kit, profile_path)
    require(profile.get('anchor_strategy') in source_pilot.FID1_NODE_CLASS_BY_STRATEGY,
            'FID1 profile has no supported anchor')
    require(job.get('trial_profile') == profile, 'prepared FID1 profile differs from its current file')
    require(job.get('seed') == profile.get('seed'), 'FID1 seed differs from the shot-specific frozen profile')
    require(job.get('sources', {}).get(profile_path) == profile_hash
            and contract.get('profile_sha256') == profile_hash,
            'FID1 profile hash changed')
    require(job.get('input_sha256') == profile['input_sha256'] == entry['sha256'],
            'FID1 profile, approval, and prepared input hashes differ')
    require(job.get('characters') == shot['characters'], 'FID1 character bindings changed')
    require(source_pilot.digest(directory / job['input_file']) == entry['sha256'], 'prepared FID1 image differs from approved source')

    dependency_files, dependency_hash = source_pilot.fid1_dependency_hash(root)
    require(contract.get('dependency_files') == dependency_files
            and contract.get('dependency_sha256') == dependency_hash,
            'FID1 implementation dependency hash changed')
    require(contract.get('node_source_sha256') == dependency_files['scripts/fid1_wan_latent_anchor_node.py'],
            'FID1 Comfy node source hash changed')
    require(all(job.get('sources', {}).get(rel) == digest for rel, digest in dependency_files.items()),
            'FID1 job source hashes do not match the implementation dependencies')

    ids = validate_graph(graph, job['characters'], fid1_profile=profile)
    load_name = graph[ids['load']]['inputs'].get('image')
    require(load_name == job['input_file'], 'Comfy LoadImage does not read the prepared approved source')
    sampler = graph[ids['sampler']]['inputs']
    require(sampler.get('seed') == job.get('seed'), 'FID1 sampler seed differs from the frozen job')
    require((sampler.get('steps'), sampler.get('cfg'), sampler.get('denoise'), sampler.get('sampler_name'), sampler.get('scheduler'))
            == (20, 5, 1, 'uni_pc', 'simple'), 'FID1 sampler settings changed')
    return True


def validate_fid1_object_info(payload, node_class='FID1WanSourceROIAnchor'):
    require(isinstance(payload, dict), 'ComfyUI object_info response is not an object')
    require(node_class in {'FID1WanSourceROIAnchor', 'FID1WanTimestepAwareROIAnchor'},
            'unsupported FID1 ComfyUI node class')
    info = payload.get(node_class)
    require(isinstance(info, dict), node_class + ' is not loaded in the running ComfyUI')
    required = (info.get('input') or {}).get('required')
    if node_class == 'FID1WanSourceROIAnchor':
        valid_inputs = (
            isinstance(required, dict)
            and set(required) == {'latent', 'roi_boxes_json'}
            and (required.get('latent') or [None])[0] == 'LATENT'
            and (required.get('roi_boxes_json') or [None])[0] == 'STRING'
        )
        expected_outputs = ['LATENT']
    else:
        valid_inputs = (
            isinstance(required, dict)
            and set(required) == {'model', 'latent', 'roi_boxes_json'}
            and (required.get('model') or [None])[0] == 'MODEL'
            and (required.get('latent') or [None])[0] == 'LATENT'
            and (required.get('roi_boxes_json') or [None])[0] == 'STRING'
        )
        expected_outputs = ['MODEL', 'LATENT']
    require(valid_inputs, 'loaded FID1 node sockets do not match the prepared graph')
    require(info.get('output') == expected_outputs, 'loaded FID1 node output does not match the prepared graph')
    return True


def validate_fid1_queue(payload):
    require(isinstance(payload, dict), 'ComfyUI queue response is not an object')
    running = payload.get('queue_running')
    pending = payload.get('queue_pending')
    require(isinstance(running, list) and isinstance(pending, list), 'ComfyUI queue response has an invalid shape')
    require(not running and not pending, 'ComfyUI queue is not empty; refusing a second GPU job')
    return {'running': len(running), 'pending': len(pending)}


def validate_fid1_runtime(root, comfy_root, job, url):
    parsed = urlparse(url)
    require(parsed.scheme == 'http' and parsed.hostname in {'127.0.0.1', 'localhost', '::1'}
            and not parsed.username and not parsed.password and parsed.path in {'', '/'}
            and not parsed.query and not parsed.fragment,
            'FID1 runtime checks are restricted to a local ComfyUI endpoint')
    contract = job.get('fid1_contract') or {}
    node_class = contract.get('node_class')
    require(node_class in {'FID1WanSourceROIAnchor', 'FID1WanTimestepAwareROIAnchor'},
            'FID1 job node class is missing or unsupported')
    try:
        from .fid1_deploy import verify_installed
    except ImportError:
        from fid1_deploy import verify_installed
    verify_installed(root, comfy_root, contract.get('node_source_sha256'))
    queue_request = Request(url.rstrip('/') + '/queue', headers={'Accept': 'application/json'})
    try:
        with urlopen(queue_request, timeout=15) as response:
            require(response.status == 200, 'ComfyUI queue request failed')
            queue = json.loads(response.read(1024 * 1024).decode('utf-8'))
    except Exception as exc:
        raise ValueError(f'cannot verify that the ComfyUI queue is empty: {exc}') from exc
    queue_state = validate_fid1_queue(queue)
    request = Request(url.rstrip('/') + '/object_info/' + node_class, headers={'Accept': 'application/json'})
    try:
        with urlopen(request, timeout=15) as response:
            require(response.status == 200, 'ComfyUI FID1 object_info request failed')
            payload = json.loads(response.read(1024 * 1024).decode('utf-8'))
    except Exception as exc:
        raise ValueError(f'cannot verify the loaded FID1 ComfyUI node: {exc}') from exc
    validate_fid1_object_info(payload, node_class)
    return {'installed_node_sha256': contract['node_source_sha256'], 'loaded_node_class': node_class,
            'queue': queue_state}


def job_command(root, directory, url):
    parsed = urlparse(url)
    require(parsed.scheme == 'http' and parsed.hostname in {'127.0.0.1', 'localhost', '::1'}
            and not parsed.username and not parsed.password and parsed.path in {'', '/'}
            and not parsed.query and not parsed.fragment, 'only local ComfyUI endpoints are allowed')
    root, directory = Path(root).resolve(), Path(directory).resolve()
    require(directory.is_relative_to(root / 'local' / 'production'), 'job outside production tree')
    job = read_json(directory / 'job.json')
    require(job.get('status') == 'PREPARED_NOT_SUBMITTED', 'invalid job state')
    for rel, digest in job['sources'].items():
        checked_asset(root, rel, digest)
    checked_asset(directory, job['input_file'], job['input_sha256'])
    checked_asset(directory, 'workflow.json', job['workflow_sha256'])
    graph = read_json(directory / 'workflow.json')
    has_fid1_node = any(node.get('class_type') in {'FID1WanSourceROIAnchor', 'FID1WanTimestepAwareROIAnchor'} for node in graph.values())
    if job.get('fid1_contract') is not None:
        validate_fid1_job(root, directory, job, graph)
    else:
        require(not has_fid1_node, 'FID1 graph node has no frozen source-trial contract')
        if job.get('purpose') == 'T1_SOURCE_ONLY':
            require(isinstance(job.get('characters'), list), 'source-trial character bindings are missing')
            validate_graph(graph, job['characters'])
    require(not (directory / 'submission_intent.json').exists(), 'job already attempted; reconcile history, do not resubmit')
    require(not (directory / 'run_record.json').exists(), 'run record already exists')
    probe = root / 'scripts' / 'p1_comfy_probe.py'
    require(probe.is_file(), 'existing p1_comfy_probe.py missing; pull the project, not only this patch')
    # The probe uploads this immutable input and injects the returned local input name.
    command = [sys.executable, str(probe), '--url', url.rstrip('/'),
               '--workflow', str(directory / 'workflow.json'), '--image', str(directory / job['input_file']),
               '--record', str(directory / 'run_record.json')]
    return command, job


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default='.')
    p.add_argument('--job-dir', required=True)
    p.add_argument('--url', required=True)
    p.add_argument('--comfy-root')
    p.add_argument('--execute', action='store_true')
    a = p.parse_args()
    lock = None
    attempt_started = False
    try:
        root = Path(a.root).resolve(); directory = relative_file(root, a.job_dir)
        command, job = job_command(root, directory, a.url)
        if not a.execute:
            print(json.dumps({'submitted': False, 'command': command, 'note': 'Add --execute only after local review.'}, ensure_ascii=False, indent=2))
            return 0
        lock = root / 'local/production/.gpu_submission.lock'
        lock.parent.mkdir(parents=True, exist_ok=True)
        # Shared across this project's supported submissions. External GUI queues are checked by probe.
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        try:
            command, job = job_command(root, directory, a.url)
            if job.get('fid1_contract'):
                require(bool(a.comfy_root), '--comfy-root is required to execute a FID1 job')
                runtime = validate_fid1_runtime(root, Path(a.comfy_root), job, a.url)
            else:
                runtime = None
            intent = directory / 'submission_intent.json'
            with intent.open('x', encoding='utf-8') as stream:
                json.dump({'state':'ATTEMPT_STARTED', 'pid':os.getpid(), 'probe_sha256':sha256_file(root/'scripts/p1_comfy_probe.py'),
                           'fid1_runtime':runtime}, stream)
            attempt_started = True
            finished = subprocess.run(command, check=False)
            write_json(directory/'submission_result.json', {'returncode':finished.returncode, 'note':'Do not retry automatically. Read run_record/prompt history.'})
            return finished.returncode
        finally:
            lock.unlink(missing_ok=True)
    except Exception as exc:
        print(json.dumps({'submitted': None if attempt_started else False, 'error': str(exc), 'note':'Check history if an attempt started; no automatic retry.'}, ensure_ascii=False))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
