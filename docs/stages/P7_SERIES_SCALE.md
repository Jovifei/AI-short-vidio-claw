# P7 系列化与泛化执行报告

## 目标

从“一集成功”升级到“长期系列稳定”。

## 功能

- 跨集状态
- character stage lifecycle
- voice map
- location reuse
- prop lifecycle
- episode recap
- cover/caption template
- regression benchmark
- Lab → Production model promotion

## 回归集

固定保留：
- 3 个视频 benchmark keyframe
- 10 个双身份 keyframe
- EP001 核心镜头

任何 production 模型/workflow 升级都重跑。

## 技术债控制

每个季度：
- 清理废弃模型 manifest
- 统计模型磁盘
- 统计 reroll 原因
- 统计单集 GPU 时长
- 统计人工介入次数

## Gate

连续 3 集达到：
- 角色一致
- 流程可恢复
- 时长预算可预测
- 失败原因可统计
才考虑 UI/分发平台集成。
