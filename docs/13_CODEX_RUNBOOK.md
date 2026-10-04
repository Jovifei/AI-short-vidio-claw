# 13 Codex 执行手册

## 1. Codex 的角色

Codex 是：
- 工程负责人
- 自动化调度器
- benchmark 执行者
- 文档维护者

Codex 不是：
- 无监督艺术总监
- 无条件升级最新模型的机器人
- 自动发布账号运营机器人

## 2. 本地首次接收仓库

第一轮只做 inventory，不改技术路线。

建议任务：
1. git pull
2. 阅读 AGENTS.md 与 PROJECT_STATE.md
3. 找出本机 ComfyUI 路径
4. 找出 Python 环境
5. 记录 GPU/RAM/driver
6. 扫描已有 custom_nodes
7. 扫描已有模型文件名和大小
8. 不移动模型
9. 生成 local/inventory.json
10. 写 docs/benchmarks/P1_ENVIRONMENT.md

## 3. 不要直接下载一堆模型

先回答：
- 已有什么；
- 缺什么；
- 为什么缺；
- 需要多少空间；
- 哪个 workflow 需要它；
再下载。

## 4. P1 推荐执行顺序

### Task A: env_probe
实现 scripts/env_probe.py。

输出：
- Windows
- GPU
- VRAM
- RAM
- driver
- torch
- CUDA
- ComfyUI path/commit
- disk free

### Task B: ComfyUI health
确认 8188/8189 或实际端口。

### Task C: workflow baseline
从 ComfyUI 手工保存一个最小 API workflow。
Codex 不要一开始自动拼复杂 graph。

### Task D: fixed benchmark assets
必须固定同一 keyframe/seed 参数组，否则模型比较无意义。

### Task E: benchmark runner
同一个任务跑：
- native Wan
- wrapper low-vram
- FramePack

结果 CSV/JSON + Markdown。

## 5. 建议未来 CLI

~~~text
claw doctor
claw models list
claw workflows validate
claw episode init EP001
claw episode validate EP001
claw shot keyframe EP001 SH001
claw shot render EP001 SH001
claw shot qc EP001 SH001
claw shot reroll EP001 SH001
claw episode edit EP001
claw episode final-qc EP001
claw episode status EP001
~~~

## 6. 任务提交安全

在调用 ComfyUI 前检查：
- endpoint 在线；
- workflow hash；
- input file 存在；
- model manifest 存在；
- output dir 可写；
- disk free 足够。

运行后写：
- job id；
- start/end；
- duration；
- output；
- error；
- peak VRAM（benchmark mode）。

## 7. 重试策略

OOM：
1. unload/restart clean；
2. 重试同配置一次确认是否碎片；
3. 降 frames；
4. 降 resolution；
5. 开/增加 offload/block swap；
6. 换量化；
7. fallback engine。

Identity drift：
1. 不先换视频模型；
2. 检查 keyframe；
3. 检查 reference；
4. 降动作；
5. 修改 motion prompt；
6. 重抽；
7. 才考虑模型/LoRA。

## 8. 文档职责

每完成阶段：
- 更新 PROJECT_STATE.md；
- 勾 ROADMAP；
- 把关键技术决策写入 DECISION_LOG；
- benchmark 放 docs/benchmarks；
- 新依赖加 REFERENCE_SOURCES 和 model manifest。

## 9. 本项目最重要的测试思维

不要问“能不能跑”。

要问：
- 在什么参数下跑？
- 多少显存？
- 多久？
- 10 次成功几次？
- 身份评分多少？
- 哪种镜头适合？
- 如何回退？

## 10. 提交规范

建议 commit：
- docs:
- feat:
- fix:
- perf:
- test:
- chore:
- benchmark:

每个 PR/commit 不混入无关的大范围重构。
