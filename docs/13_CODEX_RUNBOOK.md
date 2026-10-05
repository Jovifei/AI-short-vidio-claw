# 13 Codex 执行手册（V2 Active）

## 当前身份
Codex 是项目执行者、资产与 manifest 管理者、ComfyUI 调度器和 QA 记录者。

Codex 不是在没有 reference 时自行决定人物外观的工具。

## 当前工作顺序
1. 读 AGENTS.md
2. 读 PROJECT_STATE.md
3. 读 docs/18_ROUTE_CORRECTION_AND_MASTER_PLAN.md
4. 读 docs/19_ACTIVE_VISUAL_SPEC.md
5. 执行 docs/stages/V0_REFERENCE_AND_LOOK_LOCK.md
6. V0 PASS 后执行 K1
7. 用户批准 10 张 keyframe 后执行 T1

## 当前禁止
V0/K1 未完成前：
- 不新增 story T2V
- 不继续地铁模板测试
- 不用临时 SDXL 图作为正式人物
- 不跑 EP001
- 不训练 LoRA
- 不接 TTS/LipSync

## Reference 处理
如果本地拿不到聊天附件：
- 输出缺失列表
- 指定 local/references/inbox/
- 等用户放入文件
- 不猜人物外观

## Production Guard
每个生产视频 job 前校验：
- approved keyframe
- sha256
- identity refs
- costume refs
- motion tier
- I2V workflow

workflow 没有 start_image 时拒绝任务。

## Lab
已有 P0R/P1A 数据保留。
只有明确技术问题才新增 Lab 测试。

## 产品 QA
依次检查：
1. face
2. costume
3. identity
4. anatomy
5. relation
6. composition

人物不对时不进入 Motion。

## 阶段同步
更新 PROJECT_STATE、ROADMAP、approval manifest 与 QA。
只有用户批准才可写 APPROVED。
