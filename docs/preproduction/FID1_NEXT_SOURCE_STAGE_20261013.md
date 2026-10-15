# FID1 next source stage — local execution / web planning and review

## Goal and authorization

Jovi requested the next stage using the same C2C Project conversation. Local Codex implements, tests, runs ComfyUI and returns a fixed GitHub SHA; web ChatGPT supplies the complete plan and independent review, without writing PR12. Deliver a usable SH903 take09 human review flow and a safe, explicit predecessor chain for SH901 then SH902. Complete the engineering package in one stage, including meaningful negative tests, review, fixes and Actions. Human acceptance remains a separate prerequisite for GPU execution of the next source shot.

## Verified starting state

- Branch codex/fid1-remote-repair at e94e992a544667fb91579b9bfc876c55eb54d711; PR12 open/unmerged, Actions 4/4 success.
- SH903 take09 / SH903_FID1_V005 uses timestep-aware MODEL/LATENT anchoring. Output SHA256 dbdd44e4bdd39b13c8881c3f413a7889f0823c052b99df41698b1d5f61be2db8; runtime/media/full decode pass, Jovi full playback/identity/costume/limbs PENDING.
- Actual review evidence directory has only the earlier T1_SOURCE_REVIEW.json. No take09 visual approval exists. The latest request to continue is not a fabricated full-playback/identity/costume/limbs judgement.
- Existing source_pilot.py hardcodes SH901 <- SH903/take04 and SH902 <- SH901/take02. This stale selection cannot consume take09 acceptance. Prepare checks the gate but discards its evidence; submit does not revalidate predecessor acceptance.
- SH901/SH902 have their own V001 source hashes, seeds, prompts and ROI boxes, but use the old anchor strategy. Keep those old profiles and all old jobs intact.

## Complete stage scope

1. Add a concrete human feedback page for an existing completed job. Show full original input and actual video, source details and first/middle/last/all49; expose each criterion, exact feedback quote and decision. Default to no approval; never automatically mark PASS from playback events. Export the existing strict JSON schema bound to exact shot/profile/output hash. Generate a new page without overwriting old QA or evidence. Preserve the preview-before-apply record-review workflow. Only ingest Jovi's actual export or explicit specific judgement.
2. Replace hardcoded take selection with an explicit --previous-job selection. Fixed shot order remains SH903 -> SH901 -> SH902; no latest scan, fallback, wrong-shot predecessor or self-reference. Require a reviewed accepted predecessor for downstream FID1 prepare.
3. Return and freeze a predecessor receipt in a versioned FID1 job contract, including predecessor job/integrity/workflow/input/run/QA/output/evidence paths and hashes, shot/profile/prompt identities. Validate the completed predecessor against its frozen job/run/QA and actual bytes, without requiring its historic implementation hashes to equal current source code. Recheck before publication and at submit, including under the submission lock. Reject altered or resealed receipts, stale QA/video/evidence, absent quote/timestamp and all unsuccessful/PENDING/CHANGES_REQUIRED inputs.
4. Preserve immutable schema-1 jobs. Continue read-only reporting for completed SH903. Reject legacy downstream execution without a frozen predecessor and require a new take; never retrofit successful history or relax dependency drift checks.
5. Add independent SH901_FID1_V002 and SH902_FID1_V002 schema-4 profiles using each shot's existing approved source/hash, own seed, prompt and ROI bounds; reuse the tested timestep-aware algorithm with feather=4. Inspect their actual source layout; do not copy SH903 coordinates or broaden ROI. These profiles are candidates for gated trials, not new approval records.
6. Exercise meaningful CPU/integration and browser checks: default no approval/export validation; selected take09 instead of failed take04; wrong order; empty quote/invalid timezone; failed take08; predecessor drift across prepare/submit; concurrent change prevents publication; tampered/resealed receipt; no POST on refusal; existing SH903 reporting remains valid. Run appropriate changed suites, then the required full suite and same-SHA Actions once.
7. Commit/push only the bounded code/config/tests/docs and factual stage report to PR12. Keep tasks/ notes and Obsidian local. Return fixed SHA, Actions and real findings through the same C2C conversation; web reviews the completed package and local resolves actionable findings.
8. If Jovi specifically accepts take09 while the stage is running, record their actual words/criteria, preview/apply, prepare a new SH901 take with the exact accepted predecessor, check live Comfy/model/resources/queue, dry-run then single execution. Result unknown -> history before any POST. After SH901, wait for its own human acceptance before SH902. If no specific acceptance arrives, finish all engineering and display the concrete feedback page; report only the human visual gate as pending.

## Constraints

Use E:\project\AI-short-vidio-claw, Wan2.2-TI2V-5B, existing ComfyUI, 49 frames/24fps, existing 576x1024 trial tier, GPU concurrency 1. Preserve dirty Owner files, source PNGs, all existing jobs/evidence and Obsidian. No reset/clean, force push, merge, new platform/model/LoRA, character replacement, guessed formal keyframes or changes to original LOOKREEL/EP001 approval tables. Report engineering/media/visual/production gates separately.

## Requested web response

Read current actual files through this Project's C2C connector. Return one complete STATE: PLAN with file-level implementation, data invariants, compatibility, tests and final review criteria for the full stage above. Avoid stopping after a generic audit or waiting for visual feedback when independent engineering remains executable. Keep web write access unused; local Codex executes the plan and returns a fixed SHA.
