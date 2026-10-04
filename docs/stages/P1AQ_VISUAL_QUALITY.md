# P1A-Q Wan2.2 5B 视觉质量验证

## 前置

P1A 已 PASS。

## 目标

判断 5B 是否足以承担**低风险生活镜头**，不是判断它能否完成所有双人手部动作。

## 固定测试图

A：单人微动作
- 悟空回家站定/呼吸

B：双人同框无接触
- 两人看冰箱/并排坐

C：双人低接触
- 靠肩/递物，但避开手指特写

三张都必须先人工 approved。

## 测试矩阵

每张：
- 同 baseline 参数
- 3 takes
- seed 记录
- 同 motion prompt 结构

总计 9 clips。

## 评分

1–5：
- identity preservation
- anatomy
- motion readability
- background stability
- camera stability
- emotional plausibility

硬失败：
- 换脸/换物种
- 多肢体
- 主体消失
- 大幅背景融化

## PASS

- A/B 至少 2/3 take 可剪
- C 至少 1/3 可剪或可用静态替代
- 没有系统性身份崩坏

## 输出

`docs/benchmarks/P1A_Q_WAN22_5B.md`

结论必须为：
- Production candidate for LOW risk
或
- Runtime works but quality insufficient

第二种结论才触发 P1B。
