# P4 控制平面执行报告

## 触发

P3 First Cut 完成，说明人工流程值得自动化。

## 目标

把“手工逐镜操作”抽象成可恢复 CLI，而不是做 GUI。

## 模块

1. config loader
2. workflow registry
3. ComfyUI client
4. task runner
5. manifest writer
6. shot state machine
7. QC hooks
8. resume/reroll
9. benchmark logger

## CLI MVP

- claw doctor
- claw episode validate EP001
- claw shot render EP001 SH001
- claw shot status EP001 SH001
- claw shot reroll EP001 SH001
- claw episode status EP001
- claw episode edit EP001

## 关键原则

- executor adapter 化
- workflow JSON 版本化
- job 可重入
- 失败不影响其他 shot
- output 通过 manifest 关联
- GPU concurrency=1

## Gate

- 任意一镜从 manifest 重跑
- 中断后恢复
- 不需要人工改 workflow 参数
- 所有生成记录可审计
