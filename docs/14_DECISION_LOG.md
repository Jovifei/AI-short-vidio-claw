# 14 架构决策记录 ADR

## ADR-001 Image First → Video Second
状态：Accepted。
原因：角色和构图先冻结，视频只负责动作。

## ADR-002 Wan2.2 主线边界
状态：Amended 2026-10-04。

原定义“Native ComfyUI + Wan2.2”过宽。

新定义：
- P1A 只认 Native ComfyUI + Wan2.2-TI2V-5B。
- A14B 不属于 P1A。
- 14B 的 GGUF/强 offload 属 Lab，必须单独 benchmark。

依据：
Wan2.2 官方 5B 720P standalone 至少 24GB；I2V-A14B standalone 至少 80GB。
ComfyUI 官方则说明 5B + native offload 可适配约 8GB VRAM。
因此本机以实测为准。

## ADR-003 WanVideoWrapper
状态：Accepted as Lab only。
原生可用时优先 native；低显存/新能力再评估 Wrapper。

## ADR-004 FramePack
状态：Accepted as P1B optional。
不先安装；P1A 质量/速度有明确问题再对照。

## ADR-005 人类/非人 identity 分离
状态：Accepted。
DAIYU 与 WUKONG 不用同一个 FaceID 逻辑。

## ADR-006 原创林黛玉
状态：Accepted。
不复刻具体影视演员。

## ADR-007 两道人类 Gate
状态：Accepted。
Keyframe / Final。

## ADR-008 Git 不存大模型/大媒体
状态：Accepted。

## ADR-009 CLI before UI
状态：Accepted。

## ADR-010 借鉴而非 fork Story Claw/Drama Skills
状态：Accepted。

## ADR-011 P1 Gate 必须后验
状态：Accepted 2026-10-04。

撤销：
“576×1024 或接近尺寸一定要在 12GB 稳定”作为先验。

改为：
用阶梯实测找本机 production baseline。
分辨率只是结果字段，不是 P1 成功定义。

## ADR-012 单 GPU 服务
状态：Accepted 2026-10-04。

P1/P2/P3 默认只有一个 GPU-heavy process active。
不要求 8188/8189 双 ComfyUI。
实际 ComfyUI URL 由 P0R 发现。

## ADR-013 首个 First Cut 不做 LipSync
状态：Accepted 2026-10-04。

EP001 v0.1 三句台词先 voice-over。
口型推迟 P5。

## ADR-014 双身份同框为 P2 首要 Gate
状态：Accepted 2026-10-04。

单人 identity 成功不代表 CP 短剧可生产。
必须在 10 个固定双人生活场景中验证。

## ADR-015 Strategic GO 与 Production Ready 分开
状态：Accepted 2026-10-04。

项目方向可行 ≠ 当前机器今天可提交生产任务。
当前只有 P0R/P1A 获准执行。

## ADR-016 LTX-2.x 不进入 P1A
状态：Accepted 2026-10-04。

Lightricks ComfyUI-LTXVideo 官方当前推荐 32GB+ VRAM。
其他低显存 runner 的 LTX 结果未来单独作为 Lab，不混淆为原生 ComfyUI 路线。

## ADR-017 WanGP 可作为 P1B/P1C runner
状态：Accepted for optional benchmark。

WanGP 面向低显存并持续更新，但属于第二执行栈。
只有 P1A 后出现明确需求才安装。

## ADR-018 First Cut 动画镜头降风险
状态：Accepted。

高风险手部/接触镜头：
消毒、缠绷带、按手、点泡沫等，在 v0.1 可以使用静态 keyframe + 轻运动，不作为视频 baseline Gate。
