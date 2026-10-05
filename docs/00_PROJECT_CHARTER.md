# 00 项目章程（V2）

## 项目名称
AI-short-vidio-claw

## 一句话定义
一套由 Codex 管理、ComfyUI 执行、针对 RTX 4070 Super 12GB 优化的“角色一致 AI 短剧生产系统”。

## 产品问题
AI 工具能生成单张好图，也能生成单条视频，但连续短剧真正的难点是：
- 人物下一镜换脸；
- 同一角色服装改变；
- 双人同框身份失控；
- 高接触动作破坏脸和肢体；
- 技术 benchmark 被误当成产品成果；
- 没有 approved reference 就进入视频；
- 每次返工无法追溯。

## 首个验证系列
孙悟空 × 林黛玉生活感 CP。

当前 V2 首要验证不是“大场面”，而是：
1. 用户能否一眼认出两位角色；
2. 古装能否跨镜稳定；
3. 10 张不同构图里两位身份是否稳定；
4. approved keyframe 能否在 4070S 上安全动起来；
5. 静态与动态混合能否组成好看的短剧。

## 核心原则
1. Identity First。
2. Costume Lock Before Motion。
3. Image First → Video Second。
4. Lab 与 Production 分离。
5. 人物脸优先于动作复杂度。
6. 高风险镜头允许静态表达。
7. 用户批准是 Production 状态变化的唯一依据。
8. 本地自动化是优化目标，不是第一条成片的前置条件。

## MVP 交付
第一步不是直接 60 秒剧情。

先交付：
- V0 Golden Reference Pack
- K1 10 张 CP approved keyframe
- E0 20–30 秒 CP Look Reel

E0 通过后才进入 EP001。

## 最终系统目标
用户给出：
- 故事/单集梗概
- approved characters
- approved costumes
- 目标时长

系统产出：
- 剧本
- 视觉设定
- 分镜
- approved keyframes
- motion clips
- 声音
- 成片
- QA
- manifest

## 成功定义
MVP 成功：
- 用户明确认可两位主角视觉；
- 10 张构图中 ≥8 张身份稳定；
- 至少一套 LOW-risk I2V production workflow；
- 45–90 秒 First Cut 可观看；
- 任意镜头可追溯和局部返工；
- 后续 Agent 不依赖聊天历史也能继续。
