# Explicit predecessor admission and real video feedback

## Result

The old downstream gate selected SH903/take04 and SH901/take02 by constant, and submission did not freeze/revalidate the predecessor. New preparation requires an explicit previous job, freezes its completed evidence, and repeats admission before publication and at submission. A human review page now lets Jovi compare take09 with its exact original/reference pixels and export their actual criteria/quote. Playback never approves a clip.

Local engineering is validated. Jovi take09 visual acceptance and the final web review remain pending. No SH901/SH902 GPU task was submitted or prepared in the real workspace. The actual SH901 V002 prepare attempt correctly exited 2 before creating its take02 directory because take09 has no human review evidence.

## Implementation

- `fid1_predecessor.py`: explicit shot order SH903 -> SH901 -> SH902; canonical take paths; symlink/junction/reparse rejection; completed job/integrity/workflow/input/run/QA/video/actual human evidence checks; an eight-file immutable predecessor receipt.
- New FID1 job contract schema 2. Preparation repeats the receipt check before publication. Submission rechecks before and under the lock and again after runtime/network checks before any intent/probe. A reproduced evidence change during runtime checks now exits without a marker or probe.
- Completed historical jobs remain readable against their frozen bytes, rather than current implementation hashes. Legacy downstream schema-1 execution requires a newly prepared take. The direct predecessor receipt includes its job bytes (and embedded ancestor receipt); completed ancestors are not recursively rehashed.
- `fid1_review_contract.py`: the shared strict JSON schema, exact scope/shot/profile/output hash, four criteria, Jovi quote/raw length <=2048 and timezone timestamp.
- `fid1_visual_feedback.py` / `fid1_qa_report.py review-page`: a new standalone session with original input, actual MP4, frozen face/costume references and QA sheets. All five selectors and reviewer/quote start blank; invalid/inconsistent exports are refused. The page has no approval-write endpoint. Only actual user feedback is previewed/applied through the existing recorder.
- SH901/SH902 V002 candidates use schema 4 and the existing tested Wan5B timestep-aware node. Each keeps its own source/hash, seed, prompts and V001 ROI bounds with feather=4. `profile_receipts.json` records source dimensions, normalized/pixel boxes and both old/new profile hashes. These are candidates, not user approvals.

## Verification

- Full local unittest: **306 collected, 303 passed, 3 skipped** (existing Windows symlink-creation permission cases).
- Existing Comfy venv FID1 suite: **68 passed**; real CPU Torch numerical tests remain in the suite.
- Dedicated predecessor suite: **12 passed**. Integration includes an explicit accepted take09 fixture, all frozen-file drift, prepare races, resealed receipts, legacy downstream refusal, submission-lock/runtime-check drift and no-Torch downstream prepare/dry-run. Fixtures are isolated/synthetic and never recorded as Jovi feedback.
- Feedback-page suite: **7 passed** including client export validation in an isolated Node harness. Existing QA recorder suite: **6 passed**.
- Actual browser check: take09 H.264 playback ended at 2.041667s / 576x1024; all seven images loaded; all five selections, reviewer and quote remained blank; default export was refused. `browser_check.json` is Codex interface evidence, not human acceptance.
- Git media check: 32 files already present, copied=0, missing=0, approvals_changed=0.
- Actual take09 output remains SHA256 `dbdd44e4bdd39b13c8881c3f413a7889f0823c052b99df41698b1d5f61be2db8`. Original input approvals, formal 30-shot manifests, old jobs and Wan node bytes were not changed.

Full test logs remain local under `local/reports/fid1_next_stage_*`. Same-SHA GitHub Actions are checked after branch publication and recorded in PR12.

## C2C and next action

The existing Project/chat supplied the complete next-stage `STATE: PLAN` using the e94e992 GitHub baseline when its local connector returned internal errors. Web remains read-only. During this stage, the project's public connection returned 502; the local bridge and unauthenticated 401 check passed, but named connection repair timed out. Final web review must be requested only after that connection is healthy, using the fixed published SHA. This is not a completed web acceptance claim.

The concrete local review session is `local/production/T1_SOURCE_PILOT/review_sessions/SH903_take09_20261013_01/review.html`. Jovi's actual feedback remains PENDING. If accepted, preview/apply the real JSON and explicitly prepare SH901 with take09 as predecessor; if rejected, record the specific failed criteria and keep downstream trials locked. See the current runbook for commands.
