# FID1 保真修复实现记录

状态：IMPLEMENTATION_STAGE
基线：codex/source-fidelity-diagnostics @ acab47dddc58ef563b433af7ae327cc07d351be0

## 目标

只修复 T1_SOURCE_ONLY 的 SH903 保真问题。

不改变：
- 人物设定
- 30镜批准状态
- EP001计划
- Wan2.2-TI2V-5B路线
- 采样平台

## 已证实问题

1. 低分辨率导致脸部细节损失。
2. 单图I2V条件不足，后续latent允许较大变化。
3. 负面提示无法替代身份条件。

## 修复方向

建立可冻结的 FID-01 profile，不修改生产默认：

- scope=T1_SOURCE_ONLY
- shot=SH903
- model=Wan2.2-TI2V-5B
- fixed input hash
- fixed seed

变量顺序：

1. 固定baseline。
2. 单变量提高尺寸。
3. 单变量改变保持策略。
4. 对比首中尾及全部49帧。

## 不允许

- 自动宣称通过。
- 自动进入LOOKREEL。
- 使用评分替代人工视觉审核。
- 引入14B、LoRA、新平台。

## 验收输出

- input sha256
- workflow sha256
- seed
- size
- frames/fps
- runtime
- VRAM/RAM
- first/middle/end
- all49 QA

最终状态只能为：PASS_CANDIDATE / CHANGES_REQUIRED / REJECTED。
