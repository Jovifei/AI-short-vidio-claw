"""Read-only source/frame diagnostics. Pixel metrics never approve a video."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import statistics
import tempfile
from PIL import Image, ImageChops, ImageDraw

try:
    from .fid1_qa_report import verified_run_output, sha256_file
    from .fid1_job_paths import safe_project_path
    from .preproduction import read_json, require, write_json
except ImportError:
    from fid1_qa_report import verified_run_output, sha256_file
    from fid1_job_paths import safe_project_path
    from preproduction import read_json, require, write_json

REGIONS={'WUKONG_FACE':(.11,.20,.36,.36),'DAIYU_FACE':(.69,.20,.89,.37),
         'BACKGROUND_TREES':(.39,.18,.64,.30)}


def effective_visual_status(report):
    """Derive display from the actual review, never the obsolete top-level flag."""
    review=report.get('visual_review') or {}
    return {key:review.get(key,'PENDING') for key in ('decision','full_playback','identity','costume','limbs')}


def align_source(image,size):
    """Wan common_upscale center crop geometry + bilinear display approximation."""
    width,height=image.size;target_width,target_height=size
    ratio=target_width/target_height;x=y=0
    if width/height>ratio:x=round((width-height*ratio)/2)
    else:y=round((height-width/ratio)/2)
    return image.crop((x,y,width-x,height-y)).resize(size,Image.Resampling.BILINEAR)


def laplacian_variance(image):
    gray=image.convert('L');w,h=gray.size;data=gray.tobytes()
    require(w>=3 and h>=3,'diagnostic region is too small')
    values=[4*data[y*w+x]-data[(y-1)*w+x]-data[(y+1)*w+x]-data[y*w+x-1]-data[y*w+x+1]
            for y in range(1,h-1) for x in range(1,w-1)]
    return statistics.pvariance(values)


def mean_absolute_difference(first,current):
    histogram=ImageChops.difference(first.convert('L'),current.convert('L')).histogram()
    return sum(i*n for i,n in enumerate(histogram))/sum(histogram)


def compare(root,job_dir,out):
    root=Path(root).resolve(strict=True);directory=safe_project_path(root,job_dir)
    require(directory.is_relative_to(root/'local/production/T1_SOURCE_PILOT/video/SH903/jobs'),
            'motion diagnostic is restricted to SH903 source trials')
    destination=safe_project_path(root,out)
    require(destination.is_relative_to(root/'local/reports') and destination!=root/'local/reports',
            'diagnostics require a new local/reports child')
    require(not destination.exists(),'diagnostic output already exists; do not overwrite')
    hashes={}
    def bound(path):
        path=safe_project_path(root,path.relative_to(root).as_posix())
        require(path.is_file(),'missing diagnostic material: '+path.name)
        hashes[path.relative_to(root).as_posix()]=sha256_file(path)
        return path
    job=read_json(bound(directory/'job.json'));report=read_json(bound(directory/'qa/qa_report.json'))
    require(job.get('purpose')=='T1_SOURCE_ONLY' and job.get('eligible_for_final_cut') is False
            and job.get('shot_id')=='SH903','not an isolated SH903 trial')
    run=read_json(bound(directory/'run_record.json'))
    video,record=verified_run_output(root,directory,run);bound(video)
    require(report.get('output',{}).get('sha256')==record['sha256'] and report.get('full_decode')=='PASS',
            'QA output does not match verified video')
    media=report['media'];size=(media['width'],media['height'])
    require((media.get('frame_count'),media.get('fps'))==(49,24),'expected 49 frames at 24fps')
    source_path=bound(directory/job['input_file'])
    require(hashes[source_path.relative_to(root).as_posix()]==job['input_sha256'],'source hash changed')
    with Image.open(source_path) as image:source=align_source(image.convert('RGB'),size)
    frame_paths=[bound(directory/f'qa/all49/frame_{n:02d}.png') for n in range(1,50)]
    source_crops={name:source.crop(tuple(round(v*(size[0] if i%2==0 else size[1])) for i,v in enumerate(box)))
                  for name,box in REGIONS.items()}
    metrics={name:{'relative_box':box,'source_laplacian_variance':laplacian_variance(source_crops[name]),'frames':[]}
             for name,box in REGIONS.items()}
    first={};selected={name:[source_crops[name]] for name in REGIONS}
    for n,path in enumerate(frame_paths,1):
        with Image.open(path) as image:
            image.load();require(image.size==size,'decoded frame dimensions differ')
            frame=image.convert('RGB')
        for name,box in REGIONS.items():
            crop=frame.crop(tuple(round(v*(size[0] if i%2==0 else size[1])) for i,v in enumerate(box)))
            if n==1:first[name]=crop.copy()
            metrics[name]['frames'].append({'frame':n,'time_seconds':(n-1)/24,
                'laplacian_variance':laplacian_variance(crop),
                'mean_abs_difference_vs_first':mean_absolute_difference(first[name],crop)})
            if n in (1,25,49):selected[name].append(crop.copy())
    destination.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.motion-qa-',dir=destination.parent))
    try:
        labels=['SOURCE center/bilinear','FRAME01 0s','FRAME25 1s','FRAME49 2s']
        for name,crops in selected.items():
            w,h=crops[0].size;sheet=Image.new('RGB',(w*4,h+32),'#111827');draw=ImageDraw.Draw(sheet)
            for i,(crop,label) in enumerate(zip(crops,labels)):
                sheet.paste(crop,(i*w,0));draw.text((i*w+3,h+8),label,fill='white')
            sheet.save(stage/(name+'.png'))
        result={'scope':'T1_SOURCE_ONLY','purpose':'AUXILIARY_DIAGNOSTICS_NOT_ACCEPTANCE',
            'job_dir':directory.relative_to(root).as_posix(),'output_sha256':record['sha256'],
            'source_alignment':'Wan center-crop geometry and PIL bilinear approximation; not bit-identical Torch interpolation',
            'effective_visual_review':effective_visual_status(report),'regions':metrics,
            'caveat':'Differences include lighting, blur and identity drift; they do not prove natural head motion.',
            'decoded_frames_origin':'EXISTING_QA_FRAMES_BOUND_BY_HASH; no new independent MP4 pixel-provenance assertion',
            'sources':hashes,'approvals_changed':0}
        write_json(stage/'frame_motion_metrics.json',result)
        write_json(stage/'frame_hashes.json',{'video_sha256':record['sha256'],
            'frames':[{'frame':n,'time_seconds':(n-1)/24,'path':p.relative_to(root).as_posix(),
                       'sha256':hashes[p.relative_to(root).as_posix()]} for n,p in enumerate(frame_paths,1)]})
        for relative,digest in hashes.items():require(sha256_file(safe_project_path(root,relative))==digest,
                                                    'diagnostic source changed before publication')
        require(not destination.exists(),'concurrent diagnostic output')
        os.rename(stage,destination);stage=None
        return {'output_dir':str(destination),'effective_visual_review':result['effective_visual_review'],
                'approvals_changed':0,'visual_accepted_by_tool':False}
    finally:
        if stage is not None and stage.exists():shutil.rmtree(stage)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',default='.')
    parser.add_argument('--job-dir',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args()
    try:print(json.dumps(compare(args.root,args.job_dir,args.out),ensure_ascii=False,indent=2));return 0
    except Exception as exc:print(json.dumps({'ok':False,'error':str(exc),'visual_accepted':False}));return 2

if __name__=='__main__':raise SystemExit(main())
