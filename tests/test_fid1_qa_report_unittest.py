import importlib
import json
from pathlib import Path
import tempfile
import unittest


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
        job_dir = root / "local/production/T1_SOURCE_PILOT/video/SH903/jobs/take04"
        qa_dir = job_dir / "qa"
        media_dir = job_dir / "run_record_media"
        qa_dir.mkdir(parents=True)
        media_dir.mkdir()
        output_path = media_dir / "trial.mp4"
        output_bytes = b"verified video bytes"
        output_path.write_bytes(output_bytes)
        output_sha = qa.sha256_file(output_path)
        output_relative = output_path.relative_to(job_dir).as_posix()
        write_run_record = {
            "result": "success",
            "prompt_id": "fixture-prompt",
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
            "user_quote": "可以继续SH901同源试拍",
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


if __name__ == "__main__":
    unittest.main()
