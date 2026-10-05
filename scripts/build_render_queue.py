#!/usr/bin/env python3
"""Build a render queue from user-approved shots only."""

from __future__ import annotations

import argparse, json
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True)
    p.add_argument("--project-root",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()

    data=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    root=Path(args.project_root)
    queue=[]
    skipped=[]

    for shot_id,shot in (data.get("shots") or {}).items():
        if shot.get("status") not in {"USER_APPROVED","PRODUCTION_READY"}:
            skipped.append({"shot":shot_id,"reason":"not approved"})
            continue
        name=shot.get("approved_keyframe")
        if not name:
            skipped.append({"shot":shot_id,"reason":"approved keyframe missing"})
            continue
        candidates=list(root.rglob(name))
        if len(candidates)!=1:
            skipped.append({"shot":shot_id,"reason":f"expected exactly one file named {name}, found {len(candidates)}"})
            continue
        queue.append({
            "shot_id":shot_id,
            "image":str(candidates[0]),
            "sha256":shot.get("sha256"),
            "identity_refs":shot.get("identity_refs"),
            "costume_refs":shot.get("costume_refs"),
            "motion_tier":shot.get("motion_tier"),
            "status":"READY_FOR_GUARD"
        })

    payload={"ready":queue,"skipped":skipped}
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"ready":len(queue),"skipped":len(skipped),"out":str(out)},ensure_ascii=False))

if __name__=="__main__":
    main()
