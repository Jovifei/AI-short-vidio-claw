# AGENTS.md — AI/Codex 接手规则

## 最高优先级

当前项目执行 V2 Product Route。

必须先读：
1. README.md
2. PROJECT_STATE.md
3. docs/18_ROUTE_CORRECTION_AND_MASTER_PLAN.md
4. docs/19_ACTIVE_VISUAL_SPEC.md
5. docs/stages/README.md

## 当前任务

在 V0/K1 未 PASS 前：
- 不继续新增故事 T2V；
- 不拿官方模板输出当产品结果；
- 不用临时 SDXL 图代替 approved character reference；
- 不批量提交 Wan I2V；
- 不训练 LoRA；
- 不接 TTS/LipSync；
- 不开始 EP001 正式生产。

## Lab / Production 强制分离

### LAB_ONLY
可以：
- 官方模板
- 通用 prompt
- 性能测试
- OOM/VRAM/RAM 测量

LAB_ONLY 输出不能：
- 使用正式 SHOT 编号冒充剧情镜头
- 进入 final timeline
- 被写成角色质量结论

### PRODUCTION
每个 shot 必须有：
- composition_ref
- identity refs
- costume refs
- approved_keyframe
- approval manifest
- motion_tier

缺任何一项，不提交视频任务。

## Production T2V 禁止

主角 Production 镜头必须 Image First → Video Second。

如果 workflow 没有 LoadImage/start_image：
Production Guard 必须拒绝提交。

## 当前人物视觉

以 docs/19_ACTIVE_VISUAL_SPEC.md 为准。

文字 prompt 不是 identity source。
用户批准 reference 和 approved golden keyframe 才是。

当前服装规则：
- 双方只使用已批准古装
- 不出现现代人物服装
- 现代生活场景可以保留

## 动态策略

M0/M1/M2/M3 见 docs/stages/M1_MOTION_RISK_LADDER.md。
Codex 不得自行把高风险静态镜头升级为完整 I2V。

## 失败处理

人物脸不对：
停止该镜头，不通过继续抽视频解决。

服装不对：
回关键帧阶段。

视频换脸：
降低 motion / frames 或降为静态。

## Git

不提交：
- 模型权重
- 大批量输出
- 第三方 reference 原图
- API key

Git 保存：
- manifest
- hash
- prompts
- workflow
- QA
- stage report
- benchmark

## 每阶段结束

同步：
- PROJECT_STATE.md
- stage report
- approval/QA
- manifest

只有用户明确批准，才能把状态从 CANDIDATE 改为 APPROVED。
