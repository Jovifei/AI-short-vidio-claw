#!/usr/bin/env python3
"""Default dry-run; execute only one immutable prepared job through the existing probe."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse
from preproduction import checked_asset, read_json, relative_file, require, sha256_file, validate_graph, write_json


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
            intent = directory / 'submission_intent.json'
            with intent.open('x', encoding='utf-8') as stream:
                json.dump({'state':'ATTEMPT_STARTED', 'pid':os.getpid(), 'probe_sha256':sha256_file(root/'scripts/p1_comfy_probe.py')}, stream)
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
