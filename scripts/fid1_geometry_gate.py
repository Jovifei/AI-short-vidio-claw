#!/usr/bin/env python3
"""Hash-bound geometry evidence for schema-6 FID1 source-only trials."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image

try:
    from .fid1_job_paths import safe_project_path
    from .preproduction import read_json, require
except ImportError:
    from fid1_job_paths import safe_project_path
    from preproduction import read_json, require


MANIFEST_PATH = "config/source_fidelity_trials/geometry_manifest.json"
MANIFEST_FIELDS = {"schema_version", "entries"}
ENTRY_FIELDS = {
    "profile_id", "profile_path", "profile_byte_sha256", "source_type", "source_path",
    "source_sha256", "canonical_roi_sha256", "status", "review_layer",
    "observer", "human_accepted", "geometry_path", "geometry_sha256",
    "overlay_path", "overlay_sha256",
}
GEOMETRY_FIELDS = {
    "source_path", "source_sha256", "source_size", "latent_size",
    "geometry_mapping", "human_acceptance", "review", "local_observation",
    "candidate_prepare",
}
HEX64 = set("0123456789abcdef")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _profile_byte_identities(path: Path) -> tuple[str, dict[str, str]]:
    """Return the actual profile hash and the two explicitly allowed EOL hashes."""
    raw = path.read_bytes()
    lf_count = raw.count(b"\n")
    crlf_count = raw.count(b"\r\n")
    without_crlf = raw.replace(b"\r\n", b"")
    require(lf_count > 0 and b"\r" not in without_crlf,
            "geometry-bound profile must use consistent LF or CRLF line endings")
    if crlf_count:
        require(lf_count == crlf_count and b"\n" not in without_crlf,
                "geometry-bound profile has mixed or invalid line endings")
        lf_bytes = raw.replace(b"\r\n", b"\n")
    else:
        require(b"\r" not in raw, "geometry-bound profile has invalid line endings")
        lf_bytes = raw
    crlf_bytes = lf_bytes.replace(b"\n", b"\r\n")
    identities = {
        "LF": hashlib.sha256(lf_bytes).hexdigest(),
        "CRLF": hashlib.sha256(crlf_bytes).hexdigest(),
    }
    raw_sha = hashlib.sha256(raw).hexdigest()
    require(raw_sha in identities.values(),
            "geometry-bound profile raw bytes are not a registered LF or CRLF form")
    return raw_sha, identities


def _is_sha256(value) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX64


def _canonical_sha256(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonical_roi_sha256(rois) -> str:
    require(isinstance(rois, list), "geometry profile ROIs must be a list")
    return _canonical_sha256(rois)


def _existing_file(root: Path, relative: str, label: str) -> Path:
    path = safe_project_path(root, relative)
    require(path.is_file(), label + " is missing or not a file")
    return path


def _expected_geometry_mapping(profile):
    width = profile["width"] // 16
    height = profile["height"] // 16
    result = []
    for roi in profile["anchor_rois"]:
        x0, y0, x1, y1 = (roi[key] for key in ("x0", "y0", "x1", "y1"))
        result.append({
            "id": roi["id"],
            "latent_xyxy": [
                math.floor(x0 * width), math.floor(y0 * height),
                math.ceil(x1 * width), math.ceil(y1 * height),
            ],
            "feather": roi["feather_latent"],
            "strength": roi["preserve_strength"],
        })
    return result


def verify_geometry_evidence(root: Path | str, profile_path: str, profile: dict, source_path: str) -> dict:
    """Verify current source, profile, ROI overlay, geometry receipt, and positive status.

    The returned receipt is suitable for freezing in a prepared job. It carries
    a geometry-only status; it does not record or imply Jovi visual acceptance.
    """
    root = Path(root).resolve(strict=True)
    require(isinstance(profile, dict) and profile.get("schema_version") == 6
            and profile.get("anchor_strategy") == "wan22_timestep_aware_roi_strength_v4",
            "geometry gate only accepts the independent schema-6 strength profile")
    require(isinstance(profile_path, str) and profile_path.startswith("config/source_fidelity_trials/"),
            "geometry profile path is outside the trial config")
    profile_file = _existing_file(root, profile_path, "geometry-bound profile")
    source_file = _existing_file(root, source_path, "geometry-bound source")
    manifest_file = _existing_file(root, MANIFEST_PATH, "geometry manifest")
    profile_sha, profile_byte_sha = _profile_byte_identities(profile_file)
    source_sha = _sha256(source_file)
    require(source_path.startswith("assets/media/source_library/"),
            "geometry source must be the approved Git source image")
    require(source_sha == profile.get("input_sha256"), "geometry source hash differs from the profile input")

    manifest = read_json(manifest_file)
    require(isinstance(manifest, dict) and set(manifest) == MANIFEST_FIELDS
            and type(manifest.get("schema_version")) is int and manifest["schema_version"] == 1,
            "geometry manifest schema/fields are invalid")
    entries = manifest.get("entries")
    require(isinstance(entries, list) and bool(entries), "geometry manifest has no evidence entries")
    ids = []
    for entry in entries:
        require(isinstance(entry, dict) and set(entry) == ENTRY_FIELDS,
                "geometry manifest entry fields are invalid")
        ids.append(entry.get("profile_id"))
    require(all(isinstance(item, str) and item for item in ids) and len(ids) == len(set(ids)),
            "geometry manifest profile IDs must be unique")
    matches = [entry for entry in entries if entry.get("profile_id") == profile.get("profile_id")]
    require(len(matches) == 1, "profile has no unique geometry evidence entry")
    entry = matches[0]

    require(entry.get("profile_path") == profile_path, "geometry manifest profile path mismatch")
    registered_profile_hashes = entry.get("profile_byte_sha256")
    require(isinstance(registered_profile_hashes, dict)
            and set(registered_profile_hashes) == {"LF", "CRLF"}
            and all(_is_sha256(value) for value in registered_profile_hashes.values())
            and registered_profile_hashes == profile_byte_sha,
            "geometry manifest profile LF/CRLF hashes mismatch")
    require(entry.get("source_path") == source_path
            and _is_sha256(entry.get("source_sha256")) and entry["source_sha256"] == source_sha,
            "geometry manifest source path/hash mismatch")
    roi_sha = canonical_roi_sha256(profile.get("anchor_rois"))
    require(_is_sha256(entry.get("canonical_roi_sha256")) and entry["canonical_roi_sha256"] == roi_sha,
            "geometry manifest canonical ROI hash mismatch")
    require(entry.get("source_type") in {"REAL_SOURCE", "SYNTHETIC_FIXTURE"},
            "geometry manifest source type is unknown")
    require(entry.get("review_layer") == "INPUT_GEOMETRY_ONLY"
            and entry.get("human_accepted") is False,
            "geometry status cannot stand in for user visual acceptance")
    require(isinstance(entry.get("observer"), str) and bool(entry["observer"].strip()),
            "geometry evidence observer is missing")
    status = entry.get("status")
    require(status in {"GEOMETRY_BLOCKED", "LOCAL_GEOMETRY_PASS"},
            "geometry evidence status is missing or unknown")

    geometry_path = entry.get("geometry_path")
    overlay_path = entry.get("overlay_path")
    require(isinstance(geometry_path, str) and geometry_path.startswith("docs/reviews/"),
            "geometry JSON path is missing or outside review evidence")
    require(isinstance(overlay_path, str) and overlay_path.startswith("docs/reviews/"),
            "geometry overlay path is missing or outside review evidence")
    geometry_file = _existing_file(root, geometry_path, "geometry JSON")
    overlay_file = _existing_file(root, overlay_path, "geometry overlay")
    geometry_sha = _sha256(geometry_file)
    overlay_sha = _sha256(overlay_file)
    require(_is_sha256(entry.get("geometry_sha256")) and entry["geometry_sha256"] == geometry_sha,
            "geometry JSON hash differs from the manifest")
    require(_is_sha256(entry.get("overlay_sha256")) and entry["overlay_sha256"] == overlay_sha,
            "geometry overlay hash differs from the manifest")

    geometry = read_json(geometry_file)
    require(isinstance(geometry, dict) and set(geometry) == GEOMETRY_FIELDS,
            "geometry JSON fields are invalid")
    try:
        with Image.open(source_file) as source_image:
            require(source_image.format == "PNG", "geometry source must be a PNG")
            actual_source_size = list(source_image.size)
            source_image.verify()
        with Image.open(overlay_file) as overlay_image:
            require(overlay_image.format == "PNG", "geometry overlay must be a PNG")
            actual_overlay_size = list(overlay_image.size)
            overlay_image.verify()
    except (OSError, ValueError) as exc:
        raise ValueError(f"geometry source/overlay image is unreadable: {exc}") from exc
    source_size = geometry.get("source_size")
    require(isinstance(source_size, list) and len(source_size) == 2
            and all(type(value) is int and value > 0 for value in source_size)
            and source_size == actual_source_size,
            "geometry source_size differs from the bound source PNG")
    require(actual_overlay_size == actual_source_size,
            "geometry overlay PNG dimensions differ from the bound source PNG")
    require(str(geometry.get("source_path", "")).replace("\\", "/") == source_path
            and geometry.get("source_sha256") == source_sha,
            "geometry JSON is bound to a different source image")
    require(geometry.get("latent_size") == [profile["width"] // 16, profile["height"] // 16]
            and geometry.get("geometry_mapping") == _expected_geometry_mapping(profile),
            "geometry JSON ROI mapping differs from the frozen profile")
    require(geometry.get("review") == status
            and geometry.get("human_acceptance") is entry["human_accepted"],
            "geometry JSON status/review layer differs from the manifest")
    require(isinstance(geometry.get("local_observation"), str)
            and bool(geometry["local_observation"].strip())
            and isinstance(geometry.get("candidate_prepare"), str)
            and bool(geometry["candidate_prepare"].strip()),
            "geometry JSON observation or candidate state is missing")
    if entry["source_type"] == "SYNTHETIC_FIXTURE":
        require(entry["observer"] == "TEST_FIXTURE_ONLY"
                and geometry["local_observation"].startswith("SYNTHETIC_FIXTURE_ONLY")
                and geometry["candidate_prepare"].startswith("SYNTHETIC_FIXTURE_ONLY"),
                "synthetic geometry evidence must remain explicitly fixture-only")
    else:
        require(entry["observer"] != "TEST_FIXTURE_ONLY"
                and not geometry["local_observation"].startswith("SYNTHETIC_FIXTURE_ONLY")
                and not geometry["candidate_prepare"].startswith("SYNTHETIC_FIXTURE_ONLY"),
                "synthetic fixture evidence cannot be relabeled as real-source geometry")

    manifest_sha = _sha256(manifest_file)
    files = {
        MANIFEST_PATH: manifest_sha,
        geometry_path: geometry_sha,
        overlay_path: overlay_sha,
    }
    receipt = {
        "schema_version": 1,
        "profile_id": profile["profile_id"],
        "profile_path": profile_path,
        "profile_sha256": profile_sha,
        "profile_byte_sha256": profile_byte_sha,
        "source_type": entry["source_type"],
        "source_path": source_path,
        "source_sha256": source_sha,
        "canonical_roi_sha256": roi_sha,
        "status": status,
        "review_layer": "INPUT_GEOMETRY_ONLY",
        "human_accepted": False,
        "observer": entry["observer"],
        "manifest_path": MANIFEST_PATH,
        "manifest_sha256": manifest_sha,
        "geometry_path": geometry_path,
        "geometry_sha256": geometry_sha,
        "overlay_path": overlay_path,
        "overlay_sha256": overlay_sha,
        "files": files,
    }
    require(status == "LOCAL_GEOMETRY_PASS", "geometry evidence is blocked; prepare refused")
    return receipt
