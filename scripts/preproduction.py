#!/usr/bin/env python3
"""Offline production contracts. No model downloads, network calls or approvals by inference."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath

CAST = {"DAIYU", "WUKONG"}
APPROVED = {"USER_APPROVED", "PRODUCTION_READY"}

class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=_unique)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc


def write_json(path, value):
    """Atomic replacement. Callers must explicitly decide whether replacement is allowed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
            json.dump(value, out, ensure_ascii=False, indent=2)
            out.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def relative_file(root, relative):
    require(isinstance(relative, str) and relative.strip(), "missing relative path")
    win = PureWindowsPath(relative)
    parts = relative.replace("\\", "/").split("/")
    require(not win.drive and not win.root and not Path(relative).is_absolute(), "absolute path forbidden")
    require(all(p not in {"", ".", ".."} for p in parts), "non-canonical relative path")
    require(all(":" not in p for p in parts), "colon/alternate stream forbidden")
    root = Path(root).resolve()
    path = root.joinpath(*parts).resolve()
    require(path.is_relative_to(root), "path escapes repository root (including symlinks)")
    return path


def checked_asset(root, relative, expected):
    require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected), "missing/invalid SHA256")
    path = relative_file(root, relative)
    require(path.is_file(), f"missing asset: {relative}")
    require(sha256_file(path) == expected, f"asset hash changed: {relative}")
    return path


def check_plan(plan):
    require(isinstance(plan, dict) and plan.get("schema_version") == 5, "plan schema_version must be 5")
    require(re.fullmatch(r"[A-Z][A-Z0-9_]+", plan.get("project_id", "")), "invalid project_id")
    require(plan.get("fps") == 24, "v5 timeline is frozen at 24 fps")
    shots = plan.get("shots")
    require(isinstance(shots, list) and shots, "empty shot list")
    cursor, seen = 0, set()
    for shot in shots:
        sid = shot.get("shot_id", "")
        require(re.fullmatch(r"(?:SH\d{3}|COMP\d{2})", sid), f"invalid shot_id: {sid}")
        require(sid not in seen, f"duplicate shot: {sid}")
        seen.add(sid)
        require(type(shot.get("start_frame")) is int and shot["start_frame"] == cursor, f"gap/overlap at {sid}")
        length = shot.get("duration_frames")
        require(type(length) is int and length > 0, f"invalid duration: {sid}")
        cursor += length
        cast = shot.get("characters")
        require(isinstance(cast, list) and cast and len(set(cast)) == len(cast), f"invalid cast: {sid}")
        require(set(cast) <= CAST, f"unknown character: {sid}")
        require(set(shot.get("costume_stages", {})) == set(cast), f"costume/cast mismatch: {sid}")
        require(shot.get("motion_tier") in {"M0", "M1", "M2", "M3"}, f"missing motion tier: {sid}")
        require(shot.get("render_mode") in {"STILL", "I2V"}, f"invalid render mode: {sid}")
        if shot["render_mode"] == "I2V":
            require(shot["motion_tier"] in {"M1", "M2"}, f"unsafe automatic motion: {sid}")
            profile = shot.get("i2v", {})
            for dim in ("width", "height"):
                v = profile.get(dim)
                require(type(v) is int and v > 0 and v % 32 == 0, f"invalid {dim}: {sid}")
            frames = profile.get("frames")
            require(type(frames) is int and frames > 1 and (frames-1) % 4 == 0, f"invalid source frames: {sid}")
            require(profile.get("fps") == 24 and frames >= length, f"source shorter than cut: {sid}")
            require(bool(shot.get("motion_prompt", "").strip()), f"empty motion prompt: {sid}")
    require(cursor == plan.get("total_frames"), "timeline total does not match total_frames")
    return {"shot_count": len(shots), "frames": cursor, "seconds": cursor / plan["fps"]}


def plan_shot(plan, sid):
    check_plan(plan)
    match = [s for s in plan["shots"] if s["shot_id"] == sid]
    require(len(match) == 1, f"unknown shot: {sid}")
    return match[0]


def approval_evidence(value, sid, digest):
    require(isinstance(value, dict), "missing scoped approval evidence")
    require(value.get("subject_id") == sid and value.get("sha256") == digest, "approval bound to another asset/shot")
    require(value.get("decision") == "approve", "decision is not approve")
    require(value.get("scope") in {"reference", "keyframe"}, "invalid approval scope")
    require(isinstance(value.get("user_quote"), str) and bool(value["user_quote"].strip()), "missing user quote")
    require(isinstance(value.get("source"), str) and bool(value["source"].strip()), "missing approval source")
    try:
        stamp = datetime.fromisoformat(value.get("recorded_at", "").replace("Z", "+00:00"))
        require(stamp.tzinfo is not None, "approval timestamp needs timezone")
    except (ValueError, TypeError) as exc:
        raise ContractError("invalid approval timestamp") from exc


def validate_keyframe(root, plan, manifest, registry, sid):
    shot = plan_shot(plan, sid)
    require(manifest.get("schema_version") == 5, "approval manifest schema_version must be 5")
    require(manifest.get("project_id") == plan["project_id"], "manifest belongs to another project")
    require(manifest.get("visual_target_id") == plan["visual_target_id"] == registry.get("visual_target_id"), "visual target mismatch")
    require(registry.get("schema_version") == 5, "asset registry schema_version must be 5")
    entry = manifest.get("shots", {}).get(sid, {})
    require(entry.get("status") in APPROVED and entry.get("approved_by_user") is True, f"{sid}: not explicitly approved")
    require(entry.get("characters") == shot["characters"], "approved cast differs from shot plan")
    relative = entry.get("approved_keyframe", "")
    require(relative.startswith(f"local/production/{plan['project_id']}/approved/"), "keyframe must be in exact approved directory")
    image = checked_asset(root, relative, entry.get("sha256"))
    require(image.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}, "unsupported keyframe extension")
    evidence = entry.get("approval_evidence")
    approval_evidence(evidence, sid, entry["sha256"])
    require(evidence["scope"] == "keyframe", "keyframe needs keyframe-scoped approval")
    assets = registry.get("assets", {})
    for char in shot["characters"]:
        identities = entry.get("identity_refs", {}).get(char)
        require(isinstance(identities, list) and identities and len(set(identities)) == len(identities), f"{char}: missing/duplicate identity references")
        costume = entry.get("costume_refs", {}).get(char, {})
        require(isinstance(costume, dict) and costume.get("stage_id") == shot["costume_stages"][char], f"{char}: wrong costume stage")
        for aid, role in [(a, "face") for a in identities] + [(costume.get("asset_id"), "costume")]:
            asset = assets.get(aid, {})
            require(asset.get("status") == "USER_APPROVED", f"reference not approved: {aid}")
            require(asset.get("character") == char and role in asset.get("roles", []), f"wrong reference role/character: {aid}")
            if role == "costume":
                require(asset.get("stage_id") == costume["stage_id"] or costume["stage_id"] in asset.get("applicable_stages", []), f"reference costume stage mismatch: {aid}")
            approval_evidence(asset.get("approval_evidence"), aid, asset.get("sha256"))
            require(asset["approval_evidence"]["scope"] == "reference", "reference approval scope mismatch")
            checked_asset(root, asset.get("path"), asset.get("sha256"))
    return shot, entry, image


def validate_graph(graph, cast):
    """Check the executed source→sampler→decode→save chain, not an unused LoadImage."""
    require(isinstance(graph, dict) and "nodes" not in graph, "expected API graph, not UI graph")
    allowed = {"UNETLoader", "CLIPLoader", "VAELoader", "ModelSamplingSD3", "CLIPTextEncode", "LoadImage", "Wan22ImageToVideoLatent", "KSampler", "VAEDecode", "CreateVideo", "SaveVideo"}
    require(all(isinstance(n, dict) and n.get("class_type") in allowed for n in graph.values()), "unexpected production node; explicit review required")
    def node(kind):
        found = [(str(k), v) for k, v in graph.items() if v.get("class_type") == kind]
        require(len(found) == 1, f"expected exactly one {kind}")
        return found[0]
    def linked(n, field, target):
        require(n.get("inputs", {}).get(field) == [target, 0], f"invalid live connection: {field}")
    load_id, load = node("LoadImage")
    latent_id, latent = node("Wan22ImageToVideoLatent")
    sampler_id, sampler = node("KSampler")
    decode_id, decode = node("VAEDecode")
    video_id, video = node("CreateVideo")
    _, save = node("SaveVideo")
    linked(latent, "start_image", load_id)
    linked(sampler, "latent_image", latent_id)
    linked(decode, "samples", sampler_id)
    linked(video, "images", decode_id)
    linked(save, "video", video_id)
    vae_id, vae = node("VAELoader")
    linked(latent, "vae", vae_id)
    linked(decode, "vae", vae_id)
    require(vae["inputs"].get("vae_name") == "wan2.2_vae.safetensors", "unexpected VAE")
    clip_id, clip = node("CLIPLoader")
    require(clip["inputs"].get("clip_name") == "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "unexpected text encoder")
    require(len(graph) == 12, "unexpected extra production nodes")
    model_id, model = node("UNETLoader")
    sample_model_id, sample_model = node("ModelSamplingSD3")
    linked(sample_model, "model", model_id)
    linked(sampler, "model", sample_model_id)
    require(model["inputs"].get("unet_name") == "wan2.2_ti2v_5B_fp16.safetensors", "unexpected diffusion model")
    require(latent["inputs"].get("batch_size") == 1, "batch_size must be one")
    texts = {}
    for role in ("positive", "negative"):
        edge = sampler["inputs"].get(role)
        require(isinstance(edge, list) and len(edge) == 2 and edge[1] == 0, f"invalid {role} link")
        n = graph.get(str(edge[0]), {})
        require(n.get("class_type") == "CLIPTextEncode", f"{role} is not CLIPTextEncode")
        linked(n, "clip", clip_id)
        texts[role] = n.get("inputs", {}).get("text", "")
        require(isinstance(texts[role], str) and bool(texts[role].strip()), f"empty {role} prompt")
    require(not any(x in texts["positive"].lower() for x in ("subway musician", "1970", "地铁乐手")), "benchmark prompt in production graph")
    if len(cast) > 1:
        require(not any(x in texts["negative"].lower() for x in ("second person", "第二个人", "human face", "人脸", "人类五官")), "single-character/human-face exclusion in a two-character shot")
    return {"load": load_id, "latent": latent_id, "sampler": sampler_id, "video": video_id,
            "save": node("SaveVideo")[0], "positive": str(sampler["inputs"]["positive"][0])}


def prepare(root, plan_path, approval_path, registry_path, workflow_path, sid, seed, out):
    root = Path(root).resolve()
    for path in (plan_path, approval_path, registry_path, workflow_path, out):
        require(Path(path).resolve().is_relative_to(root), "all inputs/output must stay under repository")
    require(type(seed) is int and 0 <= seed < 2**63, "invalid seed")
    plan, manifest, registry = map(read_json, (plan_path, approval_path, registry_path))
    shot, entry, image = validate_keyframe(root, plan, manifest, registry, sid)
    require(shot["render_mode"] == "I2V" and shot["motion_tier"] in {"M1", "M2"}, "shot is static/high risk, not eligible for I2V")
    graph = deepcopy(read_json(workflow_path))
    ids = validate_graph(graph, shot["characters"])
    profile = shot["i2v"]
    graph[ids["latent"]]["inputs"].update(width=profile["width"], height=profile["height"], length=profile["frames"])
    graph[ids["sampler"]]["inputs"]["seed"] = seed
    graph[ids["positive"]]["inputs"]["text"] = shot["motion_prompt"]
    graph[ids["video"]]["inputs"]["fps"] = profile["fps"]
    prefix = f"video/production/{plan['project_id']}/{sid}/{sid}_{entry['sha256'][:12]}_{seed}"
    graph[ids["save"]]["inputs"]["filename_prefix"] = prefix
    input_filename = f"{plan['project_id']}_{sid}_{entry['sha256'][:12]}_{seed}{image.suffix.lower()}"
    graph[ids["load"]]["inputs"]["image"] = input_filename
    validate_graph(graph, shot["characters"])
    out = Path(out).resolve()
    require(out.is_relative_to(root / "local" / "production" / plan["project_id"]), "job output outside project media tree")
    require(not out.exists(), "job directory already exists; never overwrite/re-submit silently")
    out.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".job-", dir=out.parent))
    try:
        input_path = temp / input_filename
        input_path.write_bytes(image.read_bytes())
        require(sha256_file(input_path) == entry["sha256"], "keyframe changed while snapshotting")
        write_json(temp / "workflow.json", graph)
        sources = {str(Path(p).resolve().relative_to(root)).replace("\\", "/"): sha256_file(p)
                   for p in (plan_path, approval_path, registry_path, workflow_path)}
        packet = {"schema_version": 5, "status": "PREPARED_NOT_SUBMITTED", "project_id": plan["project_id"],
                  "shot_id": sid, "seed": seed, "input_file": input_path.name,
                  "input_sha256": entry["sha256"], "workflow_sha256": sha256_file(temp/"workflow.json"),
                  "sources": sources, "created_at": datetime.now(timezone.utc).isoformat(),
                  "note": "Offline preparation only. No POST /prompt was sent."}
        write_json(temp / "job.json", packet)
        require(not out.exists(), "concurrent job writer detected")
        os.rename(temp, out)
        return packet
    finally:
        if temp.exists():
            import shutil
            shutil.rmtree(temp)


def queue(root, plan, manifest, registry):
    check_plan(plan)
    ready, blocked, static = [], [], []
    for shot in plan["shots"]:
        sid = shot["shot_id"]
        if shot["render_mode"] != "I2V" or shot["motion_tier"] not in {"M1", "M2"}:
            static.append(sid)
            continue
        try:
            _, entry, image = validate_keyframe(root, plan, manifest, registry, sid)
            ready.append({"shot_id": sid, "image": str(image), "sha256": entry["sha256"]})
        except ContractError as exc:
            blocked.append({"shot_id": sid, "reason": str(exc)})
    return {"ready": ready, "blocked": blocked, "static": static, "production_ready": bool(ready) and not blocked}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["plan", "queue", "guard", "prepare"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--approval")
    parser.add_argument("--registry")
    parser.add_argument("--workflow")
    parser.add_argument("--shot")
    parser.add_argument("--seed", type=int, default=2026100501)
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        root = Path(args.root).resolve()
        p = relative_file(root, args.plan)
        plan = read_json(p)
        report = {"contract_ok": True, **check_plan(plan)}
        if args.command != "plan":
            a, r = relative_file(root, args.approval), relative_file(root, args.registry)
            if args.command == "queue":
                report.update(queue(root, plan, read_json(a), read_json(r)))
            else:
                s, _, _ = validate_keyframe(root, plan, read_json(a), read_json(r), args.shot)
                require(s["render_mode"] == "I2V" and s["motion_tier"] in {"M1", "M2"}, "static/high-risk shot blocked")
                w = relative_file(root, args.workflow)
                validate_graph(read_json(w), s["characters"])
                if args.command == "prepare":
                    report.update(prepare(root, p, a, r, w, args.shot, args.seed, relative_file(root, args.out)))
                else:
                    report["production_guard_passed"] = True
        if args.out and args.command != "prepare":
            destination = relative_file(root, args.out)
            require(not destination.exists(), "report output exists")
            write_json(destination, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if args.command != "queue" or report["production_ready"] else 2
    except (ContractError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"contract_ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
