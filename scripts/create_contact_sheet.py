#!/usr/bin/env python3
"""Create a labeled contact sheet from local character references.

This is a review aid only. It never changes approval state.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont

EXTS={".png",".jpg",".jpeg",".webp"}

def load_font(size:int):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--cols", type=int, default=4)
    p.add_argument("--cell-w", type=int, default=360)
    p.add_argument("--cell-h", type=int, default=460)
    args=p.parse_args()

    root=Path(args.input)
    files=[x for x in sorted(root.rglob("*")) if x.is_file() and x.suffix.lower() in EXTS]
    if not files:
        raise SystemExit("no images found")

    label_h=42
    rows=(len(files)+args.cols-1)//args.cols
    sheet=Image.new("RGB",(args.cols*args.cell_w,rows*(args.cell_h+label_h)),"white")
    draw=ImageDraw.Draw(sheet)
    font=load_font(18)

    for idx,path in enumerate(files):
        im=Image.open(path).convert("RGB")
        fitted=ImageOps.contain(im,(args.cell_w,args.cell_h))
        x=(idx%args.cols)*args.cell_w
        y=(idx//args.cols)*(args.cell_h+label_h)
        px=x+(args.cell_w-fitted.width)//2
        py=y+(args.cell_h-fitted.height)//2
        sheet.paste(fitted,(px,py))
        label=path.relative_to(root).as_posix()
        draw.text((x+8,y+args.cell_h+10),label,fill="black",font=font)

    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(out,quality=95)
    print(out)

if __name__=="__main__":
    main()
