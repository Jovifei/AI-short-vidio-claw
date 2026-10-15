# v4 采样边界兼容修复证据

固定计划：a6e3748611134deeda6c8ffa27c9467c0af1d279。基线：b6b5e8b408c68ebaf9b93fd231ced1d380c98480。

本机固定 Comfy 源码显示：Wan 节点默认 CPU 中间张量，采样器转至 MODEL.load_device 和 float32。旧 v4 误要求采样张量仍与节点的 anchor_mask 同设备/精度，导致合法迁移失败。原 v2/v3 没有该误拒绝。

新失败回归使用真实 Torch CPU 的完整形状和 float64→float32 转换，MODEL 仅使用明确测试脚手架；没有加载权重、创建 CUDA tensor 或运行 GPU。CUDA 路径由本机实际调用链追踪支撑，不能将 CPU 回归报告为 CUDA 实拍。

red_tests.txt 保存修复前真实失败；green_tests.txt 保存同一回归修复后结果。最终全量、ComfyCPU、noTorch和保护哈希验证另存本目录，固定实现SHA的GitHub CI在提交后独立收集。

几何和人审状态保持：V008=GEOMETRY_BLOCKED、V009=NO_SAFE_BACKGROUND_ROI，未创建take14/take15，未部署新插件，GPU NOT_RUN。take09 Jovi CHANGES_REQUIRED、take10 Jovi PENDING，SH901/SH902和正式30镜门禁未开放。
