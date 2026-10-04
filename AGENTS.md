# AGENTS.md — AI/Codex 接手规则

本文件是任何后续 AI、Codex、自动化 Agent 进入仓库后的第一份执行约束。

## 必须先读

按顺序阅读：
1. README.md
2. PROJECT_STATE.md
3. docs/00_PROJECT_CHARTER.md
4. docs/01_PRD.md
5. docs/02_FEASIBILITY.md
6. docs/03_TECHNICAL_ARCHITECTURE.md
7. docs/04_SOP.md
8. docs/05_DIRECTORY_STANDARD.md
9. docs/10_QA_ACCEPTANCE.md
10. docs/11_ROADMAP.md
11. docs/14_DECISION_LOG.md

如任务涉及人物、模型、参考项目、版权，再读对应专题文档。

## 不可违背的工程约束

- 目标硬件：Windows + RTX 4070 Super 12GB + ComfyUI + Codex。
- 第一性目标：角色一致性、故事连续性、生活感，高于“单张炫技”和原生高分辨率。
- 视频默认使用 Image First → Video Second，不把纯文生长视频作为主流程。
- 原生 ComfyUI 已支持的模型和能力，优先原生；WanVideoWrapper 只用于原生缺失的功能、实验模型或显存优化。
- GPU 重任务默认串行运行，除非基准数据明确证明并发安全。
- 每个 episode 必须先形成文本事实，再生成媒体；不得让生成结果反向成为唯一事实源。
- 人物、造型、道具、场景需要“连续性锁”，改变必须有剧情依据并写入 episode 文件。
- 不在 Git 中提交模型权重、LoRA 大文件、缓存、原始批量帧、视频成片、API key。
- 所有外部模型与代码升级必须先记录版本、来源、许可证和回退方案。
- 对失败镜头优先局部重抽或替换工作流，不允许为一个镜头破坏整个项目的统一参数。
- 不自动模仿真实演员、配音演员或具体影视改编的受保护造型。角色设计以古典文学人物概念为基础，形成原创视觉资产。

## 修改项目时必须同步

任何影响下列内容的改动，都要同时更新 PROJECT_STATE.md 和 docs/14_DECISION_LOG.md：
- 主视频模型
- 人物一致性方案
- 目录结构
- 工作分辨率/帧数
- ComfyUI 工作流接口
- TTS/口型方案
- 单集 SOP
- 许可证/商业使用结论

## 完成任务的最低交付

Codex 每完成一个阶段至少留下：
- 可运行或可复现的文件；
- 实测参数；
- 输出位置；
- 失败与限制；
- 下一步；
- 如有 benchmark，写清 GPU、显存峰值、耗时、分辨率、帧数、seed、模型版本。

## 不要做的事

- 不要新建第二套平行目录来解决同一个问题。
- 不要把模型写死在业务代码中，使用 adapter + config。
- 不要把 UI 当成第一阶段目标，先把 CLI/自动化生产闭环跑通。
- 不要一次性自动生产 20 个镜头后才检查；按镜头或小批次设质量门。
- 不要凭印象声称某模型“最好”，必须用本项目固定 benchmark 评价。
