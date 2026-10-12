#!/usr/bin/env python3
"""Create a source-only FID1 media/hash/resource report without auto-approving visuals."""
from __future__ import annotations

import argparse
from datetime import datetime
from fractions import Fraction
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageOps

try:
    from .preproduction import FID1_NODE_CLASS_BY_STRATEGY, read_json, require, write_json
    from .sync_repo_media import safe as safe_project_path
except ImportError:
    from preproduction import FID1_NODE_CLASS_BY_STRATEGY, read_json, require, write_json
    from sync_repo_media import safe as safe_project_path


SCOPE = "T1_SOURCE_ONLY"
PROJECT = "T1_SOURCE_PILOT"


def validate_fid1_job_contract(job):
    contract = job.get("fid1_contract") if isinstance(job, dict) else None
    require(isinstance(contract, dict), "FID1 QA job contract is missing")
    expected_node = FID1_NODE_CLASS_BY_STRATEGY.get(contract.get("strategy"))
    require(expected_node is not None and contract.get("node_class") == expected_node,
            "FID1 QA strategy and node class do not match")
    return True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verified_run_output(root: Path | str, job_dir: Path | str, run_record=None):
    """Return the single run-record video after rechecking its confined current bytes."""
    root = Path(root).resolve(strict=True)
    directory = Path(job_dir).resolve(strict=True)
    require(directory.is_relative_to(root / "local" / "production" / PROJECT / "video"),
            "FID1 output job must stay inside the T1 source pilot")
    run_record = run_record or read_json(directory / "run_record.json")
    outputs = run_record.get("outputs")
    require(run_record.get("result") == "success" and isinstance(outputs, list) and len(outputs) == 1,
            "expected exactly one successful ComfyUI output")
    output_record = outputs[0]
    saved_path = output_record.get("saved_path")
    require(isinstance(saved_path, str) and saved_path, "run record has no saved output path")
    candidate = Path(saved_path)
    if not candidate.is_absolute():
        candidate = directory / candidate
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("recorded output path is outside the project") from exc
    output_path = safe_project_path(root, relative.as_posix())
    output_path = output_path.resolve(strict=True)
    media_dir = safe_project_path(root, (directory / "run_record_media").relative_to(root).as_posix())
    media_dir = media_dir.resolve(strict=True)
    require(output_path.is_file() and output_path.parent == media_dir,
            "recorded output must be a regular file directly inside this job's run_record_media")
    actual_sha = sha256_file(output_path)
    actual_bytes = output_path.stat().st_size
    require(actual_sha == output_record.get("sha256") and actual_bytes == output_record.get("bytes"),
            "current output bytes differ from the ComfyUI run-record receipt")
    return output_path, output_record


def parse_ffprobe_info(payload, profile):
    require(isinstance(payload, dict), "ffprobe response must be a JSON object")
    streams = payload.get("streams")
    require(isinstance(streams, list), "ffprobe response has no streams list")
    video = [stream for stream in streams if isinstance(stream, dict) and stream.get("width") and stream.get("height")]
    require(len(video) == 1, "expected exactly one video stream")
    stream = video[0]
    try:
        width, height = int(stream["width"]), int(stream["height"])
        frame_count = int(stream.get("nb_read_frames") or stream.get("nb_frames"))
        fps = Fraction(stream["avg_frame_rate"])
        duration = float(payload["format"]["duration"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"ffprobe fields are incomplete or invalid: {exc}") from exc
    require((width, height) == (profile["width"], profile["height"]), "video dimensions differ from frozen FID1 profile")
    require(frame_count == profile["frames"], "video frame count differs from frozen FID1 profile")
    require(fps == profile["fps"], "video fps differs from frozen FID1 profile")
    expected_duration = profile["frames"] / profile["fps"]
    require(abs(duration - expected_duration) <= 1 / profile["fps"], "video duration differs by more than one frame")
    return {
        "codec_name": stream.get("codec_name"),
        "width": width,
        "height": height,
        "frame_count": frame_count,
        "fps": int(fps),
        "duration_seconds": duration,
        "expected_duration_seconds": expected_duration,
        "contract_ok": True,
    }


def pending_visual_review():
    return {
        "full_playback": "PENDING",
        "identity": "PENDING",
        "costume": "PENDING",
        "limbs": "PENDING",
        "decision": "PENDING",
        "reviewer": None,
        "reviewed_at": None,
        "user_quote": None,
    }


def visual_review_template(job, output_sha256):
    return {
        "schema_version": 1,
        "scope": SCOPE,
        "shot_id": job["shot_id"],
        "profile_id": job["trial_profile"]["profile_id"],
        "output_sha256": output_sha256,
        "decision": "PENDING",
        "full_playback": "PENDING",
        "identity": "PENDING",
        "costume": "PENDING",
        "limbs": "PENDING",
        "reviewer": "",
        "user_quote": "",
        "recorded_at": "",
    }


def record_visual_review(root: Path | str, job_dir: Path | str, feedback_path: Path | str, apply=False):
    root=Path(root).resolve(strict=True)
    directory=Path(job_dir).resolve(strict=True)
    require(directory.is_relative_to(root/"local"/"production"/PROJECT/"video"),"review job must stay inside the T1 source pilot")
    report_path=directory/"qa"/"qa_report.json"
    require(report_path.is_file(),"FID1 QA report is missing")
    report=read_json(report_path)
    output_path, output_record = verified_run_output(root, directory)
    expected_output_path = output_path.relative_to(directory).as_posix()
    require(report.get("output",{}).get("path")==expected_output_path
            and report.get("output",{}).get("sha256")==output_record.get("sha256")
            and report.get("output",{}).get("bytes")==output_record.get("bytes"),
            "QA report is stale or does not match the current run-record output")
    feedback_file=Path(feedback_path).resolve(strict=True)
    require(feedback_file.is_relative_to(root/"local"/"review_evidence"),"human review evidence must be stored under local/review_evidence")
    review=read_json(feedback_file)
    required={"schema_version","scope","shot_id","profile_id","output_sha256","decision","full_playback",
              "identity","costume","limbs","reviewer","user_quote","recorded_at"}
    require(set(review)==required and review.get("schema_version")==1,"visual review fields/schema are invalid")
    require(review.get("scope")==SCOPE and review.get("shot_id")==report.get("shot_id")
            and review.get("profile_id")==report.get("profile_id"),"visual review belongs to another source trial")
    require(review.get("output_sha256")==report.get("output",{}).get("sha256"),"visual review is not bound to this output hash")
    require(review.get("reviewer")=="Jovi" and isinstance(review.get("user_quote"),str)
            and 0<len(review["user_quote"].strip())<=2048,"review requires Jovi's explicit words")
    try:
        recorded=datetime.fromisoformat(review["recorded_at"].replace("Z","+00:00"))
    except (TypeError,ValueError) as exc:
        raise ValueError("visual review timestamp must be ISO-8601 with timezone") from exc
    require(recorded.tzinfo is not None,"visual review timestamp must include timezone")
    allowed={"PASS","CHANGES_REQUIRED","NOT_RUN"}
    require(all(review.get(key) in allowed for key in ("full_playback","identity","costume","limbs")),
            "visual review statuses must be PASS, CHANGES_REQUIRED, or NOT_RUN")
    decision=review.get("decision")
    require(decision in {"ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL","CHANGES_REQUIRED"},"invalid visual review decision")
    if decision=="ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL":
        require(all(review[key]=="PASS" for key in ("full_playback","identity","costume","limbs")),
                "next source-only trial requires PASS for full playback, identity, costume, and limbs")
    else:
        require(any(review[key]!="PASS" for key in ("full_playback","identity","costume","limbs")),
                "CHANGES_REQUIRED needs at least one unresolved or failed visual criterion")

    raw=feedback_file.read_bytes()
    evidence_sha=hashlib.sha256(raw).hexdigest()
    evidence_name=f"FID1_{review['shot_id']}_{review['profile_id']}_{review['output_sha256'][:12]}_VISUAL_REVIEW.json"
    evidence_rel="local/review_evidence/"+evidence_name
    evidence_path=root/evidence_rel
    result={"mode":"DRY_RUN","decision":decision,"evidence_path":evidence_rel,"evidence_sha256":evidence_sha,
            "next_shot_gate":"OPEN_FOR_NEXT_SOURCE_ONLY_TRIAL" if decision=="ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL" else "BLOCKED_CHANGES_REQUIRED"}
    if not apply:
        return result
    require(not evidence_path.exists(),"visual review evidence already recorded; do not overwrite it")
    require(report.get("visual_review")==pending_visual_review(),"QA report already has a human review record")
    verified_run_output(root, directory)
    original_report_sha=sha256_file(report_path)
    evidence_path.parent.mkdir(parents=True,exist_ok=True)
    try:
        with evidence_path.open("xb") as stream:
            stream.write(raw)
        require(sha256_file(report_path)==original_report_sha,"QA report changed during review recording")
        verified_run_output(root, directory)
        report["visual_review"]={
            **{key:review[key] for key in ("full_playback","identity","costume","limbs","decision","reviewer","user_quote","recorded_at")},
            "evidence_path":evidence_rel,
            "evidence_sha256":evidence_sha,
        }
        report["next_shot_gate"]=result["next_shot_gate"]
        write_json(report_path,report)
    except Exception:
        if evidence_path.is_file() and sha256_file(evidence_path)==evidence_sha:
            evidence_path.unlink()
        raise
    return {**result,"mode":"APPLIED"}


def _contact_sheet(frames, target, columns, tile_width, label_height=28):
    with Image.open(frames[0]) as first:
        width, height = first.size
    tile_height = round(tile_width * height / width)
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * tile_width, rows * (tile_height + label_height)), "#111827")
    draw = ImageDraw.Draw(sheet)
    for index, frame_path in enumerate(frames):
        with Image.open(frame_path) as frame:
            frame = ImageOps.fit(frame.convert("RGB"), (tile_width, tile_height), method=Image.Resampling.LANCZOS)
            x = (index % columns) * tile_width
            y = (index // columns) * (tile_height + label_height)
            sheet.paste(frame, (x, y))
            draw.text((x + 6, y + tile_height + 5), f"frame {index + 1:02d}", fill="white")
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target, format="PNG")


def _review_page(job, report, output_relative):
    profile = job["trial_profile"]
    output_name = html.escape(output_relative.as_posix(), quote=True)
    first_last = "first_middle_last.png"
    all49 = "all49.png"
    return f"""<!doctype html>
<html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>FID1 T1_SOURCE_ONLY 试拍复审：{html.escape(job['shot_id'])}</title>
<style>body{{font:16px system-ui;max-width:1100px;margin:auto;padding:24px;color:#e5e7eb;background:#111827}} video{{max-width:100%;max-height:75vh}} img{{max-width:100%;border:1px solid #374151}} section{{margin:24px 0;padding:16px;border:1px solid #374151;border-radius:12px}} code{{overflow-wrap:anywhere}}</style>
<h1>{html.escape(job['shot_id'])} / {html.escape(profile['profile_id'])}</h1>
<p>范围：<strong>T1_SOURCE_ONLY</strong>。此页没有写入任何视觉批准。人工状态：身份、服装、肢体、完整播放均为 PENDING。</p>
<section><h2>完整视频</h2><video controls preload="metadata" src="{output_name}"></video><p>49 帧 / 24fps / {report['media']['width']}×{report['media']['height']} / {report['media']['duration_seconds']:.6f}s</p></section>
<section><h2>首帧、中间帧、末帧</h2><img src="{first_last}" alt="first, middle, last frames"></section>
<section><h2>全部 49 帧</h2><img src="{all49}" alt="all 49 decoded frames"></section>
<section><h2>复核材料</h2><ul><li>输入 SHA256: <code>{job['input_sha256']}</code></li><li>工作流 SHA256: <code>{job['workflow_sha256']}</code></li><li>输出 SHA256: <code>{report['output']['sha256']}</code></li></ul>
<p>请完整播放后逐项看：身份/侧脸几何、头饰与服装、手和四肢、背景运动与 ROI 接缝。可复制并填写同目录的 <code>visual_review_template.json</code> 放入 <code>local/review_evidence/</code>，再运行record-review命令。若不认可，结论应为 CHANGES_REQUIRED；不要自动扩展到其他镜头。</p></section>
</html>"""


def create_report(root: Path | str, job_dir: Path | str, ffprobe: str | None = None, ffmpeg: str | None = None):
    root = Path(root).resolve(strict=True)
    directory = Path(job_dir).resolve(strict=True)
    require(directory.is_relative_to(root / "local" / "production" / PROJECT / "video"), "QA job must be inside the T1 source pilot video tree")
    require(not (directory / "qa_report.json").exists() and not (directory / "qa").exists(), "QA output already exists; choose a new take")
    job = read_json(directory / "job.json")
    require(job.get("project_id") == PROJECT and job.get("purpose") == SCOPE
            and job.get("eligible_for_final_cut") is False, "QA only accepts isolated T1_SOURCE_ONLY jobs")
    validate_fid1_job_contract(job)
    run_record = read_json(directory / "run_record.json")
    require(run_record.get("result") == "success" and run_record.get("queued_new_job") is True
            and bool(run_record.get("prompt_id")), "run record does not prove a successful new ComfyUI execution")
    require(run_record.get("workflow_sha256") == job.get("workflow_sha256"), "run record workflow hash differs from prepared job")
    output_path, output_record = verified_run_output(root, directory, run_record)
    output_hash = output_record["sha256"]
    ffprobe = ffprobe or shutil.which("ffprobe")
    ffmpeg = ffmpeg or shutil.which("ffmpeg")
    require(ffprobe and ffmpeg, "ffprobe and ffmpeg are required to create FID1 media QA")
    probe_command = [ffprobe, "-v", "error", "-count_frames", "-select_streams", "v:0",
                     "-show_entries", "stream=codec_name,width,height,avg_frame_rate,nb_read_frames,nb_frames",
                     "-show_entries", "format=duration", "-of", "json", str(output_path)]
    probe = subprocess.run(probe_command, capture_output=True, text=True, check=False)
    require(probe.returncode == 0, "ffprobe failed: " + probe.stderr[-1200:])
    media = parse_ffprobe_info(json.loads(probe.stdout), job["trial_profile"])
    decode = subprocess.run([ffmpeg, "-v", "error", "-i", str(output_path), "-f", "null", "-"],
                            capture_output=True, text=True, check=False)
    require(decode.returncode == 0 and not decode.stderr.strip(), "full video decode reported errors: " + decode.stderr[-1200:])

    stage = Path(tempfile.mkdtemp(prefix=".fid1-qa-", dir=directory))
    try:
        all49_dir = stage / "all49"
        all49_dir.mkdir()
        extract = subprocess.run([ffmpeg, "-v", "error", "-i", str(output_path), "-vsync", "0", "-frames:v",
                                  str(job["trial_profile"]["frames"]), str(all49_dir / "frame_%02d.png")],
                                 capture_output=True, text=True, check=False)
        require(extract.returncode == 0, "all49 frame extraction failed: " + extract.stderr[-1200:])
        frames = sorted(all49_dir.glob("frame_*.png"))
        require(len(frames) == job["trial_profile"]["frames"], "all49 extraction did not return exactly 49 frames")
        for frame_path in frames:
            with Image.open(frame_path) as frame:
                require(frame.size == (media["width"], media["height"]), "decoded frame dimensions changed")
        _contact_sheet(frames, stage / "all49.png", columns=7, tile_width=160)
        _contact_sheet([frames[0], frames[len(frames) // 2], frames[-1]], stage / "first_middle_last.png", columns=3, tile_width=320)
        relative_video = Path(os.path.relpath(output_path, directory / "qa"))
        report = {
            "schema_version": 1,
            "scope": SCOPE,
            "shot_id": job["shot_id"],
            "profile_id": job["trial_profile"]["profile_id"],
            "runtime_success": True,
            "media_contract_ok": True,
            "full_decode": "PASS",
            "human_full_playback": "PENDING",
            "input": {"path": job["input_file"], "sha256": job["input_sha256"]},
            "workflow_sha256": job["workflow_sha256"],
            "seed": job["seed"],
            "model": "Wan2.2-TI2V-5B",
            "media": media,
            "output": {"path": str(output_path.relative_to(directory)).replace("\\", "/"),
                       "bytes": output_path.stat().st_size, "sha256": output_hash},
            "resources": run_record.get("resources"),
            "frames": {"count": len(frames), "all49_contact_sheet": "qa/all49.png",
                       "first_middle_last": "qa/first_middle_last.png"},
            "visual_review": pending_visual_review(),
            "next_shot_gate": "WAITING_JOVI_VISUAL_ACCEPTANCE",
        }
        write_json(stage / "qa_report.json", report)
        write_json(stage / "visual_review_template.json", visual_review_template(job, output_hash))
        (stage / "review.html").write_text(_review_page(job, report, relative_video), encoding="utf-8")
        os.rename(stage, directory / "qa")
        stage = None
        return report
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage, ignore_errors=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("create", "record-review"), nargs="?", default="create")
    parser.add_argument("--root", default=".")
    parser.add_argument("--job-dir", required=True)
    parser.add_argument("--ffprobe")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--feedback")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command=="record-review":
            require(bool(args.feedback),"--feedback is required for record-review")
            report=record_visual_review(args.root,args.job_dir,args.feedback,args.apply)
        else:
            require(not args.apply and not args.feedback,"--feedback/--apply only apply to record-review")
            report = create_report(args.root, args.job_dir, args.ffprobe, args.ffmpeg)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "visual_accepted": False}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
