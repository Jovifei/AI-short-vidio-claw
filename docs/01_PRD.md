# 01 产品需求文档 PRD

## 1. 用户

### 主用户
独立 AI 视频创作者 / 工程师。

具备：
- Windows PC；
- RTX 4070 Super 12GB；
- ComfyUI；
- Codex；
- 能接受“AI 自动化 + 人工审片”的混合生产。

### 次用户
未来的 AI Agent/Codex。它需要从仓库直接恢复项目事实、决策、任务状态并继续执行。

## 2. 核心 Job To Be Done

当我有一个短剧想法时，我希望系统把它拆成可控、可复现的镜头生产任务，让我不用每次重新解决角色一致性、显存、工作流、命名、剪辑和返工问题。

## 3. MVP 输入/输出

### 输入
- episode brief
- 角色 Bible
- 风格 Bible
- 目标时长
- 可选参考图
- 可选台词

### 输出
- script.md
- visual_design.md
- storyboard.md
- image_prompts.md
- video_prompts.md
- edit_plan.md
- 每镜 approved keyframe
- 每镜 accepted clip
- dialogue / ambience / sfx
- final.mp4
- qa_report.md
- manifest.json

## 4. 功能需求

### FR-01 项目初始化
能创建标准目录、配置和 episode 模板。

### FR-02 角色资产管理
每个角色有：
- 唯一 ID；
- 正面/3/4/侧面参考；
- 固定脸部/体型特征；
- 基础造型；
- stage 造型；
- reference asset；
- 可选 LoRA；
- 禁止漂移项。

### FR-03 分镜
每镜必须有：
- shot id；
- 叙事目的；
- 起点；
- 终点；
- 人物；
- 道具；
- 景别；
- 机位；
- 动作；
- 时长；
- keyframe；
- 参考资产；
- continuity lock。

### FR-04 关键帧生产
支持两条通道：
- Hero Lane：ChatGPT 网页等人工精修高难关键帧；
- Local Lane：ComfyUI 本地批量生成。

最终只认 approved keyframe。

### FR-05 视频生产
可选择 engine adapter，并记录：
- workflow；
- 模型；
- precision；
- seed；
- frame count；
- duration；
- resolution；
- VRAM/耗时（benchmark 模式）。

### FR-06 音频
每个角色固定 voice id；对白、旁白、环境声和 SFX 分轨保存。

### FR-07 口型
只在有明确正面/半侧人脸对白的镜头启用。孙悟空等非标准人脸默认不自动套用人脸口型，除非专门验收通过。

### FR-08 质量控制
静态图、视频、音频、连续性四层 QC；失败镜头进入 reroll 队列。

### FR-09 局部重跑
修改一个镜头不能要求重跑整集。

### FR-10 导出
统一导出 1080×1920 或配置尺寸，附 manifest 和 QA。

## 5. 非功能需求

- 可复现：相同资源和版本可重新运行。
- 可审计：记录模型、workflow、seed。
- 可升级：模型替换不改业务层数据结构。
- 低显存：12GB 为硬约束。
- 安全：密钥不入库。
- 可恢复：中断后从 shot 状态继续。
- 兼容 Windows。

## 6. 产品 KPI

试播集 KPI：
- 完成率：100% 有成片；
- 镜头首轮可用率：≥50%；
- 两次以内可用率：≥80%；
- 身份一致性人工评分：≥4/5；
- 连续性重大错误：0；
- OOM 导致整集失败：0；
- 任意镜头单独重跑成功率：100%；
- 每镜 manifest 完整率：100%。

## 7. 内容策略

“林黛玉 × 孙悟空”首季内容建议维持：
- 70% 普通情侣生活；
- 20% 关系变化；
- 10% 古典人物宿命线。

先建立“他们真的一起生活”的可信感，再揭示宏大背景。
