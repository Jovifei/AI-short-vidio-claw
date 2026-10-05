# 脚本入口（V5）

主文档：`docs/30_PREPRODUCTION_V5_EXECUTION.md`；具体PowerShell命令见`docs/preproduction/LOCAL_COMMANDS_V5.md`。

| 脚本 | 用途 | 是否提交GPU |
|---|---|---|
| `import_reference_bundle.py` | 全包hash预检后复制已有图，不覆盖、不批准 | 否 |
| `preproduction.py plan` | 精确帧级数据合同 | 否 |
| `approve_asset.py reference/keyframe` | 记录真实的具体批准，先验证后写入 | 否 |
| `production_guard.py` | V5 guard入口，校验实际出场角色和I2V链路 | 否 |
| `build_render_queue.py` | V5 queue入口，静帧与blocked分别列出 | 否 |
| `preproduction.py prepare` | 冻结image/workflow/job及源文件hash | 否 |
| `submit_prepared.py` | 默认dry-run；明确--execute才调用原probe | 可选 |
| `render_reference_review.py` | 带标识的静态审片序列，CPU+FFmpeg | 否 |
| `validate_production_package.py` | 区分contract_ok和production_ready | 否 |

保留`reference_index.py`与`create_contact_sheet.py`作为一般素材浏览工具，不把它们产生的索引自动当批准登记。

保留`p1_comfy_probe.py`作为底层工具。正式流程不能用它绕过失败的guard；新入口通过任务包调用它。V5批准表不兼容旧空字段格式，必须显式按真实资产迁移，不自动赋予批准。

测试：`python -m unittest discover -s tests -p "test_preproduction_v5.py" -v`，不需要GPU/Pillow。审片序列另需Pillow及FFmpeg。

## 保留的V3管理工具

`project_preflight.py`、`register_asset.py`、`validate_schema.py`及`schemas/`均保留；它们提供V3知识/台账检查。V5使用独立版本标记的计划/批准表，旧schema通过不能替代新的hash/live-chain guard。具体整合见docs/51_PREPRODUCTION_INTEGRATION_V5.md。
