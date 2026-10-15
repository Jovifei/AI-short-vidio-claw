# 本地独立终审

两项独立只读审查均确认旧v4的正常采样误拒绝。父任务对照本机固定Comfy源码后先建立失败回归，再仅修改v4阶段的设备/精度契约；同一回归由失败转为通过。

修复只在strength_mode分支捕获MODEL.load_device，并要求采样张量为该设备上的float32。原节点入口samples/mask匹配、采样noise/latent匹配、shape、finite、重复48通道、原base mask、sigma轨迹与alpha一次计算均保留。v2/v3不使用新增采样设备检查，既有数值回归继续通过。

实际ModelPatcher保存load_device并在clone继承，默认UNETLoader使用带明确索引的CUDA设备或CPU。当前图不启用多GPU和自定义未索引设备，故不添加自动推断或--gpu-only回避。测试脚手架只增加真实接口属性及其clone继承，没有向生产代码加入测试开关。

最终本地371项（368通过/3既有Windows权限skip）、ComfyCPU129项通过，noTorch离线通过。保护清单中671项保持原hash，唯一获准改变项是本次节点源码。原profile、job、反馈、图片和已安装插件保持；旧任务不重封。

结论：本地CPU回归与固定源码调用链复核通过。没有真实CUDA运行、部署、新试拍或Jovi视觉接受；背景几何、人审和资源限制仍影响后续出片。固定实现SHA的CI在提交后另外核验。
