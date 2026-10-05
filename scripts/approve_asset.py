#!/usr/bin/env python3
"""Write one explicit user approval into an approval manifest.

This tool is intentionally narrow: it cannot infer approval.
The caller must provide --user-confirmed YES and the exact file to approve.
"""

from __future__ import annotations

import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--shot",required=True)
    p.add_argument("--image",required=True)
    p.add_argument("--user-confirmed",required=True)
    p.add_argument("--daiyu-ref",action="append",default=[])
    p.add_argument("--wukong-ref",action="append",default=[])
    p.add_argument("--daiyu-costume")
    p.add_argument("--wukong-costume")
    args=p.parse_args()

    if args.user_confirmed!="YES":
        raise SystemExit("refusing approval: --user-confirmed must be exactly YES")

    manifest_path=Path(args.manifest)
    image=Path(args.image)
    if not manifest_path.is_file():
        raise SystemExit("manifest not found")
    if not image.is_file():
        raise SystemExit("image not found")

    data=json.loads(manifest_path.read_text(encoding="utf-8"))
    shots=data.get("shots") or {}
    if args.shot not in shots:
        raise SystemExit(f"shot {args.shot} not in manifest")

    shot=shots[args.shot]
    shot["status"]="USER_APPROVED"
    shot["approved_keyframe"]=image.name
    shot["sha256"]=sha256_file(image)
    shot["identity_refs"]={"DAIYU":args.daiyu_ref,"WUKONG":args.wukong_ref}
    shot["costume_refs"]={"DAIYU":args.daiyu_costume,"WUKONG":args.wukong_costume}
    shot["approved_by_user"]=True
    shot["approved_at"]=datetime.now(timezone.utc).isoformat()

    manifest_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"shot":args.shot,"status":"USER_APPROVED","sha256":shot["sha256"]},ensure_ascii=False))

if __name__=="__main__":
    main()
