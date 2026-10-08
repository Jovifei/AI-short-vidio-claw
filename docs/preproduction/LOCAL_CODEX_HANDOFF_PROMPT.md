# 直接交给本地Codex的Prompt

接管 `E:\project\AI-short-vidio-claw`。本次远端已把真实PNG放入Git，不再停在“等用户另找ZIP”。执行下列实际任务；不要重新规划、不换模型、不升级14B。

1. `git status --short`检查并保留本地修改；安全fetch/pull最新main。冲突时使用独立worktree，不reset/clean。读START_HERE_LOCAL.md、docs/preproduction/GIT_MEDIA_HANDOFF.md。
2. 核对assets/media/source_library/有32个PNG，不是LFS指针。依次执行 `python scripts/sync_repo_media.py`、`python scripts/sync_repo_media.py --apply`、`python scripts/sync_repo_media.py --check`。收据在local/reports/git_media_receipt.json；目标missing_local=0，重复copied=0。错误必须指出具体文件，不要求重新下载旧ZIP。
3. 运行test_git_media_delivery.py、test_preproduction_v5.py、test_launch_readiness.py的unittest；原计划检查另跑launch_readiness.py --project all。不能把原计划0/30解释成接收失败，它表示精确剧情输入还未批准。
4. 执行 `python scripts/source_pilot.py review`，打开local/production/T1_SOURCE_PILOT/review.html给我看SH901/SH902/SH903和各自参考。默认不勾；不得代签，不得拿测试fixture当反馈。若我不认可某张，记录具体意见，不乱换人物。
5. 我主动导出T1_SOURCE_REVIEW.json后，将其放入local/review_evidence/，运行source_pilot.py apply --feedback该路径预览，确认是我的真实选择后才加--apply。批准只写独立T1_SOURCE_PILOT快照，不碰原LOOKREEL/EP001的30镜批准。
6. 三卡获批后，确认真实ComfyUI端口、队列为空及显存/RAM，按GIT_MEDIA_HANDOFF的完整命令先prepare SH901，再submit_prepared默认dry-run。我确认运行后才--execute。保持49帧/24fps/480×832/已有Wan2.2-TI2V-5B，GPU并发1。
7. 第一条完成先看片和记录。通过后按各自目录依次SH902、SH903；每条最多2次。状态未知查history，不自动重投；不覆盖已有take01。输出是源图保真小样，不冒名SH001/COMP09、不进正式成片、不升级为原产品T1通过。
8. 回传：同步到的32项计数/hash核查、原30镜检查、实际用户选择及范围、三条试验的输入/输出路径、seed/workflow/model、frames/fps/耗时/显存RAM、首中尾截图和全片QA。无批准时准确报告“实体图已到位、这3卡待具体审片”，不要报告“没有图片”。

原EP00120张精确关键帧、LOOKREEL修订、独立HOME/RAIN/受伤状态仍由远端制作。本次不要替远端猜图，也不要宣布整个项目已可批量开拍。你可以先完成接收/检查/展示；用户批准后再执行明确的小样试验。
