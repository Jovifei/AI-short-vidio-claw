# 01 产品需求文档 PRD（V2）

## 1. 核心用户
独立 AI 视频创作者/工程师，环境为 Windows + RTX 4070 Super 12GB + ComfyUI + Codex，并可使用 ChatGPT Web 生成/编辑关键帧。

## 2. 核心 JTBD
当我已有明确人物视觉要求时，我希望系统先把“人物是谁、穿什么”锁死，再把每个镜头拆成可追踪的关键帧和视频任务，避免技术跑通但人物完全不对。

## 3. 当前 Pilot 必需输入
当前孙悟空 × 林黛玉项目中，reference 不再是 optional。

必须有：
- DAIYU approved face refs
- DAIYU approved costume refs
- WUKONG approved face refs
- WUKONG approved costume refs
- composition refs
- visual target manifest

## 4. 关键功能

### FR-00 Visual Target Lock
没有 VISUAL_TARGET_LOCKED 状态，不允许进入 Production keyframe/video。

### FR-01 Character Asset
每个角色必须有：
- reference_manifest
- Golden Face Set
- Golden Costume Set
- stage
- hard rejects

### FR-02 Composition Reference
每个关键帧可以绑定一个构图参考，但构图参考不决定人物身份。

### FR-03 Keyframe Production
Hero Lane 与 Local Lane 并存。
MVP 可以全部用 Hero Lane。
最终只认用户 approved keyframe。

### FR-04 Production Video
主角镜头必须从 approved keyframe I2V。
禁止无 reference 的 Production T2V。

### FR-05 Motion Tier
每镜必须标 M0/M1/M2/M3。
高风险镜头默认静态或微动。

### FR-06 Approval
状态：
DRAFT → CANDIDATE → USER_APPROVED → PRODUCTION_READY。

只有用户明确批准才能进入 USER_APPROVED。

### FR-07 Manifest
每镜记录：
- refs
- keyframe hash
- workflow hash
- model
- seed
- render params
- output
- QA
- approval

## 5. MVP 路线
V0 → K1 → T1 → E0 → E1。

不是：
先 T2V benchmark → 直接 EP001。

## 6. KPI

### Visual Lock
- 10/10 关键帧有 approved input
- ≥8/10 双身份都 ≥4/5
- 现代服装误入 = 0

### Motion
- LOW-risk approved keyframe 至少 2/3 可剪
- 换脸硬失败率可统计
- GPU OOM 不阻断全片

### First Cut
- 用户认可人物
- 角色连续性重大错误 = 0
- 可局部重跑
