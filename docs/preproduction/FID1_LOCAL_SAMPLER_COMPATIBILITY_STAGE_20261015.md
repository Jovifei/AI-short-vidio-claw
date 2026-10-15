# 本地完整修复阶段：v4 采样设备与精度兼容

日期：2026-10-15。基线：b6b5e8b408c68ebaf9b93fd231ced1d380c98480 / fid1-v0.2.1。

## 授权与目标

Jovi 已要求本地自行完成规划、审核、修复；网页 GPT-6 不可用不再作为本阶段前置。本阶段先纠正独立审查发现的真实运行兼容缺陷，使用现有 Wan2.2-TI2V-5B 和 ComfyUI，不更换人物或生成平台。

这不是新 GPU 授权。V008 的 GEOMETRY_BLOCKED、V009 的 NO_SAFE_BACKGROUND_ROI、take09 的真实拒绝、take10 的 Jovi PENDING、SH901/SH902 和原30镜门禁均保持。旧 profile、job 和部署文件只读；不创建 take14/take15，不移除第三 ROI，不猜新的几何批准。

## 根因与证据

本机 ComfyUI 固定 commit 6b747c0428c343e1417219641db93a4fb7cb69ae：

1. comfy/model_management.py 的 intermediate_device 默认 CPU；comfy_extras/nodes_wan.py 的 Wan22ImageToVideoLatent 在该设备上创建 samples 与 noise_mask。
2. comfy/samplers.py 的 CFGGuider.sample/outer_sample 把 mask、noise、latent 迁到 ModelPatcher.load_device，并转换为 float32。comfy/sampler_helpers.py 的 prepare_mask 也明确调用 .to(device)。
3. scripts/fid1_wan_latent_anchor_node.py 的 strength_mode 却将采样 tensor 与节点阶段闭包内 anchor_mask 的设备、dtype 比较，合法 CPU→CUDA 或 float64→float32 边界因此抛错。
4. 原 v2/v3 已在 hook 中显式搬运 anchor；take10 使用 v2，不能验证新增 v4 分支。已有 CPU 测试反而把 .double() 作为不应发生的迁移，没有覆盖真实 Comfy 采样边界。

## 唯一修复

- 只为 v4 捕获真实 ModelPatcher.load_device，作为采样阶段的设备契约；当前验证范围为本机 CPU/CUDA。目标设备未知、meta 或不明确的 CUDA 索引拒绝。
- 采样 hook 要求输入位于该设备且为 Comfy 的 float32；在节点阶段仍严格检查 samples/noise_mask 的匹配。不能把节点中间设备当成采样设备。
- 沿用现有 anchor.to(runtime_device/runtime_dtype) 迁移；保持 alpha_space×strength 只计算一次、原 Wan mask、首格、非 ROI 及 sigma-noise 对齐不变。
- noise 与 latent 仍必须同形、同设备、同 dtype、finite；base mask 和 48通道重复检查继续保留。v2/v3 数值与 API 保持。
- 不用 --gpu-only 绕过，不安装或加载新模型，不启动 GPU。

## 完整执行与验证

- [ ] 先用真实 Torch CPU 完整 [1,48,13,64,36] float64→float32 构造失败回归，分别验证 mask hook 和 latent/noise hook。
- [ ] 修复 v4 并验证正常迁移、错误采样设备/dtype、未知设备、meta、非finite、错误base mask以及原v2/v3回归。
- [ ] 在本机 Comfy venv 运行相关 Tensor 套件；CPU验证不能冒充真实CUDA或视频效果。
- [ ] 运行全量、noTorch离线、compileall、原图片与保护哈希检查；原节点源码属于本次允许改变项，报告与旧数据变化区分。
- [ ] 独立代码复审，更新 VERSION/CHANGELOG 为下一补丁版、中文提交、同固定实现SHA四项CI与不可变标签。
- [ ] 写入本地证据和 Obsidian 接力：工程问题是否解决、GPU NOT_RUN、几何与人审剩余阻塞。

## 通过和停止标准

通过意味着正常 Comfy 设备/精度边界不再被误拒绝，同时非法输入仍拒绝。它不表示新视频已经生成或视觉质量被接受。若缺少明确采样设备、保护数据漂移或任何必测回归失败，同一阶段修复并重测，不能绕过守卫。真实 CUDA 与后续视觉试拍待几何、资源、部署及具体 GPU 授权全部满足后另行执行。
