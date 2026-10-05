# T1 — Approved Keyframe 的 Wan2.2 5B I2V 基线

## 背景
现有 Lab 已证明 5B 能运行，并且 I2V 接线曾成功一次；但唯一 I2V 输入不是 approved keyframe，所以还不能称为 Production 可用。

## 前置
K1 至少有 3 张 approved keyframe：LOW、LOW-MEDIUM、MEDIUM 各一张。

## Step 1：冻结 Production I2V Workflow
基于已有 workflows/video/lab/VID_wan22_5b_i2v_v001.json。

必须确认：
- LoadImage 存在
- start_image 已连接
- 不是 T2V graph
- positive prompt 是动作提示
- filename_prefix 不再是 smoke

复制为：
workflows/video/production/VID_wan22_5b_i2v_prod_v001.json

## Step 2：Production Guard
提交前必须校验：
- image path 存在
- image 在 approved manifest
- sha256 匹配
- workflow 有 LoadImage
- start_image connected
- shot status = KEYFRAME_APPROVED

任一不满足：禁止 POST /prompt。

## Step 3：Motion Prompt
只描述动作、微动作、镜头运动和环境运动。
不要重新设计人物外观。

## Step 4：三张各 1 take
记录：
identity drift、costume drift、anatomy、motion、elapsed、VRAM/RAM。

如果 2/3 明显换脸，停止，不继续批量跑。

## Step 5：重复稳定
选择表现最好的一张 LOW-risk keyframe，串行 3–5 takes。

已有 10×T2V 不再重复。

## PASS
- 3 张 approved keyframe 至少 2 张可剪
- LOW-risk 重复 3–5 次无 OOM
- 无系统性 identity 崩坏
- Production Guard 生效
- manifest 完整

此时 5B 才能称为 Production Candidate for LOW-RISK I2V。

## FAIL
若运行稳定但人物漂移：
1. 降低 motion
2. 缩短 frames
3. 使用静态/微动画
4. 再考虑替代引擎
5. 不直接跳 14B
