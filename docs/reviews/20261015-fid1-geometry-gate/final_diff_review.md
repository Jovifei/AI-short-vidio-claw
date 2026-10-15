# v0.2.1完整补丁复审

固定原版本111cb3f/v0.2.0保持；远端固定71ba6cb完整纠正合同已安全接收，只有新文档，未覆盖本地未提交补丁或Owner笔记。

- 几何manifest不是 caller boolean：profile原始SHA、Git源图SHA、规范ROI SHA、几何JSON/叠层SHA及PNG尺寸都须匹配，未知/缺失/阻塞失败关闭。
- prepare先验证，创建目录前拒绝；发布前重验几何记录，sources与contract冻结receipt。submit默认dry-run重验同一receipt及所有证据；锁内和runtime后沿用原最终job/source重验。
- 新模块仅schema6路径加入dependency；schema1–5保持原解析/业务逻辑，v2/v3/v4数学节点文件字节未改。生产runtime与execute两处只接受REAL_SOURCE；合成fixture只能在临时目录测试离线准备/拒绝，不能执行GPU。
- 源图检查绑定实际源PNG和take09/take10媒体SHA；已核对take10全部49帧hash并查看全景与四个探索窗口。上左第31帧以后被冠翎覆盖，中部瀑布雾、边缘花枝及小latent窗口未给出可信静态背景放行。按合同返回NO_SAFE_BACKGROUND_ROI，不建立V009或take15。
- 实际V008准备拒绝返回exit2，take14未创建。672项旧材料hash全部不变；旧版本标签、用户实际拒绝、人审PENDING、原30镜0/30和下游停止如实保留。
- 本地全量367项（364通过/3既有权限skip，148.727秒）、ComfyCPU125通过（74.348秒）、noTorch子进程通过，compileall/diff检查通过。新固定SHA CI另有日志，不借用旧359/117。

结论：本地补丁通过验证，几何与资源停止条件均保留。几何失败路径是该纠正合同的完整结果；没有产生新GPU、部署、视频或Jovi批准。固定提交后仍需新的CI及完整远端补丁复审，不能引用v0.2.0接受代替新版本接受。
