# 39 失败诊断与恢复手册

状态：ACTIVE

## 1. 总原则

先判断失败发生在哪一层。

不要：
“图不好 → 换视频模型”
“视频不好 → 重训 LoRA”
这种跨层乱修。

## 2. 人物不像

层级：Visual/Identity。

症状：
- 黛玉变网红脸
- 悟空变人脸
- 侧脸完全不像

处理：
1. 回 Golden Reference
2. 检查 reference 冲突
3. 减少 reference 数量
4. 局部 edit
5. 必要时重建 identity candidate

禁止进入视频。

## 3. 服装乱

层级：Costume。

处理：
- 检查 stage
- 只给一个 costume reference
- 明确 hard reject
- 局部修衣服

不要靠 I2V 自动修。

## 4. 双人互相串脸

层级：Dual identity。

处理优先：
1. Hero Lane
2. regional/two-pass
3. 分区 inpaint
4. 再考虑本地 identity workflow

不要继续随机抽十张。

## 5. 手坏

如果手不是叙事重点：
裁切/遮挡/降低景别。

如果手是重点：
静态修图。

不要让视频模型从坏手起步。

## 6. I2V 换脸

首先检查：
start image 是否 approved。

然后：
- motion 降低
- frames 缩短
- 避免大转头
- camera motion 变静
- prompt 去掉重新描述外观

两次系统性失败：
STATIC fallback。

## 7. 背景融化

- camera motion 降低
- 环境动作减少
- 减少背景人
- 使用较固定构图

## 8. 悟空人脸化

这是 Hard Fail。

处理：
- 不继续同一 take
- 回到 start image
- 检查 motion 是否让脸大幅旋转
- 避免极端表情
- 必要时缩短到 33/49 frames

## 9. 黛玉现代化

Hard Fail。

常见原因：
- prompt 使用 modern beauty/cinematic fashion
- reference 冲突
- 修脸工具过强

处理：
回 Golden Face，不加美颜型 face restore。

## 10. 画面漂亮但没生活感

症状：
像时尚海报。

处理：
增加：
- 实用道具
- 不对称姿势
- 视线不看镜头
- 环境杂物
- 动作中的停顿

减少：
- 完美正面对称
- 全部人物看镜头
- 过度轮廓光

## 11. 节奏慢

先剪：
- 镜头头尾空帧
- 重复景别
- 没信息的静态

不要第一反应增加更多动画。

## 12. 失败上限

同一镜头：
- Keyframe 3 轮 candidate 仍不对 → 升级为 Hero/manual edit
- I2V 2 次系统性失败 → static
- M2 3 次失败 → 降 M1
- M1 3 次失败 → M0

防止无限 GPU 抽卡。

## 13. 回滚

任何模型/workflow升级前保存：
- old hash
- old benchmark
- old accepted result

新版本失败可以一键回到旧 Production Frozen。
