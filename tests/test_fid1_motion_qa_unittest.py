"""Synthetic read-only diagnostics, never actual user acceptance."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image
from scripts import fid1_motion_qa as qa


class MotionQATests(unittest.TestCase):
    def fixture(self,root):
        job=root/'local/production/T1_SOURCE_PILOT/video/SH903/jobs/take99'
        (job/'qa/all49').mkdir(parents=True);(job/'run_record_media').mkdir()
        image=job/'source.png';Image.new('RGB',(64,128),'gray').save(image)
        video=job/'run_record_media/synthetic.mp4';video.write_bytes(b'SYNTHETIC NOT A REAL VIDEO')
        def save(path,data):path.write_text(json.dumps(data),encoding='utf-8')
        save(job/'job.json',{'purpose':'T1_SOURCE_ONLY','eligible_for_final_cut':False,'shot_id':'SH903',
                            'input_file':image.name,'input_sha256':qa.sha256_file(image)})
        save(job/'run_record.json',{'result':'success','outputs':[{'saved_path':str(video),
            'bytes':video.stat().st_size,'sha256':qa.sha256_file(video)}]})
        save(job/'qa/qa_report.json',{'full_decode':'PASS','human_full_playback':'PENDING',
            'visual_review':{'decision':'CHANGES_REQUIRED','full_playback':'CHANGES_REQUIRED',
                             'identity':'CHANGES_REQUIRED','costume':'PASS','limbs':'CHANGES_REQUIRED'},
            'output':{'sha256':qa.sha256_file(video)},'media':{'width':64,'height':128,'frame_count':49,'fps':24}})
        for n in range(1,50):Image.new('RGB',(64,128),(n,n,n)).save(job/f'qa/all49/frame_{n:02d}.png')
        return job

    def test_math_does_not_equate_pixel_change_to_head_motion(self):
        a=Image.new('RGB',(8,8),(10,10,10));b=Image.new('RGB',(8,8),(20,20,20))
        self.assertEqual(qa.laplacian_variance(a),0)
        self.assertEqual(qa.mean_absolute_difference(a,b),10)
        self.assertEqual(qa.align_source(Image.new('RGB',(20,40)),(8,16)).size,(8,16))

    def test_actual_review_overrides_obsolete_top_level_and_never_auto_accepts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job=self.fixture(root);before=(job/'qa/qa_report.json').read_bytes()
            result=qa.compare(root,job,'local/reports/SYNTHETIC_COMPARE')
            self.assertEqual(result['effective_visual_review']['full_playback'],'CHANGES_REQUIRED')
            self.assertFalse(result['visual_accepted_by_tool']);self.assertEqual(result['approvals_changed'],0)
            self.assertEqual((job/'qa/qa_report.json').read_bytes(),before)
            metrics=json.loads((Path(result['output_dir'])/'frame_motion_metrics.json').read_bytes())
            self.assertEqual(len(metrics['regions']['WUKONG_FACE']['frames']),49)
            with self.assertRaises(ValueError):qa.compare(root,job,'local/reports/SYNTHETIC_COMPARE')
            with self.assertRaises(ValueError):qa.compare(root,job,'local/review_evidence/new')

    def test_source_drift_and_wrong_frame_size_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job=self.fixture(root)
            Image.new('RGB',(64,128),'red').save(job/'source.png')
            with self.assertRaisesRegex(ValueError,'source hash'):qa.compare(root,job,'local/reports/X')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job=self.fixture(root);Image.new('RGB',(4,4)).save(job/'qa/all49/frame_25.png')
            with self.assertRaisesRegex(ValueError,'dimensions'):qa.compare(root,job,'local/reports/X')

    def test_no_torch_subprocess_runs_readonly_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job=self.fixture(root)
            code="""import builtins,sys
old=builtins.__import__
def blocked(name,*a,**k):
    if name=='torch' or name.startswith('torch.'):raise ImportError('SYNTHETIC blocked torch')
    return old(name,*a,**k)
builtins.__import__=blocked
from scripts.fid1_motion_qa import compare
r=compare(sys.argv[1],sys.argv[2],'local/reports/NO_TORCH');assert r['approvals_changed']==0
"""
            result=subprocess.run([sys.executable,'-c',code,str(root),str(job)],
                cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
