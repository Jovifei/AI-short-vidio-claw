# 18 技术路线纠偏与总执行计划（V2）

日期：2026-10-05
状态：ACTIVE

## 结论

Wan2.2-TI2V-5B 作为 4070S 的低风险图生视频引擎并没有被现有数据否定。真正的问题是：最近执行把“技术实验输出”混成了“产品效果”，而且在没有批准的人物参考与关键帧之前就开始生成故事画面。

现有仓库记录已经证明：
- 大部分 mp4 是官方模板地铁乐手；
- 一次所谓 SH001 是无参考图 T2V；
- 唯一 I2V 来自未审核 SDXL 静帧；
- 没有已批准的孙悟空/林黛玉角色参考；
- 因此这些结果不能用于判断最终人物是否符合要求。

## 根因

1. Lab 与 Production 没有硬隔离。
2. 原 P1A 要 approved keyframe，但 approved keyframe 又被放到后续 P2，存在前置依赖循环。
3. 旧 Character Bible 的视觉方向与当前用户要求不一致。
4. “Image First → Video Second”没有被提交脚本强制。
5. 没有先做静态人物/服装验收，就进入动态。

## V2 两条线

### LAB LINE
只做显存、速度、API、workflow、OOM 测量。输出永远标记 LAB_ONLY，不是短剧素材。

### PRODUCTION LINE
真正做角色和短剧。硬规则：
- 没有 approved identity refs，不生成产品 keyframe；
- 没有 approved keyframe，不提交产品 I2V；
- Production 禁止用纯 T2V 创建主角；
- 人物脸与服装优先于动作复杂度。

## 总路线

V0 视觉目标锁定
→ K1 十张 CP 构图静帧
→ 用户逐张批准
→ T1 approved-keyframe I2V
→ M1 动态风险分级
→ E0 20–30 秒 CP Look Reel
→ E1 EP001 故事关键帧
→ E2 EP001 First Cut
→ A1 本地身份自动化
→ A2 TTS / LipSync / 后期
→ A3 Codex 全流程自动化
→ Series

## 为什么先做 10 张静态 CP 照

当前最大的产品风险不是“视频能不能跑”，而是“人物是否一眼就是我们要的两个人”。

所以第一产品 Gate 是：
- 10 张静态图；
- 同一对人物；
- 用户认可的人物脸；
- 统一古装；
- 强情侣生活感。

用户提供的 10 个情侣构图直接作为 LOOKREEL01 的构图参考。

## Production 输入合同

每个产品镜头必须有：
- shot_id
- composition_ref
- character identity refs
- costume refs
- approved_keyframe
- approval manifest
- motion_tier
- motion prompt

缺一项，不允许提交视频任务。

## 优先级

1. 人物脸
2. 悟空猴脸结构/黛玉脸型
3. 服装
4. 情侣关系
5. 解剖/接触
6. 构图
7. 光线
8. 动作
9. 原生清晰度

不能为了“动起来”牺牲前五项。

## 立即执行

停止新增泛化 T2V/模板 benchmark。

下一步严格：
1. V0_REFERENCE_AND_LOOK_LOCK
2. K1_TEN_COMPOSITION_KEYFRAMES
3. 用户批准 10 张静帧
4. T1_APPROVED_I2V_BASELINE
5. M1_MOTION_RISK_LADDER
6. E0_CP_LOOK_REEL
7. 再开始 EP001

任何 Agent 跳过 1–3，视为路线执行错误。
