# K1 — 10 张情侣构图关键帧生产

## 目标
把用户提供的 10 个情侣构图做成统一人物、统一古装、统一关系氛围的 10 张 approved keyframe。

这是第一产品交付，不是 benchmark。

## 默认生产通道
MVP 优先使用 ChatGPT Web Hero Lane。
本地 ComfyUI 可作为候选，但不能为了“全本地”牺牲人物正确度。

## 每张输入包
必须包含：
1. composition_ref
2. DAIYU Golden Face refs
3. WUKONG Golden Face refs
4. DAIYU costume stage ref
5. WUKONG costume stage ref
6. docs/19_ACTIVE_VISUAL_SPEC.md
7. 本镜动作说明

缺 identity/costume ref，不出图。

## 10 张 Shot Card

- COMP01 夜景并肩站姿：LOW。重点是身高差和并肩关系。
- COMP02 室内近景：HIGH。重点是两张脸保持正确，首轮只做低动作版本。
- COMP03 奏乐与陪伴：MEDIUM。使用古典乐器，避免复杂手指特写。
- COMP04 近镜搞怪自拍：LOW。保留前大后小构图。
- COMP05 相机与小点心：LOW-MEDIUM。生活道具可现代，人物服装仍是古装。
- COMP06 床边互动：MEDIUM-HIGH。先锁表情和距离。
- COMP07 镜前抱起构图：HIGH。双手、双腿、镜像必须先过 anatomy gate。
- COMP08 枕头大战：HIGH。首轮只做静态 hero frame。
- COMP09 花束站姿：LOW。低机位，很适合第一批 I2V。
- COMP10 四格情侣日常：MEDIUM。四格都必须保持相同 identity，首轮作为静态拼图。

## 单张流程
1. 生成 candidate 1–3
2. 第一轮只看脸
3. 脸通过后看服装
4. 再看 anatomy
5. 最后看氛围
6. 不合格优先局部 edit，不整张重抽
7. 用户批准后进入 approved

## 本地目录
local/production/LOOKREEL01/
- composition_refs/
- candidates/
- approved/
- approval/

## Git 记录
episodes/LOOKREEL01/
- plan.yaml
- keyframe_manifest.yaml
- qa.md

## PASS
- 10/10 approved
- 两位 identity 均 ≥4/5
- 0 张现代服装
- 0 张悟空明显人脸化
- 0 张黛玉明显现代化
- 用户明确确认人物方向

未通过：禁止进入产品 I2V。
