#!/usr/bin/env python3
"""Install, verify, or roll back the single FID1 custom node in an existing ComfyUI."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat

try:
    from .preproduction import read_json, require, write_json
except ImportError:
    from preproduction import read_json, require, write_json


SOURCE_MANIFEST = "docs/reviews/20261011-source-fidelity/installed_comfy_source/source_manifest.json"
NODE_SOURCE = "scripts/fid1_wan_latent_anchor_node.py"
REPORT = "local/reports/fid1_deployment.json"
PLUGIN_DIR = Path("custom_nodes/fid1_wan_roi_anchor")
PLUGIN_FILE = "__init__.py"
PLUGIN_MANIFEST = "FID1_DEPLOYMENT.json"
EXPECTED_COMFY_COMMIT = "6b747c0428c343e1417219641db93a4fb7cb69ae"


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_project_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    require(path.is_relative_to(root), "project path escapes repository: " + relative)
    return path


def resolve_comfy_path(root: Path, relative: Path) -> Path:
    path = (root / relative).resolve()
    require(path.is_relative_to(root), "ComfyUI path escapes selected root: " + str(relative))
    return path


def is_junction(path: Path) -> bool:
    """Detect junctions; fail closed on other Windows reparse points too."""
    detector = getattr(path, "is_junction", None)
    if callable(detector):
        return bool(detector())
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except (FileNotFoundError, NotADirectoryError):
        return False
    except OSError:
        return True
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def require_safe_child_directory(parent: Path, child: Path, label: str, *, required: bool = False) -> None:
    parent = parent.resolve(strict=True)
    require(child.parent.resolve(strict=True) == parent, label + " parent changed")
    require(not child.is_symlink() and not is_junction(child), label + " is a symlink or junction")
    if child.exists():
        require(child.is_dir(), label + " is not a directory")
        resolved = child.resolve(strict=True)
        require(resolved.is_relative_to(parent), label + " escapes its owned directory")
    elif required:
        raise ValueError(label + " is missing")


def require_safe_owned_file(parent: Path, child: Path, label: str) -> None:
    require(not child.is_symlink() and not is_junction(child), label + " is a symlink or junction")
    require(child.is_file(), label + " is missing")
    resolved = child.resolve(strict=True)
    require(resolved.is_relative_to(parent.resolve(strict=True)), label + " escapes its owned directory")


def comfy_contract(root: Path, comfy_root: Path):
    manifest_path = resolve_project_path(root, SOURCE_MANIFEST)
    manifest = read_json(manifest_path)
    require(manifest.get("purpose") == "READ_ONLY_INSTALLED_SOURCE_AUDIT", "source manifest purpose changed")
    require(manifest.get("commit") == EXPECTED_COMFY_COMMIT, "unexpected audited ComfyUI revision")
    copies = manifest.get("copies")
    require(isinstance(copies, list) and len(copies) >= 5, "incomplete audited ComfyUI dependency manifest")
    checked = {}
    for item in copies:
        relative = item.get("path")
        expected = item.get("sha256")
        require(isinstance(relative, str) and isinstance(expected, str) and len(expected) == 64,
                "invalid ComfyUI dependency entry")
        installed = resolve_comfy_path(comfy_root, Path(relative))
        require(installed.is_file(), "ComfyUI dependency missing: " + relative)
        actual = file_sha(installed)
        require(actual == expected, "ComfyUI dependency hash mismatch: " + relative)
        checked[relative] = actual
    return {
        "commit": manifest["commit"],
        "manifest_sha256": file_sha(manifest_path),
        "files": checked,
        "dependency_sha256": hashlib.sha256(json.dumps(checked, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
    }


def paths(root: Path, comfy_root: Path):
    root = root.resolve(strict=True)
    comfy_root = comfy_root.resolve(strict=True)
    require(comfy_root.is_dir(), "selected ComfyUI root is not a directory")
    custom_nodes = comfy_root / "custom_nodes"
    require_safe_child_directory(comfy_root, custom_nodes, "ComfyUI custom_nodes", required=True)
    custom_nodes = custom_nodes.resolve(strict=True)
    require(custom_nodes.is_relative_to(comfy_root), "ComfyUI custom_nodes escapes selected root")
    target_dir = custom_nodes / PLUGIN_DIR.name
    report = resolve_project_path(root, REPORT)
    return root, comfy_root, target_dir, report


def deploy(root: Path | str, comfy_root: Path | str):
    root, comfy_root, target_dir, report_path = paths(Path(root), Path(comfy_root))
    contract = comfy_contract(root, comfy_root)
    source = resolve_project_path(root, NODE_SOURCE)
    source_hash = file_sha(source)
    require_safe_child_directory(target_dir.parent, target_dir, "FID1 plugin directory")
    if target_dir.exists():
        require(target_dir.is_dir(), "FID1 plugin path conflicts with a non-directory")
        package_manifest_path = target_dir / PLUGIN_MANIFEST
        installed_path = target_dir / PLUGIN_FILE
        require_safe_owned_file(target_dir, package_manifest_path, "FID1 ownership manifest")
        require_safe_owned_file(target_dir, installed_path, "FID1 installed node")
        installed_manifest = read_json(package_manifest_path)
        require(installed_manifest.get("schema_version") == 1
                and installed_manifest.get("source_rel") == NODE_SOURCE
                and installed_manifest.get("comfy_commit") == contract["commit"],
                "existing FID1 plugin ownership manifest conflicts")
        require(file_sha(installed_path) == installed_manifest.get("installed_sha256"),
                "installed FID1 node changed outside the deployment tool")
        require(installed_manifest.get("source_sha256") == source_hash
                and installed_manifest.get("dependency_sha256") == contract["dependency_sha256"],
                "owned FID1 node is from another source revision; roll it back before installing")
        require(report_path.is_file(), "FID1 ownership receipt is missing; refusing to adopt existing files")
        report = read_json(report_path)
        require(report.get("state") == "INSTALLED"
                and report.get("target_dir") == str(target_dir)
                and report.get("installed_sha256") == source_hash,
                "local FID1 deployment receipt does not match the installed package")
        return {"status": "ALREADY_INSTALLED", "target_dir": str(target_dir), "sha256": source_hash}

    if report_path.exists():
        previous = read_json(report_path)
        require(previous.get("state") == "ROLLED_BACK", "deployment receipt exists but the plugin is absent")

    target_dir.mkdir()
    installed_path = target_dir / PLUGIN_FILE
    package_manifest_path = target_dir / PLUGIN_MANIFEST
    try:
        payload = source.read_bytes()
        temp_path = target_dir / (PLUGIN_FILE + ".installing")
        temp_path.write_bytes(payload)
        os.replace(temp_path, installed_path)
        installed_hash = file_sha(installed_path)
        require(installed_hash == source_hash, "installed FID1 node failed byte verification")
        installed_manifest = {
            "schema_version": 1,
            "node_class": "FID1WanSourceROIAnchor",
            "source_rel": NODE_SOURCE,
            "source_sha256": source_hash,
            "installed_sha256": installed_hash,
            "comfy_commit": contract["commit"],
            "comfy_manifest_sha256": contract["manifest_sha256"],
            "dependency_sha256": contract["dependency_sha256"],
        }
        write_json(package_manifest_path, installed_manifest)
        report = {
            **installed_manifest,
            "state": "INSTALLED",
            "comfy_root": str(comfy_root),
            "target_dir": str(target_dir),
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "rollback": "python scripts/fid1_deploy.py rollback --root . --comfy-root " + str(comfy_root),
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        write_json(report_path, report)
        return {"status": "INSTALLED", "target_dir": str(target_dir), "sha256": installed_hash}
    except Exception:
        for path in (installed_path, package_manifest_path, target_dir / (PLUGIN_FILE + ".installing")):
            if path.is_file():
                path.unlink()
        try:
            target_dir.rmdir()
        except OSError:
            pass
        raise


def verify_installed(root: Path | str, comfy_root: Path | str, expected_node_sha256: str | None = None):
    root, comfy_root, target_dir, report_path = paths(Path(root), Path(comfy_root))
    contract = comfy_contract(root, comfy_root)
    require(report_path.is_file(), "FID1 deployment receipt is missing")
    require_safe_child_directory(target_dir.parent, target_dir, "FID1 plugin directory", required=True)
    report = read_json(report_path)
    target_path = resolve_comfy_path(comfy_root, PLUGIN_DIR / PLUGIN_FILE)
    package_manifest = read_json(resolve_comfy_path(comfy_root, PLUGIN_DIR / PLUGIN_MANIFEST))
    actual = file_sha(target_path)
    require(report.get("state") == "INSTALLED" and package_manifest.get("installed_sha256") == actual
            and report.get("installed_sha256") == actual,
            "FID1 deployment files or receipt changed")
    require(report.get("target_dir") == str(target_dir) and report.get("comfy_root") == str(comfy_root),
            "FID1 deployment belongs to another ComfyUI root")
    require(package_manifest.get("source_sha256") == actual == package_manifest.get("installed_sha256"),
            "installed FID1 node source hash mismatch")
    require(package_manifest.get("node_class") == "FID1WanSourceROIAnchor"
            and package_manifest.get("source_rel") == NODE_SOURCE
            and package_manifest.get("comfy_commit") == contract["commit"]
            and package_manifest.get("dependency_sha256") == contract["dependency_sha256"],
            "installed FID1 ComfyUI dependency contract changed")
    if expected_node_sha256 is not None:
        require(actual == expected_node_sha256, "installed FID1 node does not match the prepared job")
    return {"status": "VERIFIED", "target": str(target_path), "sha256": actual, "comfy_commit": contract["commit"]}


def rollback(root: Path | str, comfy_root: Path | str):
    root, comfy_root, target_dir, report_path = paths(Path(root), Path(comfy_root))
    require(report_path.is_file(), "FID1 deployment receipt is missing")
    report = read_json(report_path)
    require(report.get("state") == "INSTALLED" and report.get("comfy_root") == str(comfy_root)
            and report.get("target_dir") == str(target_dir), "FID1 deployment receipt does not match the requested target")
    require_safe_child_directory(target_dir.parent, target_dir, "installed FID1 plugin directory", required=True)
    node_path = target_dir / PLUGIN_FILE
    manifest_path = target_dir / PLUGIN_MANIFEST
    require_safe_owned_file(target_dir, node_path, "FID1 installed node")
    require_safe_owned_file(target_dir, manifest_path, "FID1 ownership manifest")
    package_manifest = read_json(manifest_path)
    require(file_sha(node_path) == report.get("installed_sha256") == package_manifest.get("installed_sha256"),
            "installed FID1 node changed; refusing rollback")
    allowed = {PLUGIN_FILE, PLUGIN_MANIFEST, "__pycache__"}
    require({entry.name for entry in target_dir.iterdir()} <= allowed, "FID1 plugin directory contains unowned files")
    cache = target_dir / "__pycache__"
    require_safe_child_directory(target_dir, cache, "FID1 bytecode cache")
    if cache.exists():
        for entry in cache.iterdir():
            require(entry.is_file() and not entry.is_symlink() and not is_junction(entry) and entry.suffix == ".pyc"
                    and entry.name.startswith("__init__"), "FID1 bytecode cache contains unowned files")
        for entry in cache.iterdir():
            entry.unlink()
        cache.rmdir()
    node_path.unlink()
    manifest_path.unlink()
    target_dir.rmdir()
    report["state"] = "ROLLED_BACK"
    report["rolled_back_at"] = datetime.now(timezone.utc).isoformat()
    write_json(report_path, report)
    return {"status": "ROLLED_BACK", "target_dir": str(target_dir)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("deploy", "verify", "rollback"))
    parser.add_argument("--root", default=".")
    parser.add_argument("--comfy-root", required=True)
    args = parser.parse_args(argv)
    try:
        result = {"deploy": deploy, "verify": verify_installed, "rollback": rollback}[args.command](args.root, args.comfy_root)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
