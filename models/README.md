# models

Git 仓库内只保存 models/manifests，不提交大模型权重。

本机真实模型统一放：
local/models/

建议分类：
- checkpoints
- diffusion_models
- loras
- vae
- text_encoders
- clip_vision
- ipadapter
- insightface
- tts
- lipsync

每个模型 manifest 至少记录：
- model_id
- source_url
- filename
- sha256
- license/code license
- weight license
- size
- purpose
- tested_gpu
- tested_vram_peak
- tested_workflow
- validated_date

ComfyUI 通过 extra_model_paths 或 junction 指向统一模型库，避免多份重复权重。
