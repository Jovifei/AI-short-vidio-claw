# 本地完整差异复审

范围：既有A/V006、B/V007暂存实施，以及b37edc5合同新增独立V008/schema6/v4。计划文档与实现固定提交分开。

- 保留旧v2/v3构建器完全冻结断言；v4独立部分强度构建器允许fractional alpha，先完整复制source，再仅在克隆MODEL hook应用有效alpha。LATENT原mask、metadata、首格及ROI外保持。
- 策略、schema、类/socket隔离，严格ROI字段/有限非bool强度、面积和latent重叠验证；双MODEL0/LATENT1边真实接入KSampler，依赖/profile/workflow pins保留。
- 新v4hook明确拒绝dtype/device变化、非法base/repeated48-channel mask；资源门禁在队列和object_info后获取最新数据，RAM不足/未知、VRAM不足/负值/不合理统计都拒绝。没有降低原V5/R1–R4门禁。
- 正负prompt、seed、source、模型与采样预算跟V006一致；强度与额外背景区是综合变化，不作单变量因果结论。
- 父复审发现资源负值可绕过，子代理已补范围与负例。真实full-size Torch、legacy回归、无Torch子进程prepare/dry-run均进入最终发现。
- 646项保护哈希全部相同。旧A/B证据目录只读保留，旧task/take11–13不重封，实际插件旧SHA不变。
- 几何预检真实发现背景框穿过长翎。该具体候选GEOMETRY_BLOCKED，实际take14未创建、prepare/dry-run NOT_RUN、部署NOT_DONE、GPU NOT_RUN。临时fixture准备成功不能代替该现场预检。
- 本地全量359收集/356通过/3既有Windows符号链接权限skip。ComfyCPU与同固定实现HEAD CI另有日志。take09真实拒绝、take10人审PENDING、原30镜0/30和下游关闭如实保留。

结论：源码工程已本地验证；候选现场几何和部署/资源阻塞未解决，不能宣称视频已修好或可开拍。GitHub CI与远端接受仍需实际固定提交后的证据。
