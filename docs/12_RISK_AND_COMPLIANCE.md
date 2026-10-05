# 12 风险、版权与合规（V2）

本文件不是法律意见。

## 1. 当前原型的 Reference 模式
当前 Pilot 使用用户批准的视觉参考来锁定角色脸型、发式和古装方向。

工程规则：
- 第三方 reference 原图默认只放 local/，不提交 Git；
- Git 只保存 ref_id、hash、用途与批准状态；
- 不自动从互联网批量抓取人物数据；
- 不用未授权素材训练公开分发的角色模型。

## 2. 原型与公开/商业发布分开
“可以作为内部制作 reference”不等于“已经确认可公开商业使用”。

若后续公开或商业发布，在发布 Gate 重新确认：
- reference 素材权利
- 角色/影视改编相关权利
- 模型权重许可
- BGM/SFX
- 声音授权
- 平台规则

如果权利边界不满足，则切换到 ORIGINAL_LITERARY_VARIANT，再重新做 Golden Reference。

## 3. LoRA/训练数据
优先：
- 自己生成并有权使用的 approved keyframes
- 明确授权素材
- 可合法使用的数据

不默认批量抓取现实人物或影视截图训练模型。

## 4. 声音
GPT-SoVITS 等工具只使用：
- 本人声音
- 授权配音
- 许可明确的 voice asset

## 5. 开源依赖
继续分别记录：
- code license
- model weight license
- commercial restrictions
- attribution

代码许可证不自动等于模型权重许可。

## 6. 密钥/隐私
禁止 Git：
- API key
- cookie/token
- 私有声音
- 未授权 reference 原图
- 敏感本地信息

## 7. 产品风险
人物不像：
→ V0/K1 解决，不进入视频。

视频换脸：
→ T1/M1 降动作或静态。

显存不足：
→ 低风险 I2V、短帧、串行、fallback。

Agent 越级：
→ AGENTS.md + Production Guard。
