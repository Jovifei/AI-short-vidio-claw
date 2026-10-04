# 03 技术架构

## 1. 架构目标

把“创作事实”“调度逻辑”“GPU 工作流”“媒体文件”四件事分开。

### A. Creative Truth
Markdown/YAML/JSON。
决定故事是什么、角色长什么样、镜头发生什么。

### B. Control Plane
Codex + Python CLI。
负责拆任务、调用 adapter、队列、状态、manifest、QC、重试。

### C. Media Plane
ComfyUI / GPT-SoVITS / MuseTalk / FFmpeg。
负责真正生成像素、声音和成片。

### D. Storage Plane
local/ + episodes/ + outputs/。
区分可版本控制事实与不可版本控制大文件。

## 2. 总体数据流

~~~text
Episode Brief
   │
   ▼
Script
   │
   ▼
Visual Design + Continuity Locks
   │
   ├── Character Assets
   ├── Location Assets
   └── Prop Assets
   │
   ▼
Storyboard
   │
   ▼
Frozen Keyframe Prompts
   │
   ├── Hero Lane: ChatGPT/manual
   └── Local Lane: ComfyUI
   │
   ▼
Approved Keyframes
   │
   ▼
Video Adapter
   ├── Native ComfyUI + Wan2.2 (default)
   ├── WanVideoWrapper (low VRAM / experimental)
   └── FramePack (long low-motion fallback)
   │
   ▼
Accepted Shot Clips
   │
   ├── TTS: GPT-SoVITS
   ├── LipSync: MuseTalk when eligible
   └── SFX/BGM/Ambience
   │
   ▼
FFmpeg Edit
   │
   ▼
Automated QC
   │
   ▼
Human Approval
   │
   ▼
Final Episode + Manifest
~~~

## 3. 为什么改成“原生 ComfyUI 优先”

早期方案容易把 WanVideoWrapper 当成主引擎。复核其当前 README 后做出优化：

- Wrapper 作者明确写明：如果某能力已经在 ComfyUI native 中可用，优先 native。
- Wrapper 永久处于 WIP，更适合快速跟进新模型。
- 原生节点更利于长期维护、workflow 兼容和升级。

因此：
- Production：native first。
- Lab：wrapper first for new features。
- 一旦实验功能进入 native 并通过 benchmark，迁回 native。

## 4. 两个 ComfyUI 实例

建议支持但不强制：

- 8188：image / identity / utility；
- 8189：video。

原因：
- Python 依赖容易冲突；
- 视频模型占显存大；
- 可以独立重启视频实例；
- Codex 能按任务启动/停止实例。

12GB 显存下仍保持 GPU heavy concurrency = 1。

## 5. Adapter 接口

未来代码层只认抽象任务：

ImageTask:
- prompt
- references
- width/height
- seed
- workflow_id

VideoTask:
- keyframe
- prompt
- duration
- frames
- fps
- seed
- workflow_id

SpeechTask:
- character_id
- voice_id
- text
- emotion

LipSyncTask:
- video
- audio
- face_policy

EditTask:
- shot_order
- in/out
- subtitle
- audio_tracks

具体模型参数放 config，不放剧情层。

## 6. Shot Manifest

每镜必须生成机器可读 manifest：

- episode_id
- shot_id
- input hashes
- character stages
- prompt revision
- reference files
- workflow version/hash
- model versions
- seed
- render settings
- output files
- QC score
- status
- retry count
- notes

这是未来可复现和自动返工的核心。

## 7. 状态机

DRAFT
→ KEYFRAME_PENDING
→ KEYFRAME_REVIEW
→ KEYFRAME_APPROVED
→ VIDEO_PENDING
→ VIDEO_REVIEW
→ VIDEO_ACCEPTED
→ AUDIO_READY
→ EDIT_READY
→ FINAL_QC
→ DONE

失败可进入：
- REROLL_KEYFRAME
- REROLL_VIDEO
- MANUAL_FIX
- BLOCKED

不得用“文件存在”代替状态事实。

## 8. 12GB 显存策略

默认：
- 串行；
- 480×832 / 576×1024；
- 49/65/81 frames；
- 3–5 秒；
- 先 baseline，不先开所有加速；
- OOM 后按顺序：减分辨率 → 减帧 → offload → block swap → FP8/GGUF → fallback。

不要同时改变多个参数，否则 benchmark 无法解释。
