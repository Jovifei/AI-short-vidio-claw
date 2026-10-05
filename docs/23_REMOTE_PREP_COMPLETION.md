# 23 远端准备完成报告

日期：2026-10-05
状态：REMOTE_PREP_COMPLETE / WAITING_LOCAL_VISUAL_REFERENCES

## 已经由远端完成

### 产品/架构
- V2 路线纠偏
- Lab / Production 分离
- Visual Lock 前置
- Approved Keyframe 前置
- Motion Tier
- Production Guard 设计
- 项目目录标准

### 创作
- 第一季创作圣经
- 10 集方向
- LOOKREEL01 十构图设计
- LOOKREEL01 图片提示包
- LOOKREEL01 视频动作提示包
- LOOKREEL01 剪辑方案
- EP001 完整剧本
- EP001 20 镜 storyboard
- EP001 image prompt pack
- EP001 video prompt pack
- EP001 continuity
- EP001 edit plan
- EP001 QA

### 角色/资产建模
- DAIYU active character card
- WUKONG active character card
- 双方 HOME / OUTDOOR / RAIN / INJURED costume stages
- locations registry
- props registry
- visual target config
- reference manifest 模板与 active manifest

### 模型/Workflow
- Wan2.2-TI2V-5B 本机 manifest
- Production candidate I2V workflow JSON
- Production workflow metadata
- 现有 Lab benchmark 保留

### 自动化
- reference_index.py
- production_guard.py
- validate_production_package.py
- p1_comfy_probe.py 已有且保留

## 仍然必须在本地完成

这些无法由远端替代：

1. 把用户真正认可的脸/服装 reference 放入 local/
2. 计算本地 reference hash
3. 用户批准 Golden Face / Costume Set
4. 生成 K1 十张 candidate/approved keyframe
5. 用户批准每张 keyframe
6. 用本机 ComfyUI + GPU 跑 T1
7. 把 approved still / video 组织成 E0
8. 最终 EP001 GPU 渲染和 FFmpeg

## 当前唯一 blocker

Golden Face / Costume reference 还没有落到本地 manifest，因此任何 Production 视频都应被 Production Guard 阻止。

这是正确的阻止，不是进度故障。

## 什么时候重新找远端审核

建议在以下节点把 Git 提交给远端再审：
- V0 contact sheet 完成
- K1 10 张 keyframe 完成
- T1 三张 I2V 完成
- E0 look reel 完成
- EP001 first cut 完成
