# 从个人 ConfyUI 工作流库可借用的部分

扫描日期：2026-10-04（Asia/Shanghai）。只读。没有启动 ComfyUI，没有排队，没有下载模型，没有把工作流 JSON 抄进本仓库。

这不是 P1A 路线文件。P1A 仍只有：本机正在用的原生 ComfyUI + Wan2.2-TI2V-5B。14B、GGUF、LTX、WanGP、FramePack 都不进 P1A。角色是林黛玉和孙悟空。悟空不使用 FaceID。MuseTalk 仍是 P5，而且这个库里没有 MuseTalk 图。

旧文件 `F:\ConfyUI\工作流\WORKFLOW_AUDIT_4070S.md`（2026-07-26，静态审计）按「肌肉男跳舞」排序，优先 MimicMotion / SCAIL / Reactor / InstantID。那份顺序和本项目冻结路线相反，不要照做。

## 扫过什么

目录：`F:\ConfyUI\工作流`。跳过 0 字节文件（18 个，含根目录 `肌肉男一键换脸.json`，以及 `Organized\11_Others` 里 17 个）。跳过 tokenizer、package.json 和大于 8MB 的非工作流 JSON。约 413 个 JSON 能抽出 ComfyUI 节点类型。

按目录（含空文件）：`01_ImageGen` 64，`02_VideoGen` 154，`03_Ecommerce` 17，`04_ImageProc` 19，`05_Animation` 27，`06_Character` 11，`07_Design` 1，`09_Tools` 9，`10_Tutorial` 152，`11_Others` 40。根目录另有 Flux / AnimateDiff / 换脸 / 混元图。`4070S_可执行` 只有 1 张 MimicMotion。

节点类型归组（一张图只进先命中的一组，所以数字是下界，不是全集）：

| 组 | 大约张数 | 图在做什么 | 对本项目 |
|---|---:|---|---|
| Wan（含 Wrapper / 14B / 1.3B / Animate / 首尾帧） | 171+ | `WanVideo*`、`UNETLoader`、`WanImageToVideo`、`EmptyHunyuanLatentVideo` | 除下面那张官方 5B 外，不用 |
| FLUX 文生图 / 重绘 / Redux / Kontext | 很多 | `UNETLoader`、`FluxGuidance`、`DualCLIP` | 权重不在 `F:\ComfyUI\models`，现在不用 |
| 放大（SUPIR / 4x / SeedVR2 / UltimateSD） | 约 40 | `UpscaleModelLoader`、`SUPIR_Upscale`、`SeedVR2VideoUpscaler` | 只借「后期放大」这个想法，见下 |
| IPAdapter | 15 | `IPAdapter*` | 盘上几乎只有 FaceID 权重，现在不用 |
| InstantID | 12 | `InstantID*`、`ApplyInstantID` | 换脸，不用 |
| Qwen Image/Edit/TTS | 若干 | `TextEncodeQwenImageEditPlus`、`FB_Qwen3TTS*` | 模型不在本机 ComfyUI，不在 P1A 装 |
| HyVideo / 混元 | 1 张真混元，其余多半是 Wan 的 Hunyuan latent 节点误扫 | `HyVideo*` | 不用 |
| SCAIL | 6 | `WanVideoAddSCAILReferenceEmbeds`，14B GGUF/FP8 | 不用 |
| MimicMotion | 3 | `MimicMotionSampler`、`MimicMotionGetPoses` | 不用 |
| AnimateDiff + RIFE | 3（都在根目录） | `ADE_AnimateDiffLoaderGen1`、`RIFE VFI` | 视频模型不用；插帧想法见下 |
| PuLID | 3 | `ApplyPulidFlux` | 换脸，现在不用 |
| FaceID / ReActor | 2 + 2 | `IPAdapterFaceID`、`ReActorFaceSwap` | 不用；悟空禁止 FaceID |
| LTX 2.0 / 2.3 | 2 | `EmptyLTXVLatentVideo`，19B/22B | 不用 |
| FramePack | 至少 6，混在放大组里（节点名含 Tiled） | `LoadFramePackModel` | 不进 P1A |
| 普通 Checkpoint 文生图 | 8 | `CheckpointLoaderSimple`、`KSampler` | 只借静帧骨架，见下 |
| Sonic / InfiniteTalk / IndexTTS | 各 1 路 | 数字人或配音 | 不是 MuseTalk；P5 之前不做 |

`F:\ComfyUI` 上这次能对上的权重：`diffusion_models\wan2.2_ti2v_5B_fp16.safetensors`，`vae\wan2.2_vae.safetensors`，`text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors`，`checkpoints\sd_xl_base_1.0.safetensors`，`checkpoints\v1-5-pruned-emaonly-fp16.safetensors`，`vae\sdxl_vae.safetensors`，`ipadapter\ip-adapter-faceid-plusv2_sdxl.bin`，`clip_vision\model.safetensors`。`Juggernaut-XL-10.safetensors` 是 0 字节，不能用。`upscale_models`、`loras`、`controlnet`、`insightface`、`animatediff_models` 都是空的。已装自定义节点只有 `comfyui_ipadapter_plus` 和 `glm_prompt`（后者以前导入失败）。没有 WanVideoWrapper、MimicMotion、ReActor、PuLID、RIFE、SUPIR、SeedVR2。

## 可以借用的想法

每一条只借指定的那一段，不把整张图拿来当生产流程。

### 1. 官方 5B 图生视频那一支

- 来源：`F:\ConfyUI\工作流\Organized\01_ImageGen\Wan2x\07.29-万相2.2重磅登场：超越Sora的开源AI视频生成模型，4K高分辨率、多模态创新将引领行业变革\官方工作流\video_wan2_2_5B_ti2v.json`
- 只借：图生视频。节点是原生 `Wan22ImageToVideoLatent` + `LoadImage` + `UNETLoader` / `KSampler`。同一张图里的文生视频路径已经在 P1A smoke 里用过（LoadImage 被旁路）。
- 阶段：P1A（I2V 还没做）。本文件不授权现在去提交。
- 为什么：这就是冻结路线里的那一个模型。三个文件已经在 `F:\ComfyUI\models`，不需要新节点。同目录的 `video_wan2_2_14B_i2v.json` 和 `video_wan2_2_14B_t2v.json` 不要借。不要把这张 JSON 再复制进 git；仓库里已有的 lab API 图继续单独维护。

### 2. SDXL 文生图骨架，只做以后的静帧试验

- 来源：`F:\ConfyUI\工作流\Organized\10_Tutorial\TeacherWorkflows\吴老师\10.02文生图与背后生图逻辑\课程配套资料\本期课件\工作流\文生图+lora.json`（同课 `10.03` 的图生图也只是 `CheckpointLoaderSimple` + `KSampler` + `LoadImage`）
- 只借：提示词到静帧。不要借文件名里的 LoRA（`F:\ComfyUI\models\loras` 是空的）。
- 阶段：以后，P2 静帧。不是 P1A，也不是双人身份 Gate。
- 为什么：本机完整的底模只有 `sd_xl_base_1.0.safetensors` 和 SD1.5 fp16，另有 `sdxl_vae.safetensors`。没有角色 LoRA，没有 ControlNet，没有可用的非 FaceID IPAdapter 权重，所以它锁不住林黛玉或孙悟空。`Juggernaut-XL` 是空文件。

### 3. 静帧放大

- 来源：`F:\ConfyUI\工作流\Organized\10_Tutorial\TeacherWorkflows\吴老师\10.04.高清放大与细节修复\课程配套资料\本期课件\sd放大工作流.json`（`UpscaleModelLoader` + `UltimateSDUpscale`，文件名指向 `4x-UltraSharp.pth`）。更重的对照是 `Organized\04_ImageProc\Upscale\03.31-高清修复无损工作流\工作流\SUPIR图像高清放大细节修复.json` 和 `Organized\04_ImageProc\Upscale\11.19-终于等到了！SeedVR2-2.5.1 完美优化：高清放大+极速体验，低配党的胜利\工作流\▶SeedVR2无损高清放大.json`。
- 只借：放大。不要借任何挂在 14B I2V 后面的 `Video_Upscale_With_Model`。
- 阶段：以后，P5 后期。现在不用。
- 为什么：`F:\ComfyUI\models\upscale_models` 是空的，SUPIR / SeedVR2 权重也不在 models 里。P1A 结束、源片 fps 定下来之前不选放大器。

### 4. 插帧

- 来源：`F:\ConfyUI\工作流\文生视频工作流.json`（根目录）。节点里有 `RIFE VFI`，权重名 `rife47.pth`。
- 只借：插帧这一段。
- 阶段：以后，P5 后期。现在不用。
- 为什么：这张图的主体是 SD1.5 `ADE_AnimateDiffLoaderGen1`，`animatediff_models` 是空的，而且不是 Wan 5B。不要跑整张图。本机也没有 RIFE 权重。同组不要用的还有根目录 `12月19日调.json`、`lora调整测试12月18日15_50.json`。

### 5. 脸部细节，不是换脸

- 来源：`F:\ConfyUI\工作流\Organized\10_Tutorial\TeacherWorkflows\吴老师\10.04.高清放大与细节修复\课程配套资料\本期课件\面部细化工作流.json`
- 只借：静帧面部细化（`FaceDetailer`）。不借 FaceID、PuLID、InstantID、ReActor。
- 阶段：以后，P2 静帧细节或更后。现在不用。悟空不要走这条的人脸锁定。
- 为什么：图要 `bbox/face_yolov8m.pt` 和 `sam_vit_l_0b3195.pth`，本机没有。`insightface` 也是空的。

## 明确不要用

- 跳舞 / 动作迁移：`4070S_可执行\方案A_MimicMotion_4070S_16帧首测_无RIFE.json`；`Organized\02_VideoGen\MotionTransfer\04.11-MimicMotion 照片转跳舞视频教程，照片一键AI转视频\工作流\MimicMotion 上传图片生成跳舞 图生视频 图片跳舞 (1).json`；吴老师 `10.13` 的 MimicMotion；全部 SCAIL（含 `SCAIL动作迁移低显存工作流GGUF.json` 和吴老师 80/87/93）；`09.25-Wan-Animate【动作迁移】换人-高质量+细节`。这些和短剧冻结路线冲突，而且是 14B 或未安装节点。
- 换脸：根目录 `全能一键换脸2.0丨高阶必备丨FLUX+SUPIR+FaceID.json`；吴老师 `10.09` Reactor、`10.16` InstantID、`10.07` FaceID、`10.22` FLUX-PuLID；`Epicrealismxl+Flux换脸工作流.json`。悟空禁止 FaceID。林黛玉的身份以后若测 PuLID / FaceID，也要单独做 P2，不从这些换脸图开工。盘上虽有 `ip-adapter-faceid-plusv2_sdxl.bin`，但 insightface 为空，现在也跑不起来。
- 14B / GGUF / Wrapper：Wan2.1 14B I2V、Wan2.2 A14B 高低噪、VACE、Animate 换人、MoCha、DaSiWa、FusionX、LightX2V distill。节点多半是 `WanVideoModelLoader` / `WanVideoBlockSwap`，本机没有 WanVideoWrapper。首尾帧图 `Wan2.2首尾帧工作流.json` 同样是 14B，不要拿来代替 5B 的关键帧。
- 其他视频栈：根目录 `腾讯混元图生视频V3.json`（`HyVideo*`，720 FP8）；吴老师 `85` LTX2.0 与 `98` LTX2.3；FramePack 长视频（`LoadFramePackModel`，模型不在本机）。LTX / FramePack / WanGP 都不是 P1A。
- 口型：InfiniteTalk、Sonic、IndexTTS、WanAnimate 嘴型。MuseTalk 不在这个库里，仍留到 P5。
- 电商换装、室内效果图、产品精修、洗稿。和林黛玉 / 孙悟空无关。
