#!/usr/bin/env python3
"""CPU-only labeled reference review sequence. Never a production episode export."""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from preproduction import checked_asset, read_json, require, write_json


def render_review(root, registry, group, output, seconds=2, width=720, height=1280):
    require(width % 2 == 0 and height % 2 == 0 and width >= 160 and height >= 240, 'invalid review dimensions')
    require(type(seconds) is int and seconds > 0, 'duration must be positive whole seconds')
    exe = shutil.which('ffmpeg'); require(exe, 'ffmpeg not installed')
    selected = [(k,v) for k,v in registry['assets'].items() if v.get('group') == group]
    require(selected, 'empty review group')
    output = Path(output).resolve(); require(not output.exists(), 'review output exists; refusing overwrite')
    inputs = [(aid, a, checked_asset(root, a['path'], a['sha256'])) for aid,a in selected]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='reference-review-', dir=output.parent) as tmp:
        tmp = Path(tmp); listing=[]
        for idx,(aid,asset,path) in enumerate(inputs):
            canvas = Image.new('RGB',(width,height),(24,24,24))
            with Image.open(path) as im:
                im = ImageOps.exif_transpose(im).convert('RGB')
                im = ImageOps.contain(im,(width,height-100))
                canvas.paste(im,((width-im.width)//2,70+(height-100-im.height)//2))
            draw = ImageDraw.Draw(canvas)
            try:
                font = ImageFont.load_default(size=max(11,width//36))
            except TypeError:  # Pillow 10.0 lacks the size keyword.
                font = ImageFont.load_default()
            draw.text((10,10),'REFERENCE REVIEW | NOT EP001',font=font,fill='white')
            draw.text((10,37),f'{aid} | CANDIDATE',font=font,fill='white')
            filename=f'{idx:03}.png';canvas.save(tmp/filename)
            listing.extend([f"file '{filename}'",f'duration {seconds}'])
        listing.append(f"file '{len(inputs)-1:03}.png'")
        (tmp/'input.ffconcat').write_text('\n'.join(listing)+'\n',encoding='utf-8')
        command=[exe,'-hide_banner','-loglevel','error','-n','-f','concat','-safe','1','-i',str(tmp/'input.ffconcat'),
                 '-vf','fps=24,format=yuv420p','-t',str(len(inputs)*seconds),'-an','-c:v','libx264',
                 '-threads','2','-preset','fast','-crf','22','-movflags','+faststart',str(output)]
        subprocess.run(command,check=True,capture_output=True)
    report={'status':'REFERENCE_REVIEW_ONLY','group':group,'asset_count':len(inputs),
            'fps':24,'seconds':len(inputs)*seconds,'frames_expected':len(inputs)*seconds*24,
            'source_hashes':{aid:a['sha256'] for aid,a,_ in inputs},'output':str(output),
            'note':'Static sequencing, no I2V, no 3D model or identity validation claimed.'}
    write_json(output.with_suffix('.json'),report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default='.')
    p.add_argument('--registry',default='assets/registry/generated_assets_v5.json')
    p.add_argument('--group',default='REFBATCH02')
    p.add_argument('--out',required=True)
    a=p.parse_args()
    try:
        r=render_review(a.root,read_json(Path(a.root)/a.registry),a.group,a.out)
        print(json.dumps(r,ensure_ascii=False,indent=2));return 0
    except Exception as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False));return 2
if __name__=='__main__':
    raise SystemExit(main())
