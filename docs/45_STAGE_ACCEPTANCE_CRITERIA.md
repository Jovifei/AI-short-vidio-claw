# 45 各阶段验收标准

状态：ACTIVE

## MODEL_REVIEW

PASS：
- DAIYU face ≥4/5
- WUKONG face ≥4/5
- Costume direction approved
- Couple scale accepted
- User explicit approval

FAIL：
“基本可以继续看看”但仍指出核心脸型错误。

当前用户反馈：
“感觉可以，继续用建模的人物制作前期工作。”

解释：
可记 PREPROD_APPROVED。
但在本地 reference/hash 落盘前，不自动记 FINAL_GOLDEN_APPROVED。

## V0

PASS：
- local reference exists
- sha256 exists
- face refs approved
- costume refs approved
- 10 composition refs indexed
- contact sheet reviewed

## K1

PASS：
- 10/10 keyframes
- identity each ≥4
- no modern clothing
- no severe anatomy
- user approved each image
- hashes in manifest

## T1

PASS：
- 3 approved keyframes tested
- ≥2 clips usable
- LOW-risk repeated 3–5 without OOM
- no systematic identity collapse
- Guard works

## E0

PASS：
- 20–30s complete
- all 10 keyframes visible
- 3–4 motion clips acceptable
- visual identity consistent
- user explicitly approves overall direction

## EP001 KEYFRAMES

PASS：
- 20/20 approved
- injury/bandage continuity
- rain continuity
- costume stages correct
- silent slideshow tells story

## EP001 FIRST CUT

PASS：
- 45–90s
- story understandable
- no fatal identity drift
- no missing shots
- audio understandable
- user approves

## LoRA

PASS：
- fixed regression set identity ≥4
- costume flexibility
- no strong overfit
- two-shot not worse than Hero baseline

## Audio

PASS：
- authorized asset
- same voice identity
- dialogue clear
- no imitation dependency
- ambience supports scene

## Final

PASS：
- visual
- story
- sound
- technical
- rights review
- manifest

都通过才叫 DONE。
