# AI-short-vidio-claw

> RTX 4070 Super 12GB + ComfyUI + Codex 的角色一致 AI 竖屏短剧生产线。

## 当前实际接收入口

本轮已通过对话链接提供 `AI_short_drama_MEDIA_READY.zip`，54,937,113 bytes，26项真实PNG与27秒静态候选审片。先读 [当前素材接收说明](docs/preproduction/CURRENT_MEDIA_RECEIPT.md)。复用已有V5导入器，不再安装新接收版本。新只读registry是 `assets/registry/received_sources_20261007.json`。

**不是26张新出图，也不是30镜开拍包。** EP001精确关键帧等仍由远端补齐，`remote_request_complete=false`、`production_ready=false`。Git不含图片，git pull不等于附件传输。历史FIX2说明保留，仅供接收那个特定旧包，不能混用其hash验证本包。

## 当前状态与唯一入口

人物方向已获“感觉可以，可以继续前期工作”的认可，记录为 `PREPROD_MODEL_DIRECTION_APPROVED`，不是所有新图/权重/三维模型已经最终批准。

**保留V2技术路线、V3创作圣经和V5执行合同。** 不覆盖已有摄影、表演、服装、第一季、声音、WBS与Schema。

技术执行读 [整合与执行索引](docs/51_PREPRODUCTION_INTEGRATION_V5.md) → [详细任务与Gate](docs/30_PREPRODUCTION_V5_EXECUTION.md) → [本地逐条命令](docs/preproduction/LOCAL_COMMANDS_V5.md)。实体素材接收以本文顶部当前入口为准。

## 产品路线

```text
当前人物方向
 → 真实参考/具体批准/哈希
 → 逐镜关键帧
 → approved-keyframe I2V小样
 → 静动态混剪Look Reel
 → EP001故事片
 → 需要时再优化本地身份训练、配音与自动化
```

脸、服装、解剖与情侣关系优先于动作和清晰度；场景可以现代，人物保持批准古装；主角生产镜头禁止无参考T2V，Lab结果不能顶替生产Gate。

## V5已完成的可检查内容

- 3张角色/组合板、10张最近样图、4张确定性裁片：原17项均包括在当前附件。
- LOOKREEL01：10镜、648帧/24fps=27秒；EP001：20镜、1440帧/24fps=60秒。
- 两集机器执行计划、逐镜阅读版、未冒签的批准表；EP001台词/环境音表和字幕草稿。
- 53项既有V5离线回归、逐资产hash、实际I2V连线检查、冻结任务包、默认dry-run提交器。
- CPU静态参考审片不是正式剧情成片。

详细验证见 `docs/preproduction/VALIDATION_V5.md` 与当前接收说明。没有新跑用户GPU，没有训练LoRA，没有三维拓扑/骨骼产物。

## 保留的V3创作知识

| 主题 | 位置 |
|---|---|
| 人物Canonical Visual、表情、斗战胜佛FORMAL/DAILY/HOME | `assets/characters/` |
| 美术/摄影/表演 | `docs/30_VISUAL_DIRECTION_BIBLE.md`、31、32；`assets/style/`、`assets/relationship/` |
| 第一季十集与资产复用 | `episodes/SEASON01/`、38号文档 |
| LoRA/声音/后期/QA/恢复 | 33–39号文档 |
| 分工/准备度/容量/WBS/风险/验收/批次/Prompt/Reference/Agent | 40–50号文档 |
| Schema与管理工具 | `schemas/`、`project_preflight.py`、`register_asset.py`、`validate_schema.py` |

V3服装alias继续有效。COMP09明确FORMAL，日常市场/公交使用DAILY。具体执行参数只认各集`production_plan_v5.json`，不与旧YAML双写。

## 快速离线检查

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/validate_production_package.py --project-dir episodes/EP001
python scripts/validate_production_package.py --project-dir episodes/LOOKREEL01
```

`contract_ok=true`不等于素材已获批；具体关键帧未批准时`production_ready=false`是正确状态。

## 数据与执行

Git保存文档、代码、计划、hash与批准证据；不上传大模型。原图经已有V5导入器校验后导入local，不覆盖冲突文件、不自动批准。只读received_sources登记不能替换生产generated_assets登记。

新任务先 `preproduction.py prepare` 冻结输入；不联网。`submit_prepared.py` 默认仅打印命令，明确 `--execute` 才调用已有ComfyUI probe。严格串行，状态未知先查history，不重复POST。
