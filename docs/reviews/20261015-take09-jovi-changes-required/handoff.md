# take09 真实拒绝与后续修复接力

Jovi于2026-10-15明确要求接收实际填写的反馈并继续后续工作。原始反馈文件已复制到local/review_evidence/FID1_SH903_TAKE09_FEEDBACK.json，SHA256 e09b6471ee2b9a9fcbf78248466355a81407f0e057f93b975e00ef821a30b473。

record-review preview+双hash pin apply成功。唯一允许的历史变化为take09的qa/qa_report.json，以及新增实际用户证据；job/workflow/run/video/source未改。决定CHANGES_REQUIRED；full_playback、identity、limbs均CHANGES_REQUIRED，costume PASS；原话完整保存在证据与QA。下游BLOCKED_CHANGES_REQUIRED。图片来源批准依然有效，但不是这个输出的视觉接受。

已实际查看正确1/25/49帧拼图。旧SH903_FID1_V005明确almost motionless、hold starting pose throughout；negative禁止head rotation、pose changes、hand movement；现有timestep-aware hook通过denoise_mask*(1-alpha)持续保留未来ROI。因此“头不动”首先有明确提示和算法限制，不能仅当采样随机故障。背景变糊/面部细节衰减还需完整视频与源图同尺度比较，不凭测试推导视觉通过。

当前工程固定版1bd1c6e1cc5b47d4fccf18766f42fdb61c0221ad，fid1-v0.1.1，R1-R4远端ACCEPTED_ENGINEERING。后续修复与这个工程验收独立。保留历史v001–v005与所有take；不可覆写take09，不可改原30镜。继续Wan2.2-TI2V-5B、49帧24fps、576x1024、单GPU，禁止14B/新平台/换人/训练LoRA。

接力要求：远端一次完成实际失败审核、解释prompt与anchor对运动及背景的影响、选择最小有证据的修复、逐文件/数据合同/回归/视觉QA/资源门禁/新take试验/失败停止/版本与固定SHA计划；提交完整计划文档，之后本地执行与测试并回传复审。不要只做审计或重新规划整条路线。真实人审继续保留；SH901/902不开放。

本机Comfy8188当前无监听，RTX4070SUPER约10GiB显存可用、RAM约6.7GiB可用，资源会漂移。新试拍前必须复核并启动既有实例，不能用旧峰值证明安全余量。
