# Jovi授权：保真修复完整远端阶段

## 目标与所有权

2026-10-11，Jovi明确授权按「远端修复提交 → 本地验证 → GitHub回传 → 远端审核」解决本次输出模糊、转头变脸问题。继续既有短剧Project及对话，不重新规划人物/剧本/平台。远端负责审计、实现、测试修复、自审及固定GitHub提交；本地负责接收精确SHA、实际GPU验证和证据回传。C2C连接只读，不能代替远端GitHub写入能力；若当前网页没有写入工具，要如实说明可用的远端执行方式，不能虚构提交。

## 已核对的事实

- 仓库：Jovifei/AI-short-vidio-claw；远端main及本地基线50ca098ff11147ba8077df4079fd357564a84c63。本地codex/source-fidelity-diagnostics为真实诊断改动；接手时重新检查最新分支/SHA。
- 32个真实Git PNG已同步；missing_local=0、copied=0、already_present=32，hash匹配。原LOOKREEL01/EP001精确输入批准仍0/30；这是正式输入缺口，不是媒体传输失败。
- Jovi主动导出三卡批准，SH901/902/903仅T1_SOURCE_ONLY。local/review_evidence/T1_SOURCE_REVIEW.json及独立review snapshot已应用。原30镜registry和approval没有修改。
- 已真实通过本机ComfyUI生成原3条take01，以及SH903的take02/take03。Jovi指出原输出模糊且人物错误；原3条输出均需要修改，输入批准没有被撤销。
- SH903原图REFB02_01.png，941×1672，SHA2566476cf1e17105b3589095918a46546baced0db35ef2a6ca235551f4b7002149f；各对照同seed2026100803、49帧/24fps、Wan2.2-TI2V-5B、20steps/CFG5/uni_pc/simple/denoise1。
- take01 480×832：326.706秒，VRAM采样峰值11434MiB，明显转正脸、人脸化，CHANGES_REQUIRED。
- take02同尺寸，仅改具体保持左右侧脸/凝视/牵手的提示：514.004秒，峰值11012MiB；人脸化减少但末段转头仍在，CHANGES_REQUIRED。
- take03同take02提示，仅改已有5B候选档576×1024：698.443秒，峰值11613MiB；侧脸/朝向更稳、细节改善，嘴部/饰品微变仍在，IMPROVED_NOT_ACCEPTED。三版同输入、同seed，不等于所有源图/seed都能改善。
- QA检查全部49帧、首中尾及完整播放2.041667秒。GPU成功不等于视觉批准。物理RAM最低：take02 7016448bytes，take03 13938688bytes；显存峰值是5秒采样的全局已用量，非连续硬件峰值。

## 已定位的机制与可用性

1. 480×832约为源图25.4%的像素量。真实ComfyUI ImageScale→VAEEncode→VAEDecode静态诊断显示缩放/VAE先损失细节；Lanczos480改善小，576静态重建更好。
2. 当前单PNG输入的Wan22ImageToVideoLatent只锁首个时间latent，后续mask允许采样；审片脸部/服装裁片没有作为独立生成条件进入现有graph。具体代码：local/comfyui/image/ComfyUI/comfy_extras/nodes_wan.py:1418-1458。
3. 后续latent没有逐帧源图初始化，不能盲目把denoise调小就宣称身份锁定。必须说明每种改动怎样改变实际条件/噪声/几何，并做同源对照。
4. 本机已有原生ImageScale/Wan22 latent/KSampler/VAE等；无可用upscale权重、SUPIR/SeedVR2/FaceDetailer节点。不能因工作流JSON存在就认为依赖可用。现有官方5B模板与原采样参数一致。
5. 本地source_pilot新增冻结trial-profile（480×832/576×1024），仅T1_SOURCE_ONLY，固定输入hash/49帧/24fps/模型采样边界；既有批准校验不变。配置与脚本hash进入job，配置解析/hash竞态和重复键回归已修复。新增9项及原34/53/31项检查通过（共126通过、1Windows符号链接权限跳过）。这只是准备与约束检查，不是质量证明。

## 远端一次完整交付

审查本地诊断分支、当前main、既有5B节点与workflow、实际QA。明确哪些是已证实损失、哪些只是待验证假设；不要复述本地已完成的图片接收步骤。

在现有5B条件下实现一个可复现、有资源边界的保真修复阶段，包括：

- 有界、可冻结的诊断/质量参数及必要graph变更；解释身份条件、姿态、缩放、采样的实际作用，避免仅靠负面提示宣称已锁脸。
- 对任何新节点/算法核实与本机已有版本和5B latent/VAE通道兼容；依赖缺失必须让prepare/guard明确失败。不能自动安装模型或新平台。
- 可执行的对照计划：先SH903单镜新take，保持源图/seed，逐项改变；成功后才顺序扩展SH901/902。不得并发或覆盖旧take。
- 自动化元数据/hash/graph/负路径回归与实际首中尾/all49 QA工具。自动分数不能代替Jovi视觉批准，静态重建/锐化不能冒充视频身份一致性。
- 更新runbook、项目状态和接力合同；保持正式30镜与source小样事实分离。
- 远端自行运行离线测试、修复、自审；提交GitHub分支/PR和最终40位SHA、测试命令/结果及本地准确执行步骤。没有GPU则GPU=NOT_RUN，不得写本机视觉通过。

禁止换人物、安装14B或新生成平台、训练LoRA、替远端猜补EP001剧情图/独立HOME/RAIN/受伤状态、扩大原30镜批准。不能删除本地修改或Obsidian。首次480固定协议属于原baseline，576已有明确本地诊断记录，任何继续放大需先给出显存边界，不得自动当生产默认。

## 验收与回传

本地安全fetch接收精确SHA；有冲突用独立checkout/worktree。运行批准/hash/graph负路径、32图幂等和正式输入readiness；实际队列/模型/资源复核后先dry-run再单次execute。执行状态未知先查history，禁止自动重复POST。

回传每条输入/输出相对路径、hash、seed、workflow、模型、尺寸/49帧/24fps、耗时、显存/RAM采样、首中尾/all49及完整播放的身份/服装/肢体QA。保真改善候选先给Jovi看；reference_approved/keyframe_approved/runtime_success/visual_accepted/final_approved分别记录。远端审核失败继续同阶段修复，不能以单元测试绿、HTTP200或视频生成成功关闭视觉缺陷。

本机详证：local/reports/source_fidelity_comparison_20261010.json，comfy_actual_history_trace_20261009.json，source_fidelity_regression_20261010.json；local/production/T1_SOURCE_PILOT/video/SH903/jobs/take01..03/；diagnostics/SH903/vae_boundary_take01/。通过本项目只读连接读取；现有完整运行记录在local中保留。GitHub审核副本在docs/reviews/20261011-source-fidelity/，包括5条实际视频、首中尾/all49、workflow、QA及manifest；视频/图像原字节一致，JSON本机路径归一化，manifest分别记录原始和副本hash。该目录沿用既有docs/reviews审核副本例外，不是批准素材或批量成片。
