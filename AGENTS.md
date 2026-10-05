# AGENTS — V5执行约束

## 阅读顺序

README → PROJECT_STATE → docs/51_PREPRODUCTION_INTEGRATION_V5 → docs/30_PREPRODUCTION_V5_EXECUTION → docs/preproduction/LOCAL_COMMANDS_V5。

创作继续读取V3的30_VISUAL_DIRECTION_BIBLE、31_CINEMATOGRAPHY_GRAMMAR、32_CHARACTER_PERFORMANCE_BIBLE、45_STAGE_ACCEPTANCE_CRITERIA、49_AGENT_OPERATING_RULES。保留Canonical Visual与Douzhanshengfo FORMAL/DAILY/HOME；兼容名解析见51号整合表。

保留V2的Identity First / Image First → Video Second。V5补齐资产和机器合同，不是新的视频模型路线。历史阶段文档与V5冲突时，以V5当前数据/命令为准，同时记录差异；不要无声覆盖已有实测结果。

## 当前生产事实来源

- `assets/registry/generated_assets_v5.json`：真实资产路径/hash/角色/用途/批准。
- 各集`production_plan_v5.json`：出场角色、服装阶段、帧级时间线、静动态策略。
- 各集`approval_manifest_v5.json`：具体镜头批准。
- `director_cards_v5.md`：机器计划的人工阅读版，禁止独立修改数字造成漂移。

## 不可越过

1. 不把“感觉可以”的方向认可扩展为所有新图批准，不虚构user_quote。
2. 不把二维设定板称为已训练LoRA/三维模型；不把生成板中文字当文学考证。
3. 不用未经批准静帧、临时SDXL角色或无图T2V创建正式主角镜头。
4. 只审实际出场角色；单人镜头不编造另一个人物ref。
5. M0/M3不自动进入I2V；失败后使用同一批准图静态回退。
6. 参考ID必须可解析为正确角色/用途/stage且hash有效的文件，不接受非空字符串冒充资产。
7. 并发GPU任务为1；只允许已有5B候选路径。不得未经明确同意升级14B/新runner。
8. prepare不提交；submit默认dry-run。状态未知时先查history，不自动POST重试。
9. 已存在任务目录不覆盖。图、计划、workflow或批准记录改变后重新prepare。
10. 三张具体获批的合适静帧可做局部T1；完整Look Reel仍需十镜批准，不取消逐图确认。

## 本地路径

- 模型仍用本机已有库，不复制权重到Git。
- reference：`local/references/generated/20261005_v5/`及后续显式登记的本地目录。
- candidate：`local/production/<PROJECT>/candidates/<SHOT>/`。
- approved：`local/production/<PROJECT>/approved/`。
- job/takes：`local/production/<PROJECT>/video/<SHOT>/jobs/takeNN/`。
- 后期：`local/production/<PROJECT>/edit/review/`与`final/`分开。

## 交付状态必须分层

`contract_ok`、`reference_approved`、`keyframe_approved`、`runtime_success`、`visual_accepted`、`final_approved`是不同事实，不能互相替代。

每次写清新增文件、验证方法、实际运行结果、仍未完成内容。不得把本轮容器CPU测试当成用户Windows/GPU测试。不要删除历史Lab审计。

## Git与权限

不提交大模型、密钥、第三方原图、批量成片。用户已生成素材随交付包提供，Git只保存可追溯登记。保留本地未提交修改，不运行reset/clean清除工作。新代码先跑离线测试再提交；涉及用户具体批准的写入必须如实记录。

## 与V3新增工作的协作

`project_preflight.py`、`register_asset.py`、`validate_schema.py`及schemas保留，原preflight可做知识层盘点，但不替代V5媒体合同。人物方向状态是PREPROD_MODEL_DIRECTION_APPROVED，非FINAL_GOLDEN_MODEL_APPROVED。每次任务结束记录完成WBS ID、Gate、Files、QA/Benchmark、Blocker、Commit、Next WBS。新模型必须Lab→固定回归→比较→批准后晋级，不能因热门自行切换。
