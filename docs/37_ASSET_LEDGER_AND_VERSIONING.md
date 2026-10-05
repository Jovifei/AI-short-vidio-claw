# 37 资产台账、版本与生命周期

状态：ACTIVE

## 1. 为什么需要资产台账

AI 项目最大的隐形成本是：
不知道“哪一张才是批准的”。

所有关键资产必须有唯一 ID、状态、Hash、来源与用途。

## 2. Asset Types

CHAR_REF
COSTUME_REF
COMP_REF
KEYFRAME
VIDEO_TAKE
VIDEO_ACCEPTED
VOICE
SFX
MUSIC
WORKFLOW
MODEL
PROMPT
FINAL

## 3. Status

DRAFT
CANDIDATE
RECOMMENDED
USER_APPROVED
PRODUCTION_READY
ACCEPTED
SUPERSEDED
REJECTED
ARCHIVED

Agent 不能自己设 USER_APPROVED。

## 4. Versioning

图：
KF_v001, v002...

Workflow：
v001, v002...

Prompt：
r001, r002...

不要覆盖 approved 文件。

## 5. Canonical ID

例：
DAIYU_FACE_FRONT_001
WUKONG_FACE_3Q_L_001
LOOKREEL01_COMP09_KF_001
EP001_SH006_KF_001
EP001_SH006_TAKE_002

文件名可以变，但 Canonical ID 不变。

## 6. Ledger 字段

- asset_id
- type
- project
- shot
- version
- status
- local_path
- sha256
- source
- generated_by
- model/workflow
- identity_refs
- costume_refs
- created_at
- approved_at
- supersedes
- notes

## 7. Supersede

Approved 资产不能删除。
新版本通过后：
旧版本状态 → SUPERSEDED。

这样以后能回滚。

## 8. Prompt Trace

任何生成资产必须能追溯：
- prompt revision
- reference IDs
- seed
- workflow hash

无法追溯的图不能成为训练数据。

## 9. Training Eligibility

只有：
USER_APPROVED / PRODUCTION_READY / ACCEPTED
且
identity QA 通过
的图片可以进入训练候选。

## 10. Backup

建议本地：
- Git：文本事实
- local：媒体
- 可选外部盘：approved/final 镜像备份

不要只靠 ComfyUI output 文件夹保存正式资产。

## 11. Cleanup

可以清理：
- rejected candidates
- duplicate temp
- caches

不能清理：
- approved source
- accepted take
- final
- manifest
- model/workflow hash record

## 12. Asset Ledger 文件

建议：
local/asset_ledger.jsonl

Git：
schemas/asset_ledger.schema.json

后续 A3 控制平面自动维护。
