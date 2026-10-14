import importlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PROFILE = {"width": 576, "height": 1024, "frames": 49, "fps": 24}
VALID_PROBE = {
    "streams": [{"codec_name": "h264", "width": 576, "height": 1024, "avg_frame_rate": "24/1", "nb_read_frames": "49"}],
    "format": {"duration": "2.041667"},
}


class FID1QAReportTests(unittest.TestCase):
    def test_accepts_timestep_aware_job_contract_but_rejects_mismatched_node(self):
        qa = self.module()
        validate = getattr(qa, "validate_fid1_job_contract", None)
        self.assertTrue(callable(validate), "FID1 QA must bind strategy to its actual Comfy node class")
        job = {"fid1_contract": {
            "strategy": "wan22_timestep_aware_future_roi_v2",
            "node_class": "FID1WanTimestepAwareROIAnchor",
        }}
        self.assertTrue(validate(job))
        job["fid1_contract"]["node_class"] = "FID1WanSourceROIAnchor"
        with self.assertRaisesRegex(ValueError, "strategy|node class|contract"):
            validate(job)

    def module(self):
        self.assertTrue((ROOT / "scripts/fid1_qa_report.py").is_file(), "FID1 output QA must be a real ffprobe/decode report tool")
        return importlib.import_module("scripts.fid1_qa_report")

    def test_parses_exact_video_contract_and_leaves_human_review_pending(self):
        qa = self.module()
        result = qa.parse_ffprobe_info(VALID_PROBE, PROFILE)
        self.assertEqual(result["frame_count"], 49)
        self.assertEqual(result["fps"], 24)
        self.assertEqual((result["width"], result["height"]), (576, 1024))
        review = qa.pending_visual_review()
        self.assertEqual(review["decision"], "PENDING")
        self.assertEqual(review["identity"], "PENDING")
        self.assertEqual(review["costume"], "PENDING")
        self.assertEqual(review["limbs"], "PENDING")
        self.assertEqual(review["full_playback"], "PENDING")

    def test_visual_review_template_does_not_preapprove_or_name_a_reviewer(self):
        qa = self.module()
        make_template = getattr(qa, "visual_review_template", None)
        self.assertTrue(callable(make_template), "QA must create an unapproved Jovi review template")
        job = {"shot_id": "SH903", "trial_profile": {"profile_id": "SH903_FID1_V002"}, "purpose": "T1_SOURCE_ONLY"}
        template = make_template(job, "b" * 64)
        self.assertEqual(template["decision"], "PENDING")
        self.assertEqual(template["reviewer"], "")
        self.assertEqual(template["user_quote"], "")

    def test_rejects_wrong_frame_fps_or_dimensions(self):
        qa = self.module()
        for field, value, message in (
            ("nb_read_frames", "48", "frame"),
            ("avg_frame_rate", "25/1", "fps"),
            ("width", 480, "dimension"),
        ):
            with self.subTest(field=field):
                probe = {"streams": [dict(VALID_PROBE["streams"][0])], "format": dict(VALID_PROBE["format"])}
                probe["streams"][0][field] = value
                with self.assertRaisesRegex(ValueError, message):
                    qa.parse_ffprobe_info(probe, PROFILE)

    def review_fixture(self, qa, root):
        # Synthetic fixture only, never a real failed/accepted user take.
        job_dir = root / "local/production/T1_SOURCE_PILOT/video/SH903/jobs/take99"
        qa_dir = job_dir / "qa"
        media_dir = job_dir / "run_record_media"
        qa_dir.mkdir(parents=True)
        media_dir.mkdir()
        output_path = media_dir / "trial.mp4"
        output_bytes = b"verified video bytes"
        output_path.write_bytes(output_bytes)
        output_sha = qa.sha256_file(output_path)
        image = job_dir/'fixture.png'; image.write_bytes(b'SYNTHETIC source')
        workflow=job_dir/'workflow.json'; workflow.write_text('{}',encoding='utf-8')
        workflow_sha=qa.sha256_file(workflow)
        job={'project_id':'T1_SOURCE_PILOT','purpose':'T1_SOURCE_ONLY','eligible_for_final_cut':False,
             'shot_id':'SH903','seed':2026100803,'input_file':image.name,'input_sha256':qa.sha256_file(image),
             'workflow_sha256':workflow_sha,'trial_profile':{'profile_id':'SH903_FID1_V002',**PROFILE},
             'fid1_contract':{'schema_version':1,'strategy':'wan22_timestep_aware_future_roi_v2',
                              'node_class':'FID1WanTimestepAwareROIAnchor'}}
        (job_dir/'job.json').write_text(json.dumps(job),encoding='utf-8')
        (job_dir/'job_integrity.json').write_text(json.dumps({'schema_version':1,
            'job_sha256':qa.sha256_file(job_dir/'job.json'),'workflow_sha256':workflow_sha,
            'input_sha256':job['input_sha256']}),encoding='utf-8')
        output_relative = output_path.relative_to(job_dir).as_posix()
        write_run_record = {
            "result": "success",
            "prompt_id": "fixture-prompt",
            'queued_new_job':True,'workflow_sha256':workflow_sha,
            "outputs": [{"saved_path": str(output_path), "bytes": len(output_bytes), "sha256": output_sha}],
        }
        (job_dir / "run_record.json").write_text(json.dumps(write_run_record), encoding="utf-8")
        report = {
            "schema_version": 1,
            "scope": "T1_SOURCE_ONLY",
            "shot_id": "SH903",
            "profile_id": "SH903_FID1_V002",
            "runtime_success": True,
            "media_contract_ok": True,
            "full_decode": "PASS",
            'workflow_sha256':workflow_sha,'seed':job['seed'],
            'input':{'path':image.name,'sha256':job['input_sha256']},
            'media':{'width':576,'height':1024,'frame_count':49,'fps':24},
            "output": {"path": output_relative, "bytes": len(output_bytes), "sha256": output_sha},
            "visual_review": qa.pending_visual_review(),
        }
        report_path = qa_dir / "qa_report.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        review = {
            "schema_version": 1,
            "scope": "T1_SOURCE_ONLY",
            "shot_id": "SH903",
            "profile_id": "SH903_FID1_V002",
            "output_sha256": output_sha,
            "decision": "ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL",
            "full_playback": "PASS",
            "identity": "PASS",
            "costume": "PASS",
            "limbs": "PASS",
            "reviewer": "Jovi",
            "user_quote": "SYNTHETIC TEST ONLY: no real human approval.",
            "recorded_at": "2026-10-13T10:00:00+08:00",
        }
        review_path = root / "local/review_evidence/review.json"
        review_path.parent.mkdir(parents=True)
        review_path.write_text(json.dumps(review, ensure_ascii=False), encoding="utf-8")
        return job_dir, output_path, report_path, review_path

    def test_jovi_visual_review_is_explicit_hashed_and_required_for_next_shot(self):
        qa = self.module()
        record_review = getattr(qa, "record_visual_review", None)
        self.assertTrue(callable(record_review), "FID1 human review must be an explicit, hash-bound operation")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job_dir, output_path, report_path, review_path = self.review_fixture(qa, root)

            preview = record_review(root, job_dir, review_path)
            self.assertEqual(preview["mode"], "DRY_RUN")
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["visual_review"]["decision"], "PENDING")
            applied = record_review(root, job_dir, review_path, apply=True)
            self.assertEqual(applied["decision"], "ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL")
            updated = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["visual_review"]["reviewer"], "Jovi")
            self.assertEqual(updated["visual_review"]["evidence_sha256"], applied["evidence_sha256"])
            self.assertTrue((root / updated["visual_review"]["evidence_path"]).is_file())

    def test_review_refuses_video_replaced_after_qa(self):
        qa = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job_dir, output_path, report_path, review_path = self.review_fixture(qa, root)
            output_path.write_bytes(b"different unreviewed video")
            with self.assertRaisesRegex(ValueError, "current output bytes"):
                qa.record_visual_review(root, job_dir, review_path)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["visual_review"]["decision"], "PENDING")
            self.assertEqual(list((root / "local/review_evidence").glob("FID1_*_VISUAL_REVIEW.json")), [])

    def test_competing_exclusive_create_never_deletes_other_evidence(self):
        qa = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job, _, report, feedback = self.review_fixture(qa, root)
            destination = root / qa.record_visual_review(root, job, feedback)['evidence_path']
            original_open = Path.open
            def compete(path, mode='r', *args, **kwargs):
                if path == destination and mode == 'xb':
                    path.write_bytes(feedback.read_bytes())
                    raise FileExistsError('synthetic competing writer')
                return original_open(path, mode, *args, **kwargs)
            before = report.read_bytes()
            with patch.object(Path, 'open', compete), self.assertRaises(Exception):
                qa.record_visual_review(root, job, feedback, apply=True)
            self.assertTrue(destination.exists(), 'loser must not delete the winner evidence')
            self.assertEqual(report.read_bytes(), before)

    def test_feedback_change_after_validation_cannot_save_different_decision(self):
        qa = self.module()
        contract = importlib.import_module('scripts.fid1_review_contract')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job, _, report, feedback = self.review_fixture(qa, root)
            validate = contract.validate_visual_review_payload
            def change(review, **kwargs):
                validate(review, **kwargs)
                changed = dict(review, decision='CHANGES_REQUIRED', identity='CHANGES_REQUIRED')
                feedback.write_text(json.dumps(changed), encoding='utf-8')
            with patch.object(contract, 'validate_visual_review_payload', change):
                try:
                    qa.record_visual_review(root, job, feedback, apply=True)
                except ValueError:
                    pass
            stored = json.loads(report.read_bytes())
            if stored['visual_review']['decision'] != 'PENDING':
                evidence = json.loads((root / stored['visual_review']['evidence_path']).read_bytes())
                self.assertEqual(stored['visual_review']['decision'], evidence['decision'])

    def test_qa_change_after_first_read_is_not_overwritten(self):
        qa = self.module()
        contract = importlib.import_module('scripts.fid1_review_contract')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job, _, report, feedback = self.review_fixture(qa, root)
            validate = contract.validate_visual_review_payload
            def change(review, **kwargs):
                validate(review, **kwargs)
                changed = json.loads(report.read_bytes()); changed['concurrent_note'] = 'preserve me'
                report.write_text(json.dumps(changed), encoding='utf-8')
            with patch.object(contract, 'validate_visual_review_payload', change):
                try:
                    qa.record_visual_review(root, job, feedback, apply=True)
                except ValueError:
                    pass
            self.assertEqual(json.loads(report.read_bytes()).get('concurrent_note'), 'preserve me')

    def test_preview_pins_refuse_feedback_and_qa_drift(self):
        qa=self.module()
        for target in ('feedback','QA'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); job,_,report,feedback=self.review_fixture(qa,root)
                preview=qa.record_visual_review(root,job,feedback)
                path=feedback if target=='feedback' else report
                path.write_bytes(path.read_bytes()+b' ')
                before=report.read_bytes()
                with self.assertRaisesRegex(ValueError,'snapshot differs'):
                    qa.record_visual_review(root,job,feedback,True,
                        expected_feedback_sha256=preview['feedback_sha256'],expected_qa_sha256=preview['qa_sha256'])
                self.assertEqual(report.read_bytes(),before)
                self.assertFalse((job/'qa/.fid1-review.lock').exists())

    def test_two_cooperative_writers_only_one_publishes(self):
        qa=self.module(); contract=importlib.import_module('scripts.fid1_review_contract')
        for same in (True,False):
            with self.subTest(same=same), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);job,_,report,feedback=self.review_fixture(qa,root)
                other=feedback.parent/'other.json'; payload=json.loads(feedback.read_bytes())
                if not same:payload.update(decision='CHANGES_REQUIRED',identity='CHANGES_REQUIRED')
                other.write_text(json.dumps(payload),encoding='utf-8')
                entered=threading.Event(); release=threading.Event(); outcomes=[]
                validate=contract.validate_visual_review_payload
                def hold(review,**kwargs):
                    validate(review,**kwargs);entered.set()
                    self.assertTrue(release.wait(5))
                def writer():
                    try:outcomes.append(qa.record_visual_review(root,job,feedback,True))
                    except Exception as exc:outcomes.append(exc)
                with patch.object(contract,'validate_visual_review_payload',hold):
                    thread=threading.Thread(target=writer);thread.start()
                    self.assertTrue(entered.wait(5))
                    try:
                        lock=job/'qa/.fid1-review.lock'; token=lock.read_bytes()
                        with self.assertRaisesRegex(ValueError,'review lock'):
                            qa.record_visual_review(root,job,other,True)
                        self.assertEqual(lock.read_bytes(),token)
                    finally:release.set();thread.join(5)
                self.assertFalse(thread.is_alive())
                self.assertEqual(outcomes[0]['mode'],'APPLIED')
                stored=json.loads(report.read_bytes()); evidence=root/stored['visual_review']['evidence_path']
                self.assertEqual(evidence.read_bytes(),feedback.read_bytes())
                with self.assertRaises(ValueError):qa.record_visual_review(root,job,feedback,True)
                self.assertTrue(evidence.exists())

    def test_publication_failure_preserves_evidence_for_recovery(self):
        qa=self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);job,_,report,feedback=self.review_fixture(qa,root)
            before=report.read_bytes(); original=qa.os.replace
            def fail(source,destination):
                if Path(destination)==report:raise OSError('SYNTHETIC disk failure')
                return original(source,destination)
            with patch.object(qa.os,'replace',fail), self.assertRaises(OSError):
                qa.record_visual_review(root,job,feedback,True)
            self.assertEqual(report.read_bytes(),before)
            recovery=job/'qa/.fid1-review-recovery.json'
            self.assertEqual(json.loads(recovery.read_bytes())['state'],'RECOVERY_REQUIRED')
            evidence=list(feedback.parent.glob('FID1_*_VISUAL_REVIEW.json'))
            self.assertEqual(len(evidence),1);self.assertEqual(evidence[0].read_bytes(),feedback.read_bytes())
            with self.assertRaisesRegex(ValueError,'RECOVERY_REQUIRED'):
                qa.record_visual_review(root,job,feedback,True)

    def test_lost_lock_ownership_does_not_delete_replacement(self):
        qa=self.module()
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);(directory/'qa').mkdir();lock=directory/'qa/.fid1-review.lock'
            with qa._review_lock(directory,True):
                lock.unlink();lock.write_bytes(b'OTHER WRITER')
            self.assertEqual(lock.read_bytes(),b'OTHER WRITER')

    def test_post_publish_drift_keeps_recovery_and_never_reports_applied(self):
        qa=self.module()
        for kind in ('job','lock'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);job,_,report,feedback=self.review_fixture(qa,root)
                original=qa.os.replace
                def drift(source,destination):
                    result=original(source,destination)
                    if Path(destination)==report:
                        path=job/'job.json' if kind=='job' else job/'qa/.fid1-review.lock'
                        path.write_bytes(path.read_bytes()+b' ')
                    return result
                with patch.object(qa.os,'replace',drift),self.assertRaisesRegex(ValueError,'snapshot changed'):
                    qa.record_visual_review(root,job,feedback,True)
                self.assertTrue((job/'qa/.fid1-review-recovery.json').exists())
                if kind=='lock':self.assertTrue((job/'qa/.fid1-review.lock').exists())

    def test_contact_sheet_uses_source_numbers_and_times(self):
        qa=self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);frames=[]
            for n in (1,25,49):
                p=root/f'frame_{n}.png';qa.Image.new('RGB',(32,64)).save(p);frames.append(p)
            with patch.object(qa.ImageDraw.ImageDraw,'text') as draw:
                qa._contact_sheet(frames,root/'sheet.png',3,32,frame_numbers=[1,25,49],fps=24)
            self.assertEqual([c.args[1] for c in draw.call_args_list],['frame 01 / 0s','frame 25 / 1s','frame 49 / 2s'])

    def test_actual_recording_feeds_eight_file_predecessor_chain(self):
        from test_fid1_predecessor_unittest import completed_predecessor_fixture
        import fid1_predecessor as predecessor
        qa=self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);relative=completed_predecessor_fixture(root,take='take99');job=root/relative
            report_path=job/'qa/qa_report.json'; report=json.loads(report_path.read_bytes())
            feedback=root/report['visual_review']['evidence_path']; report['visual_review']=qa.pending_visual_review()
            report_path.write_text(json.dumps(report),encoding='utf-8')
            preview=qa.record_visual_review(root,job,feedback)
            qa.record_visual_review(root,job,feedback,True,expected_feedback_sha256=preview['feedback_sha256'],
                                   expected_qa_sha256=preview['qa_sha256'])
            receipt=predecessor.validate_predecessor(root,'SH901',relative)
            self.assertEqual(len(receipt['files']),8)
            (job/'qa/.fid1-review-recovery.json').write_text('{}',encoding='utf-8')
            with self.assertRaises(ValueError):predecessor.validate_predecessor(root,'SH901',relative)


if __name__ == "__main__":
    unittest.main()
