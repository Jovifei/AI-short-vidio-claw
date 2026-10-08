# AI-short-vidio-claw

角色一致、可追溯的9:16 AI短剧生产线：Windows、RTX4070 Super12GB、ComfyUI、Wan2.2-TI2V-5B。人物方向为古装孙悟空与林黛玉的生活感CP。

## 本轮实际图片已入Git

**不再只提交文件名和图片链接。** `assets/media/source_library/`有32个真实PNG、约54MB：原V5 17项、9张旧构图来源、6张确定性服装细节裁片。

[查看真实图片目录](assets/media/README.md) · [本地接收与试拍步骤](docs/preproduction/GIT_MEDIA_HANDOFF.md) · [给本地Codex的交接Prompt](docs/preproduction/LOCAL_CODEX_HANDOFF_PROMPT.md)

本次用户明确要求直接提交图片，因此有界源图库进入Git；大模型、密钥和批量成片仍不入Git。旧文档“git pull不传PNG/另收ZIP”对这个目录已过时。本地不再需要聊天附件或OpenArt/CDN登录。

```powershell
git status --short
git fetch origin
git pull --ff-only
python scripts/sync_repo_media.py --apply
python scripts/sync_repo_media.py --check
python scripts/source_pilot.py review
```

保留本地未提交修改，不reset/clean。初次32项复制，重复跳过，冲突不覆盖，审批不改。完整命令先读START_HERE_LOCAL.md。

## 三张具体源图试拍候选

草坡SH901、石阶SH902、山水SH903，原图及人物/服装引用已经到位。`T1_SOURCE_PILOT`是独立的49帧同源保真诊断：用户具体审片批准后，离线prepare、默认dry-run、再明确执行；沿用已有Wan2.2-TI2V-5B。

**这不是30镜已完成，也不直接授予原产品T1通过。** 不改LOOKREEL01/EP001的计划和审批，不把这些来源图冒名成剧情SH001/COMP09。完整剧情关键帧仍由远端制作。

## 正式目标和路线不变

V0参考/视觉锁定 → K1逐镜批准 → 获批图生产T1验证 → 27秒LOOKREEL01 → 60秒EP001《大圣今天受伤了》 → 声音、后期、最终验收 → 第一季扩展。

V2是产品路线；V3是创作圣经；V5是逐帧计划、资产、审批与执行合同。图像默认ChatGPT Images参考编辑，第三方不自动扣积分；视频不换14B，不把LoRA或三维模型设为首片前置。

## 事实源

- `assets/registry/generated_assets_v5.json`：原17项路径/hash/用途/批准；本轮不改。
- `assets/media/git_media_manifest.json`：本轮32项Git与local路径/hash。
- `episodes/LOOKREEL01/production_plan_v5.json`：10镜648帧/24fps=27秒。
- `episodes/EP001/production_plan_v5.json`：20镜1440帧/24fps=60秒。
- 对应`approval_manifest_v5.json`：原具体镜头批准，不因source试验而提升。
- `tasks/git_media_delivery_status.json`：本轮实际交付与剩余工作。

## 保留的创作和工程资料

人物Canonical/斗战胜佛FORMAL、DAILY、HOME：`assets/characters/`。
摄影/美术/表演：V3 30–32号文档；第一季：`episodes/SEASON01/`。
声音/训练/后期/QA/资产/恢复：33–39号文档；执行管理：40–50号文档。
V5总执行：`docs/51_PREPRODUCTION_INTEGRATION_V5.md`和`docs/preproduction/LOCAL_SHOOTING_RUNBOOK.md`。

## 离线测试

```powershell
python -m unittest discover -s tests -p test_git_media_delivery.py -v
python -m unittest discover -s tests -p test_preproduction_v5.py -v
python -m unittest discover -s tests -p test_launch_readiness.py -v
python scripts/launch_readiness.py --project all
```

原30镜0/30与`production_ready=false`目前仍可成立：它报告精确剧情输入未批准，不再表示源图传输缺失。测试成功不代替用户Windows/GPU运行和视觉验收。
