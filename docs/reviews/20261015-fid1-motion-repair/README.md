# FID1 v0.2.0：真实拒绝后的完整工程与受控试拍证据

固定计划fea10412233353a2931d338cc30832accccf0d66；实施目录原E盘项目，中文Commit、不可变tag fid1-v0.2.0。旧fid1-v0.1.1保留。

## 已发生

take09的Jovi实际反馈CHANGES_REQUIRED原样应用并保留。实验A V006只改运动语义提示包，使用既有Wan5B，seed2026100803，576×1024，49/24，20steps/CFG5/uni_pc/simple/denoise1/shift8。只POST一次：cb0a1e46-3422-477b-93a4-1805ec4869bd，117.773秒，输出SHA32e93baca62c6a95d63433a526f85dc78fec239f9e8f09b64cd34509a6663435，821029字节。完整decode/49帧合同通过。

实际完整播放及1/25/49/全49帧检查仍未见明确自然头动，脸部叠影、背景细节不足。树木局部末帧Laplacian方差take09约106.08、take10约65.46；这是辅助诊断，不能代替人审或独立证明因果。A使用现有支持的fast-disk和1GiB显存预留，保留模型/dtype/算法预算，但内存管理环境不同于旧take09，明确限制对照归因。

## B的工程与停止点

V007/schema5/v3独立节点实现及真实CPU数学、图链、无Torch prepare/dryrun、依赖漂移/资源负路径已完成。权重1/1/1/1/.9/.8/.7/.6/.6/.6/.6/.6，原mask不改。B没有部署、没有POST；实际安装仍旧版，guard明确拒绝。最终预备包take13，take11/12因代码修正失效而保留，不重封旧包。

A采样显存峰11084MiB，物理RAM最低42385408字节，资源余量不安全。B新门禁要求提交前RAM≥8GiB、空闲VRAM≥8192MiB，未知即拒绝。snapshot不保证后续峰值。只有资源恢复、最终同SHA CI、节点升级/空队列检查都通过，才允许既有合同中的单次B；不刷take或绕过guard。当前Comfy旧实例在空队列后由本任务释放缓存并退出，没有停止其他项目进程。

## 测试与真实门禁

最终本地349：346通过、3既有Windows权限skip；ComfyCPU107通过。附原始日志和保护比较，final_diff_review记录审查。CI及网页复审在固定提交后另记录，ci.json/summary在本提交时明确PENDING，不预报成功。

take10的人审字段仍空/PENDING，不把本地观察当用户拒绝或接受。take09为真实CHANGES_REQUIRED；SH901/902与正式30镜未开放。新审片入口local/production/T1_SOURCE_PILOT/review_sessions/SH903_take10_motion_A_20261015/review.html；MP4保留本地run_record_media，不提交大视频。
