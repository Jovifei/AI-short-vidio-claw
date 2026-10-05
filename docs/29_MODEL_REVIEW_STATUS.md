# 29 人物模型审核状态

日期：2026-10-05
状态：WAITING_USER_REVIEW

## 已生成用于用户审核的建模参考

本轮已在对话中生成两类人物建模审核图：

1. 综合人物建模参考板
   - 孙悟空多角度脸部
   - 林黛玉多角度脸部
   - 双方全身/服装
   - 同框比例
   - 10 个情侣构图示意

2. 锁脸/角色设计参考板
   - 孙悟空正面、侧面、表情
   - 林黛玉正面、侧面、表情
   - 双方全身造型
   - 动作示意与道具

这些图片目前只是 CANDIDATE REVIEW ASSET。
尚未写入 Golden Model Approved。

## 用户需要审核的重点

### 林黛玉
- 脸型是否正确
- 下巴是否仍偏尖
- 眼型/眉形是否正确
- 是否有现代 AI 美女感
- 发型/发饰是否正确
- 古装是否符合目标

### 孙悟空
- 是否一眼是经典齐天大圣猴脸
- 眉骨是否正确
- 吻部是否正确
- 耳形是否正确
- 毛色/毛区是否正确
- 是否出现普通男性脸加毛
- 头箍/服装是否正确

### Couple
- 身高差
- 体型差
- 同框时两张脸是否仍稳定
- CP 感是否自然

## 用户反馈后必须执行

1. 把用户明确批准的建模图保存到：
   local/production/MODEL_REVIEW/approved/

2. 运行 reference_index / hash。

3. 更新：
   assets/characters/daiyu/modeling_review.yaml
   assets/characters/wukong/modeling_review.yaml

4. 只有用户明确批准，才设置：
   golden_model_status: APPROVED

5. 如果用户指出脸型不对：
   只重新做人物建模板，不进入 K1，不消耗 Wan I2V GPU 时间。

## 当前 Gate

GOLDEN_MODEL_APPROVED = false

因此：
- K1 可以继续准备文档，但不能把错误脸批量化；
- Product I2V 继续禁止；
- LoRA 训练继续禁止。
