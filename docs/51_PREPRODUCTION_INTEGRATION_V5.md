# 51｜V3 创作基线与 V5 执行合同合并说明

日期：2026-10-06。整合基线：`114523857ece96d5f4f11179af7d0141b9b8b8dc`。

## 为什么有这一页

本轮准备工作开始时 main 为 `f3d9d3b59525efff372f3d60d3982ff2b09a545b`；提交前，另一路提交了 V3 摄影/表演/服装/声音/第一季与WBS文档。**本次在新的1145238基线上合并，保留新文件，不用旧tree覆盖main。**

V2是主技术路线，V3是创作知识层，V5是本轮可检查的制作合同与工具版本。编号不是要本地重装五次系统，也不是五套并行生产线。

## 唯一执行入口与职责

1. 阅读本页 → `docs/30_PREPRODUCTION_V5_EXECUTION.md` → `docs/preproduction/LOCAL_COMMANDS_V5.md`。
2. 美术、摄影、表演、声音、第一季创作继续参考原有 `docs/30_VISUAL_DIRECTION_BIBLE.md`、31、32、34、38以及 `episodes/SEASON01/`。
3. WBS、风险、分工与阶段验收继续保留 `docs/40–50` 对应文件。
4. 当前两部片子的具体镜头ID、出场角色、时长、静动态方式，以各集 `production_plan_v5.json` 为机器执行事实。旧YAML不是同时运行的另一张时间表。
5. 具体素材与批准，以 `generated_assets_v5.json` 和 `approval_manifest_v5.json` 为准。旧空批准表/方向认可不自动迁移成USER_APPROVED。
6. `project_preflight.py`、`register_asset.py`、`validate_schema.py`继续保留。preflight可用于旧知识层盘点，但其PASS不能代替本轮逐文件hash与实际I2V链路校验。V5提交以guard/prepare为准。

## 服装名称对照：不重新设计用户刚认可的人物

| 现有镜头兼容名 | V3 canonical | V5使用规则 |
|---|---|---|
| DAIYU_CLASSIC_OUTDOOR | DAIYU_CANONICAL_LAVENDER | 相同淡紫古典系列，具体引用须获批 |
| DAIYU_CLASSIC_HOME | DAIYU_CANONICAL_HOME | 居家轻古装，不现代睡衣 |
| DAIYU_CLASSIC_RAIN | 外出同衣 + 雨中湿度 | 不凭空换发髻或披风 |
| WUKONG_CLASSIC_OUTDOOR | WUKONG_DZS_DAILY | 黄/灰/棕日常层、轻冠/帽、念珠；不默认重甲 |
| WUKONG_CLASSIC_HOME | WUKONG_DZS_HOME | 居家轻层，无重肩甲 |
| WUKONG_CLASSIC_INJURED | WUKONG_DZS_HOME + injury state | V5进一步明确左手背及绷带 |
| WUKONG_DZS_FORMAL | WUKONG_DZS_FORMAL | 明确写FORMAL的镜头才用正式金红甲装 |

LOOKREEL01的COMP09花束主视觉明确选FORMAL；EP001的市场、公交与日常OUTDOOR保持DAILY。`WUKONG_COSTUME_CROP`来自重甲设定板，所以登记为FORMAL，**不能把这张裁片当作日常DAILY已获批的衣服**。HOME与DAILY的具体引用仍待选择/确认；不以非空ID假装已经有图。

## 审批与试拍边界

用户说“感觉可以，继续”已支持继续非本地工作，不再把整个项目停在“还不能写剧本”。但新图的具体身份/衣服与镜头批准仍需真实记录。

可在三张合适关键帧获批后做局部T1，不必等剩余七张。完整LOOKREEL01仍要求十镜全部通过。此处调整的是先后依赖，不取消Visual Lock与逐图批准。

## 代码兼容与回退

本轮核对1145238中的旧guard、queue、approve、package-validator仍是最初版本，故使用已测试的V5实现替换；新增preflight/ledger/schema工具不删除。老命令行参数会明确报错，不静默读取错版manifest。

既有 `p1_comfy_probe.py` 和生产候选workflow保持原样；没有替换模型或custom node。Git历史与Lab记录完整保留。确实需要复现旧工具时从原commit检出到隔离Lab目录，不能把旧批准逻辑拿回正式生产。

## 验证与交付

离线53项测试针对V5执行层，不代表自动审查了全部V3新增文档或用户GPU。素材包是补充包，不是完整Git仓库；先拉取合并后的main，再导入包内17项原图/裁片。不要用部分ZIP覆盖整个工程。
