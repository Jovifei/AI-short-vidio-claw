# 当前实际素材接收｜2026-10-07

本轮没有扩写技术路线、没有再创建另一套导入程序。继续复用已有V5的 `import_reference_bundle.py`，把真正存在的原图和可播放审片作为附件交付。

## 实際提供的文件

`AI_short_drama_MEDIA_READY.zip`

- 字节数：54,937,113。
- SHA256：`6259e103d41af94a3c984d6d47a62b65b70579ba7694bede2c338ad3ba3e6906`。
- 26项PNG、26个不同内容hash：原V5 17项 + 新归档的9张旧生成来源。
- LOOKREEL01有10个来源选择，其中COMP09复用REFB02_09，没有重复计数为新图。
- `LOOKREEL01_candidate_review_27s.mp4` 实测720×1280、24fps、648帧、27秒；是旧图静态审片，没有新Wan动作。
- `REVIEW.html` 提供10图原尺寸文件入口、逐项限制、默认未审核的反馈选择。导出意见不等于生产批准。
- `SHOT_REQUIREMENTS.json` 保留30镜当前要求及远端未完成责任，不冒充图片成果。

附件已在对话中给出可点击链接。这次应接收这个确实存在的包；不要用历史FIX2或MEDIA_RECOVERY的固定hash校验本包。历史脚本/文档保留，但不引入另一个接收版本。

Git仍不包含PNG。`git pull`只能拿到登记，不会传图片；本轮没有创建GitHub Release或公开上传人像原件。

## 接收方法

先保存并解压到例如 `E:/incoming/AI_short_drama_MEDIA_READY/`。不要整包覆盖工程，保留本地todo、lessons、Obsidian笔记和未提交修改。

```powershell
Set-Location E:/project/AI-short-vidio-claw
git status --short
git pull --ff-only
python scripts/import_reference_bundle.py --source-root E:/incoming/AI_short_drama_MEDIA_READY --repo-root . --registry assets/registry/received_sources_20261007.json
```

已有文件相同hash则跳过，冲突则拒绝，不覆盖、不批准。完整首次应导入26项；完整重复应新增0、跳过26。包内 `IMPORT_TO_PROJECT.cmd` 调用同一个已有导入器。

原17项恢复到 `local/references/generated/20261005_v5/`；新增9项在 `local/references/received_sources_20261007/`。

新 `received_sources_20261007.json` 仅用于接收，绝不能替换 `generated_assets_v5.json` 充当生产批准库。

## 来源与镜头差异

| 镜头 | 已有来源 | 仍需处理 |
|---|---|---|
| COMP01 | 月下灯影古装并肩 | 服装偏正式，不能当日常轻装；人物一致性 |
| COMP02 | 金光罗衣亲密近景 | 面部遮挡、居家服装与身份 |
| COMP03 | 古典琴语 | 已有古典拨弦乐器；悟空较人类化，不能自动通过 |
| COMP04 | 古院趣味自拍 | 透视、猴脸结构、饰物 |
| COMP05 | 古风灯影相机点心 | 偏正式古装，不能自动当HOME |
| COMP06 | 烛影花帷近景 | 亲密姿势、脸部遮挡、居家装 |
| COMP07 | 镜前抱起 | 手机遮脸、镜像、手脚；只能先静态审 |
| COMP08 | 古风枕头大战 | 遮挡、手臂、飞絮；不能测试复杂I2V |
| COMP09 | REFB02_09花束 | 花束挡脸；不是合格锁脸输入 |
| COMP10 | 四格古装日常 | 逐格身份和服装；不是单镜I2V输入 |

具体映射和hash在包内 `episodes/LOOKREEL01/source_review_20261007.json`。上述图是旧原图恢复，不是本轮新出图。

## 实际验证

助手容器Python 3.13.5：重新运行既有V5 53项测试；新增4项只读registry元数据测试，57项通过。本轮没有宣称重跑前两次交付的所有测试组合。

另8组真实素材集成检查通过：26项文件字节/hash/尺寸/解码，首次导入26，重复跳过26，两份批准表和生产registry前后hash一致，本地冲突不覆盖，最后一项源hash损坏在首个写入前拒绝，10镜绑定和648帧核对，实际视频ffprobe核对。

ZIP CRC检查通过。所有这些是容器离线/CPU检查，不是用户Windows、ComfyUI或GPU验收。

## 没完成的内容

EP00120张精确剧情关键帧仍未交付；LOOKREEL来源与计划差异未全部修复；独立HOME、雨湿、绷带等服装/状态图未完整。

本轮独立出图结果未通过单镜布局要求，返回的拼贴板不计入完成，不裁小格凑数。未完成的出图工作仍由REMOTE_PREPARATION承担；不能全部写成“用户未批准”，也不能让本地Codex以为只剩GPU。

当前 `production_ready=false`、`remote_request_complete=false`。本地可以接收现有素材并核对，不能据此批量开拍。
