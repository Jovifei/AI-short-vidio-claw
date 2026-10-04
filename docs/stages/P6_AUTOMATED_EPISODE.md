# P6 一键单集执行报告

## 目标

将验证过的生产步骤串起来，而不是删除人工判断。

输入：
- episode brief
- approved character stages
- target duration

自动：
- 文本模板
- shot task
- workflow submit
- manifest
- audio
- edit
- technical QC

强制人工 Gate：
1. keyframe approval
2. final approval

## 不自动做

- 自动发布
- 自动训练新角色 LoRA
- 自动替换 production 模型
- 无确认下载大模型
- 无确认改变角色设定

## Gate

从 episode.yaml 开始，可恢复地走到 final candidate。
