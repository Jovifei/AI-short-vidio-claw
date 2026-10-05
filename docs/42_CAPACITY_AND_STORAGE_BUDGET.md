# 42 4070S 生产容量与存储预算

日期：2026-10-05
状态：PLANNING BASELINE

## 1. 已知本机事实

来自历史 Lab：
- GPU：RTX 4070 SUPER 12GB
- RAM：约 31.82GB
- Wan2.2-TI2V-5B
- T2V 480×832×49：10/10 success
- T2V p50：187.7095s
- T2V p95：264.101s
- 一次 I2V 480×832×49：208.639s

注意：
I2V 样本只有 1 条，不能把 208.639s 当稳定 p50。
这里只用于规划量级。

## 2. LOOKREEL01 粗预算

计划：
- 10 张 approved still
- 4 张优先动态
- 每张先 1 take
- 必要时最多 2 takes

### GPU task 数
最少：4
常见：6–8

如果单条约 3.5–5 分钟：
纯推理：
- 4 条：约 14–20 分
- 8 条：约 28–40 分

再加：
- 模型加载
- Guard
- 上传
- QA
- 重试
实际工作时间可能约 45–90 分钟。

这不是承诺，是排程参考。

## 3. EP001 粗预算

第一版：
- 20 stills
- 4–6 motion shots
- motion shots 1–2 takes

GPU task：
约 6–12。

纯 Wan 推理粗略：
约 25–60 分钟量级。

真正耗时最大的可能不是 GPU，而是：
- 关键帧审核
- 身份修正
- 构图返工

## 4. 为什么不做 20 镜全动态

若 20 镜 × 2 takes：
40 个任务。

以 3.5–5 分/条：
约 140–200 分纯推理。

而高风险镜头通过率更低，实际会更长。

第一版用 4–6 动态镜头能显著提高投入产出比。

## 5. 模型存储

已安装 Wan2.2 5B 核心约：
- diffusion 9.999GB
- VAE 1.409GB
- UMT5 6.736GB

合计约 18.1GB 文件量级（十进制约数；以 manifest bytes 为准）。

不要在多个 ComfyUI 复制同一份。

## 6. Media 存储

单条当前测试 mp4 体积很小，但正式质量/编码可能更大。
不要依赖 benchmark 小文件外推最终空间。

建议每项目预留：
- candidates：5–20GB
- accepted：2–10GB
- temp/cache：10–30GB
- final：较小

LOOKREEL + EP001 建议至少留 50GB 工作余量。

## 7. LoRA 数据

未来：
- source images
- crops
- captions
- checkpoints
- optimizer states

建议单角色准备 20–50GB 实验空间，具体由训练器决定。

## 8. 批次策略

不要一次 queue 20 条。

建议：
- 1 条 smoke
- 2–3 条小批
- QA
- 再继续

GPU 不闲置不是目标。
**避免批量生成一堆错误人物才是目标。**

## 9. 夜间任务

适合夜间：
- approved LOW-risk shots
- 固定 workflow
- 已通过 Guard
- 不需要人工中途选择

不适合夜间：
- 新 identity workflow
- 高风险镜头
- 第一次 LoRA
- 未验证新模型

## 10. 容量 KPI

后续真实记录：
- image candidate / approved ratio
- video take / accepted ratio
- average GPU minutes / accepted shot
- human review minutes / shot
- storage GB / episode

三集后再做真正生产效率优化。
