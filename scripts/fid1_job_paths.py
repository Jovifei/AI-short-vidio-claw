"""Canonical source-trial job paths, checked before resolving any aliases."""
from pathlib import Path
import re

try:
    from .preproduction import require
    from .sync_repo_media import safe
    from .fid1_deploy import is_junction
except ImportError:
    from preproduction import require
    from sync_repo_media import safe
    from fid1_deploy import is_junction


LOCAL = 'local/production/T1_SOURCE_PILOT'
SHOTS = {'SH901', 'SH902', 'SH903'}


def safe_project_path(root, value):
    """Return a project child without erasing traversal or reparse components."""
    root = Path(root).resolve(strict=True)
    require(isinstance(value, (str, Path)) and bool(str(value)), 'missing FID1 path')
    raw = str(value)
    candidate = Path(raw)
    # Native absolute paths are accepted by Python APIs; CLI relative paths retain
    # the repository's forward-slash convention. Inspect raw before Path/resolve.
    lexical = raw.replace('\\', '/') if candidate.is_absolute() else raw
    require(all(part not in {'.', '..'} for part in lexical.split('/')),
            'FID1 path contains traversal/dot components')
    if candidate.is_absolute():
        require(candidate.is_relative_to(root), 'FID1 path is outside project')
        relative = candidate.relative_to(root).as_posix()
    else:
        relative = raw
    path = safe(root, relative)
    current = root
    for part in relative.split('/'):
        current /= part
        require(not current.is_symlink() and not is_junction(current),
                'FID1 path contains a link/junction/reparse point')
        try:
            attributes=getattr(current.lstat(),'st_file_attributes',0)
        except (FileNotFoundError,NotADirectoryError):
            attributes=0
        require(not attributes & 0x400, 'FID1 path contains a Windows reparse point')
    return path


def canonical_job_directory(root, value, shot_id):
    """Require the actual shot's video/<shot>/jobs/takeNN before any writes."""
    require(shot_id in SHOTS, 'unknown FID1 source shot')
    path = safe_project_path(root, value)
    relative = path.relative_to(Path(root).resolve(strict=True)).as_posix()
    prefix = f'{LOCAL}/video/{shot_id}/jobs/'
    require(re.fullmatch(re.escape(prefix) + r'take[0-9]{2,}', relative) is not None,
            'FID1 job requires the actual shot canonical video/shot/jobs/takeNN path')
    return path
