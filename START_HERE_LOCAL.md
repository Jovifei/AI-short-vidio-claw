# 本地先接收这批真实PNG

本轮用户明确要求图片直接入Git。**本分支/提交实际有32个PNG**，不再要求聊天附件ZIP或OpenArt账号。

入口：[图片接收与试拍交接](docs/preproduction/GIT_MEDIA_HANDOFF.md)。

```powershell
git status --short
git fetch origin
git pull --ff-only
python scripts/sync_repo_media.py --apply
python scripts/sync_repo_media.py --check
python scripts/source_pilot.py review
Start-Process local/production/T1_SOURCE_PILOT/review.html
```

先保留本地未提交修改，禁止reset/clean。以上不启动GPU，不修改原30镜审批。

三张现有完整源图已备齐供具体审片。独立`T1_SOURCE_PILOT`仅用于49帧同源保真诊断；经用户逐卡确认后可按交接文件prepare及dry-run，再明确执行。不是原LOOKREEL/EP001的精确剧情镜头，也不替代原产品T1验收。

原27秒LOOKREEL、60秒EP001计划和30镜审批不改；仍由远端补精确关键帧/服装状态，不让本地以旧来源凑剧情。

完整正式生产流程仍读`docs/preproduction/LOCAL_SHOOTING_RUNBOOK.md`。旧文档中“git pull不传PNG/必须ZIP”对本次`assets/media/source_library`不再成立；仅此有界例外，权重和批量成片仍不提交。
