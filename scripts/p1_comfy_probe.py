#!/usr/bin/env python3
"""P1A minimal ComfyUI probe.

Health-check a running server, read an API workflow, inject prompt, seed, size,
frames, and an image when the graph already has LoadImage, submit one job, wait,
download the output, and write a metadata record.

This file does not start ComfyUI. It does not install models. It does not add
nodes to a graph that has no image input. It is not an episode manager,
scheduler, LoRA loader, MuseTalk, TTS, UI, or database.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SHANGHAI = ZoneInfo("Asia/Shanghai")
POLL_SECONDS = 2.0
SAMPLE_SECONDS = 5.0
WAIT_SECONDS = 7200.0
WAN_LATENT = "Wan22ImageToVideoLatent"
IMAGE_NODES = {"LoadImage", "LoadImageMask"}
SAMPLER_NODES = {"KSampler", "KSamplerAdvanced"}


class ProbeError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(SHANGHAI).isoformat(timespec="milliseconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def request_json(method: str, url: str, payload: dict | None = None, timeout: float = 60):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            status = resp.status
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ProbeError(f"HTTP {exc.code} {url}: {body[:2000]}") from exc
    except urllib.error.URLError as exc:
        raise ProbeError(f"request failed {url}: {exc.reason}") from exc
    except (TimeoutError, OSError) as exc:
        raise ProbeError(f"request failed {url}: {exc}") from exc
    if not raw:
        return status, None
    return status, json.loads(raw.decode("utf-8"))


def node_title(node: dict) -> str:
    meta = node.get("_meta") or {}
    if isinstance(meta, dict):
        return str(meta.get("title") or "")
    return ""


def load_api_workflow(path: Path) -> tuple[bytes, dict]:
    raw = path.read_bytes()
    try:
        graph = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ProbeError(f"workflow is not UTF-8 JSON: {exc}") from exc
    if not isinstance(graph, dict):
        raise ProbeError("workflow JSON must be an object")
    if "nodes" in graph and "links" in graph:
        raise ProbeError("workflow is ComfyUI UI format, not an API prompt dict")
    if not any(isinstance(node, dict) and "class_type" in node for node in graph.values()):
        raise ProbeError("workflow has no API nodes")
    return raw, graph


def text_nodes(graph: dict, role: str) -> list[str]:
    found = []
    for node_id, node in graph.items():
        if not isinstance(node, dict) or node.get("class_type") != "CLIPTextEncode":
            continue
        if role in node_title(node).lower():
            found.append(str(node_id))
    return found


def inject(graph: dict, args: argparse.Namespace, uploaded_name: str | None) -> list[dict]:
    notes = []
    if args.positive is not None:
        found = text_nodes(graph, "positive")
        if len(found) != 1:
            raise ProbeError(f"--positive needs exactly one CLIPTextEncode titled positive, found {found}")
        graph[found[0]]["inputs"]["text"] = args.positive
        notes.append({"node": found[0], "field": "text", "role": "positive"})
    if args.negative is not None:
        found = text_nodes(graph, "negative")
        if len(found) != 1:
            raise ProbeError(f"--negative needs exactly one CLIPTextEncode titled negative, found {found}")
        graph[found[0]]["inputs"]["text"] = args.negative
        notes.append({"node": found[0], "field": "text", "role": "negative"})
    if args.seed is not None:
        seeded = []
        for node_id, node in graph.items():
            if not isinstance(node, dict) or node.get("class_type") not in SAMPLER_NODES:
                continue
            inputs = node.get("inputs") or {}
            key = "seed" if "seed" in inputs else ("noise_seed" if "noise_seed" in inputs else None)
            if key is None or isinstance(inputs.get(key), list):
                continue
            inputs[key] = int(args.seed)
            seeded.append(str(node_id))
        if not seeded:
            raise ProbeError("--seed found no integer KSampler seed/noise_seed")
        notes.append({"nodes": seeded, "field": "seed"})
    if args.width is not None or args.height is not None or args.frames is not None:
        size_ids = []
        for node_id, node in graph.items():
            if not isinstance(node, dict):
                continue
            inputs = node.get("inputs") or {}
            if not isinstance(inputs, dict):
                continue
            has_frames = isinstance(inputs.get("length"), int) or isinstance(inputs.get("frames"), int)
            if isinstance(inputs.get("width"), int) and isinstance(inputs.get("height"), int) and has_frames:
                size_ids.append(str(node_id))
        if len(size_ids) != 1:
            raise ProbeError(f"width/height/frames need exactly one latent size node, found {size_ids}")
        node = graph[size_ids[0]]
        inputs = node["inputs"]
        if args.width is not None:
            if node.get("class_type") == WAN_LATENT and int(args.width) % 32 != 0:
                raise ProbeError("Wan22ImageToVideoLatent width must be a multiple of 32")
            inputs["width"] = int(args.width)
        if args.height is not None:
            if node.get("class_type") == WAN_LATENT and int(args.height) % 32 != 0:
                raise ProbeError("Wan22ImageToVideoLatent height must be a multiple of 32")
            inputs["height"] = int(args.height)
        if args.frames is not None:
            key = "length" if "length" in inputs else "frames"
            frames = int(args.frames)
            if node.get("class_type") == WAN_LATENT and (frames - 1) % 4 != 0:
                raise ProbeError("Wan22ImageToVideoLatent frames must satisfy (frames-1) divisible by 4")
            inputs[key] = frames
        notes.append({"node": size_ids[0], "class_type": node.get("class_type"), "field": "width/height/frames"})
    if args.image:
        loaders = [
            str(node_id)
            for node_id, node in graph.items()
            if isinstance(node, dict) and node.get("class_type") in IMAGE_NODES
        ]
        if not loaders:
            raise ProbeError(
                "workflow has no LoadImage; refusing to add a node or wire start_image"
            )
        if not uploaded_name:
            raise ProbeError("image upload did not return a filename")
        for node_id in loaders:
            graph[node_id]["inputs"]["image"] = uploaded_name
        notes.append({"nodes": loaders, "field": "image", "uploaded_name": uploaded_name})
    return notes


def upload_image(base: str, path: Path) -> str:
    if not path.is_file():
        raise ProbeError(f"image not found: {path}")
    boundary = uuid.uuid4().hex
    filename = path.name
    file_bytes = path.read_bytes()
    chunks = [
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode(),
        b"Content-Type: application/octet-stream\r\n\r\n",
        file_bytes,
        f"\r\n--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="overwrite"\r\n\r\ntrue\r\n',
        f"--{boundary}\r\n".encode(),
        b'Content-Disposition: form-data; name="type"\r\n\r\ninput\r\n',
        f"--{boundary}--\r\n".encode(),
    ]
    body = b"".join(chunks)
    req = urllib.request.Request(
        base + "/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ProbeError(f"image upload failed HTTP {exc.code}: {detail[:2000]}") from exc
    except urllib.error.URLError as exc:
        raise ProbeError(f"image upload failed: {exc.reason}") from exc
    name = payload.get("name")
    if not name:
        raise ProbeError(f"image upload response missing name: {payload}")
    return str(name)


def sample_ram() -> dict:
    if sys.platform != "win32":
        return {"ram_error": f"unsupported platform {sys.platform}"}

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    if not ok:
        return {"ram_error": "GlobalMemoryStatusEx failed"}
    return {
        "ram_load_percent": int(stat.dwMemoryLoad),
        "ram_total_bytes": int(stat.ullTotalPhys),
        "ram_avail_bytes": int(stat.ullAvailPhys),
        "pagefile_total_bytes": int(stat.ullTotalPageFile),
        "pagefile_avail_bytes": int(stat.ullAvailPageFile),
    }


def sample_gpu() -> dict:
    exe = shutil.which("nvidia-smi")
    if not exe:
        return {"gpu_error": "nvidia-smi not on PATH"}
    try:
        done = subprocess.run(
            [
                exe,
                "--query-gpu=name,memory.used,memory.total,driver_version,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"gpu_error": str(exc)}
    if done.returncode != 0:
        return {"gpu_error": (done.stderr or done.stdout or "nvidia-smi failed").strip()[:500]}
    line = (done.stdout or "").strip().splitlines()
    if not line:
        return {"gpu_error": "nvidia-smi returned no rows"}
    parts = [part.strip() for part in line[0].split(",")]
    if len(parts) < 5:
        return {"gpu_error": f"unexpected nvidia-smi row: {line[0]}"}
    try:
        used = int(parts[1])
        total = int(parts[2])
        util = int(parts[4])
    except ValueError:
        return {"gpu_error": f"non-integer nvidia-smi row: {line[0]}"}
    return {
        "gpu_name": parts[0],
        "gpu_memory_used_mib": used,
        "gpu_memory_total_mib": total,
        "driver_version": parts[3],
        "gpu_utilization_percent": util,
    }


class ResourceSampler:
    def __init__(self, base: str):
        self.base = base
        self.samples: list[dict] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, name="p1-comfy-probe-sampler", daemon=True)

    def start(self) -> None:
        self.samples.append(self._safe_sample())
        self._thread.start()

    def finish(self) -> None:
        self._stop.set()
        self._thread.join(timeout=20)
        self.samples.append(self._safe_sample())

    def sample(self) -> dict:
        # nvidia-smi and Win32 memory only. Do not poll /system_stats while a
        # job is running: ComfyUI answers that on the same thread as inference.
        row = {"at": now_iso()}
        row.update(sample_gpu())
        row.update(sample_ram())
        return row

    def _safe_sample(self) -> dict:
        try:
            return self.sample()
        except Exception as exc:  # noqa: BLE001 ? sampling must not abort the job
            return {"at": now_iso(), "sample_error": f"{type(exc).__name__}: {exc}"}

    def _loop(self) -> None:
        while not self._stop.wait(SAMPLE_SECONDS):
            self.samples.append(self._safe_sample())


def summarize_samples(samples: list[dict]) -> dict:
    used = [row["gpu_memory_used_mib"] for row in samples if isinstance(row.get("gpu_memory_used_mib"), int)]
    avail = [row["ram_avail_bytes"] for row in samples if isinstance(row.get("ram_avail_bytes"), int)]
    free = [row["comfy_vram_free_bytes"] for row in samples if isinstance(row.get("comfy_vram_free_bytes"), int)]
    return {
        "sample_count": len(samples),
        "sample_interval_seconds": SAMPLE_SECONDS,
        "nvidia_smi_memory_used_mib_first": used[0] if used else None,
        "nvidia_smi_memory_used_mib_peak": max(used) if used else None,
        "nvidia_smi_memory_used_mib_last": used[-1] if used else None,
        "ram_avail_bytes_min": min(avail) if avail else None,
        "ram_total_bytes": next((row.get("ram_total_bytes") for row in samples if row.get("ram_total_bytes")), None),
        "comfy_vram_free_bytes_min": min(free) if free else None,
        "note": "nvidia-smi memory.used is a sample peak, not a continuous hardware maximum",
    }


def message_timestamp(item: dict, name: str):
    status = item.get("status") or {}
    for message in status.get("messages") or []:
        if isinstance(message, list) and len(message) >= 2 and message[0] == name and isinstance(message[1], dict):
            return message[1].get("timestamp")
    return None


def output_files(item: dict) -> list[dict]:
    found = []
    outputs = item.get("outputs") or {}
    if not isinstance(outputs, dict):
        return found
    for node_id, node_out in outputs.items():
        if not isinstance(node_out, dict):
            continue
        for key in ("images", "gifs", "videos"):
            for entry in node_out.get(key) or []:
                if isinstance(entry, dict) and entry.get("filename"):
                    found.append({"node": str(node_id), "key": key, **entry})
    return found


def download_output(base: str, entry: dict, dest_dir: Path) -> dict:
    filename = Path(str(entry["filename"])).name
    subfolder = str(entry.get("subfolder") or "")
    file_type = str(entry.get("type") or "output")
    query = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": file_type})
    req = urllib.request.Request(base + "/view?" + query)
    dest = dest_dir / filename
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ProbeError(f"download failed HTTP {exc.code} {filename}: {detail[:1000]}") from exc
    except urllib.error.URLError as exc:
        raise ProbeError(f"download failed {filename}: {exc.reason}") from exc
    dest.write_bytes(data)
    return {
        "node": entry.get("node"),
        "filename": filename,
        "subfolder": subfolder,
        "type": file_type,
        "saved_path": str(dest),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def wait_for_history(base: str, prompt_id: str) -> dict:
    deadline = time.monotonic() + WAIT_SECONDS
    last_error = None
    while time.monotonic() < deadline:
        try:
            _status, hist = request_json("GET", base + "/history/" + urllib.parse.quote(prompt_id), timeout=30)
            last_error = None
        except ProbeError as exc:
            last_error = str(exc)
            time.sleep(POLL_SECONDS)
            continue
        item = hist.get(prompt_id) if isinstance(hist, dict) else None
        if isinstance(item, dict):
            status = item.get("status") or {}
            if status.get("completed") or status.get("status_str") in {"success", "error"}:
                return item
        time.sleep(POLL_SECONDS)
    raise ProbeError(f"timed out after {WAIT_SECONDS:.0f}s waiting for {prompt_id}; last error: {last_error}")


def write_record(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



def history_graph(item: dict):
    prompt = item.get("prompt")
    if isinstance(prompt, list) and len(prompt) >= 3 and isinstance(prompt[2], dict):
        return prompt[2]
    return None


def repo_root_from(path: Path) -> Path:
    resolved = path.resolve()
    for parent in (resolved.parent, *resolved.parents):
        if (parent / "PROJECT_STATE.md").is_file() and (parent / "scripts").is_dir():
            return parent
    return Path.cwd()


def apply_finished_item(base: str, item: dict, record: dict, media_dir: Path) -> None:
    record["history_status"] = item.get("status")
    start_ms = message_timestamp(item, "execution_start")
    end_ms = message_timestamp(item, "execution_success") or message_timestamp(item, "execution_error")
    record["comfy_execution_start_ms"] = start_ms
    record["comfy_execution_end_ms"] = end_ms
    if isinstance(start_ms, (int, float)) and isinstance(end_ms, (int, float)):
        record["comfy_elapsed_seconds"] = (end_ms - start_ms) / 1000.0
        record["comfy_execution_start"] = datetime.fromtimestamp(start_ms / 1000.0, SHANGHAI).isoformat(timespec="milliseconds")
        record["comfy_execution_end"] = datetime.fromtimestamp(end_ms / 1000.0, SHANGHAI).isoformat(timespec="milliseconds")
    cached = []
    status = item.get("status") or {}
    for message in status.get("messages") or []:
        if isinstance(message, list) and message and message[0] == "execution_cached" and isinstance(message[1], dict):
            nodes = message[1].get("nodes")
            if isinstance(nodes, list):
                cached = [str(node) for node in nodes]
    record["execution_cached_nodes"] = cached
    if status.get("status_str") != "success":
        raise ProbeError(f"execution status is {status.get('status_str')}")
    media_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for entry in output_files(item):
        saved.append(download_output(base, entry, media_dir))
    if not saved:
        raise ProbeError("execution succeeded but history listed no output file")
    record["outputs"] = saved


def post_run_snapshot(base: str) -> dict:
    """One nvidia-smi plus Win32 memory reading after a job already finished.

    This is not a peak and must not be summarized as one.
    """
    row = ResourceSampler(base).sample()
    row["label"] = "post_run_snapshot"
    used = row.get("gpu_memory_used_mib")
    return {
        "sample_kind": "post_run_snapshot",
        "sample_count": 1,
        "sample_interval_seconds": None,
        "nvidia_smi_memory_used_mib": used if isinstance(used, int) else None,
        "nvidia_smi_memory_used_mib_peak": None,
        "note": "Single nvidia-smi and Win32 memory sample taken after the prompt had already finished. Not a peak and not a during-run series.",
        "sample": row,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe one ComfyUI API workflow and record the run.")
    parser.add_argument("--url", required=True, help="ComfyUI base URL, for example http://127.0.0.1:8188")
    parser.add_argument("--workflow", required=True, help="API workflow JSON path")
    parser.add_argument("--image", default=None, help="Image to upload into an existing LoadImage node")
    parser.add_argument("--positive", default=None, help="Replacement positive prompt")
    parser.add_argument("--negative", default=None, help="Replacement negative prompt")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--height", type=int, default=None)
    parser.add_argument("--frames", type=int, default=None)
    parser.add_argument("--record", required=True, help="Path of the JSON metadata record to write")
    parser.add_argument(
        "--from-prompt-id",
        default=None,
        help="Write --record from an already-finished prompt id (GET /history, download, one post-run nvidia-smi snapshot). Does not POST /prompt.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    base = args.url.rstrip("/")
    record_path = Path(args.record)
    workflow_path = Path(args.workflow)
    record: dict = {
        "tool": "scripts/p1_comfy_probe.py",
        "started_at": now_iso(),
        "url": base,
        "workflow": str(workflow_path),
        "args": {
            "image": args.image,
            "positive": args.positive,
            "negative": args.negative,
            "seed": args.seed,
            "width": args.width,
            "height": args.height,
            "frames": args.frames,
            "from_prompt_id": args.from_prompt_id,
        },
        "mode": None,
        "queued_new_job": None,
        "result": None,
        "error": None,
    }
    sampler: ResourceSampler | None = None
    exit_code = 1
    try:
        stats_status, stats = request_json("GET", base + "/system_stats", timeout=20)
        record["health"] = {
            "http_status": stats_status,
            "comfyui_version": (stats.get("system") or {}).get("comfyui_version"),
            "pytorch_version": (stats.get("system") or {}).get("pytorch_version"),
            "python_version": (stats.get("system") or {}).get("python_version"),
            "ram_total": (stats.get("system") or {}).get("ram_total"),
            "ram_free": (stats.get("system") or {}).get("ram_free"),
            "devices": stats.get("devices"),
        }
        _status, queue = request_json("GET", base + "/queue", timeout=20)
        running = queue.get("queue_running") or []
        pending = queue.get("queue_pending") or []
        record["queue_before"] = {"running": len(running), "pending": len(pending)}
        raw, graph = load_api_workflow(workflow_path)
        record["workflow_sha256"] = sha256_bytes(raw)
        record["workflow_bytes"] = len(raw)
        if args.from_prompt_id:
            if running or pending:
                record["queue_note"] = "queue was not empty; this mode does not submit, so it was left untouched"
            record["mode"] = "record_existing_prompt"
            record["queued_new_job"] = False
            prompt_id = str(args.from_prompt_id)
            record["prompt_id"] = prompt_id
            _status, hist = request_json("GET", base + "/history/" + urllib.parse.quote(prompt_id), timeout=30)
            item = hist.get(prompt_id) if isinstance(hist, dict) else None
            if not isinstance(item, dict):
                item = wait_for_history(base, prompt_id)
                record["history_wait"] = "polled until the history item appeared; no prompt was submitted by this process"
            else:
                status = item.get("status") or {}
                terminal = bool(status.get("completed") or status.get("status_str") in {"success", "error"})
                if not terminal:
                    item = wait_for_history(base, prompt_id)
                    record["history_wait"] = "polled until a terminal status; no prompt was submitted by this process"
                else:
                    record["history_wait"] = "history already terminal on the first GET; no new submit; wait loop not used"
            hist_graph = history_graph(item)
            record["workflow_matches_history_prompt"] = hist_graph == graph
            if hist_graph != graph:
                raise ProbeError("workflow file does not equal history prompt[2]; refusing to record them as the same run")
            prompt_meta = item.get("prompt")
            if isinstance(prompt_meta, list) and len(prompt_meta) >= 4 and isinstance(prompt_meta[3], dict):
                record["history_client_id"] = prompt_meta[3].get("client_id")
                record["history_create_time_ms"] = prompt_meta[3].get("create_time")
            media_dir = repo_root_from(workflow_path) / "local" / "p1_probe_media" / record_path.stem
            apply_finished_item(base, item, record, media_dir)
            record["resources"] = post_run_snapshot(base)
            record["result"] = "success"
            exit_code = 0
        else:
            if running or pending:
                raise ProbeError("ComfyUI queue is not empty; refusing to submit a second job")
            uploaded = upload_image(base, Path(args.image)) if args.image else None
            graph = deepcopy(graph)
            record["injection"] = inject(graph, args, uploaded)
            submitted = json.dumps(graph, ensure_ascii=False).encode("utf-8")
            record["submitted_graph_sha256"] = sha256_bytes(submitted)
            client_id = str(uuid.uuid4())
            record["client_id"] = client_id
            sampler = ResourceSampler(base)
            sampler.start()
            record["submit_started_at"] = now_iso()
            _status, prompt_resp = request_json(
                "POST",
                base + "/prompt",
                {"prompt": graph, "client_id": client_id},
                timeout=60,
            )
            record["prompt_response"] = prompt_resp
            node_errors = prompt_resp.get("node_errors") if isinstance(prompt_resp, dict) else None
            if node_errors:
                raise ProbeError(f"prompt rejected with node_errors: {json.dumps(node_errors)[:2000]}")
            prompt_id = prompt_resp.get("prompt_id") if isinstance(prompt_resp, dict) else None
            if not prompt_id:
                raise ProbeError(f"prompt response missing prompt_id: {prompt_resp}")
            record["prompt_id"] = prompt_id
            item = wait_for_history(base, prompt_id)
            record["history_status"] = item.get("status")
            start_ms = message_timestamp(item, "execution_start")
            end_ms = message_timestamp(item, "execution_success") or message_timestamp(item, "execution_error")
            record["comfy_execution_start_ms"] = start_ms
            record["comfy_execution_end_ms"] = end_ms
            if isinstance(start_ms, (int, float)) and isinstance(end_ms, (int, float)):
                record["comfy_elapsed_seconds"] = (end_ms - start_ms) / 1000.0
            status = item.get("status") or {}
            if status.get("status_str") != "success":
                raise ProbeError(f"execution status is {status.get('status_str')}")
            media_dir = record_path.parent / (record_path.stem + "_media")
            media_dir.mkdir(parents=True, exist_ok=True)
            saved = []
            for entry in output_files(item):
                saved.append(download_output(base, entry, media_dir))
            if not saved:
                raise ProbeError("execution succeeded but history listed no output file")
            record["outputs"] = saved
            record["mode"] = "submit"
            record["queued_new_job"] = True
            record["result"] = "success"
            exit_code = 0
    except ProbeError as exc:
        record["result"] = "error"
        record["error"] = str(exc)
        exit_code = 1
    except Exception as exc:  # noqa: BLE001 — record unexpected failures instead of losing them
        record["result"] = "error"
        record["error"] = f"{type(exc).__name__}: {exc}"
        exit_code = 1
    finally:
        if sampler is not None:
            sampler.finish()
            record["samples"] = sampler.samples
            record["resources"] = summarize_samples(sampler.samples)
        record["finished_at"] = now_iso()
        try:
            write_record(record_path, record)
        except OSError as exc:
            print(f"failed to write record: {exc}", file=sys.stderr)
            record["_write_failed"] = str(exc)
    if record.get("_write_failed"):
        return 1
    if record.get("prompt_id"):
        outputs = record.get("outputs") or []
        saved_path = outputs[0]["saved_path"] if outputs else ""
        elapsed = record.get("comfy_elapsed_seconds")
        resources = record.get("resources") or {}
        print(f"prompt_id={record['prompt_id']}")
        print(f"saved_path={saved_path}")
        print(f"elapsed_seconds={elapsed}")
        print(f"queued_new_job={record.get('queued_new_job')}")
        if resources.get("sample_kind") == "post_run_snapshot":
            print(f"post_run_vram_mib={resources.get('nvidia_smi_memory_used_mib')}")
            print("peak_vram_mib=not_sampled")
        else:
            print(f"peak_vram_mib={resources.get('nvidia_smi_memory_used_mib_peak')}")
    print(f"record={record_path}")
    print(f"result={record['result']}")
    if record.get("error"):
        print(f"error={record['error']}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
