# PROJECT_STATE

更新时间：2026-10-04

## 当前结论

项目正式进入 P0：产品、架构、目录、SOP 和验收基线建立。

仓库原为空仓库。本轮已经确立：
- 产品目标：45–90 秒、9:16、10–20 镜头的生活型 AI 微短剧。
- 首个验证 IP：原创视觉设计的“林黛玉 × 孙悟空”CP 生活短剧。
- 硬件目标：RTX 4070 Super 12GB。
- 控制平面：Codex + 项目文件。
- 媒体执行平面：ComfyUI。
- 核心方法：冻结关键帧 → 图生视频 → 音频/口型 → 剪辑 → QC。
- 视频优先路线：原生 ComfyUI + Wan2.2。
- 低显存/实验路线：ComfyUI-WanVideoWrapper。
- 长镜头/低动作回退：FramePack。
- 人类角色身份：参考图 + PuLID/IPAdapter，稳定后再训练角色 LoRA。
- 孙悟空身份：优先角色 LoRA + reference conditioning；不把人脸 FaceID 当作唯一方案。
- TTS：GPT-SoVITS。
- 人脸口型：MuseTalk。
- 剪辑：FFmpeg/ffprobe。
- 质量控制：规则检查 + 视觉模型检查 + 人工最终确认。

## 下一阶段：P1 4070S Benchmark

必须先完成以下基准再继续大规模开发：

1. inventory
   - 记录显卡驱动、CUDA、PyTorch、ComfyUI commit、自定义节点版本。
2. image identity benchmark
   - 同一个林黛玉参考包、同一个孙悟空参考包，测试 10 张不同生活动作关键帧。
3. video benchmark
   - 固定 3 张 approved keyframe。
   - 每张生成 3–5 秒视频。
   - 比较 native Wan2.2、WanVideoWrapper 低显存方案、FramePack。
4. 记录指标
   - VRAM 峰值、生成耗时、崩溃率、人物漂移、手部异常、背景漂移、动作完成度。
5. 形成 docs/benchmarks/P1_4070S_BASELINE.md。

## P1 通过条件

- 至少有一条 576×1024 或接近尺寸的 3–5 秒 I2V 工作流在 12GB 显存上稳定运行。
- 连续 10 次运行不因 OOM 中断超过 2 次。
- 双人低/中动作镜头至少 70% 可用或可通过一次局部重抽修复。
- 输出命名、manifest、seed、模型版本可复现。
- Codex 能通过配置调用 ComfyUI 队列并拿回结果。

## 尚未决定

- 本地图像基座最终选 FLUX、SDXL 还是其他模型。
- 林黛玉是否需要单独 LoRA；先完成参考图锁定再决定。
- 孙悟空 LoRA 训练器和训练参数。
- VLM QC 具体模型。
- 插帧/放大模型。
- 是否引入 Wan2.2 Animate / S2V，需在 12GB 上实测后再决定。
