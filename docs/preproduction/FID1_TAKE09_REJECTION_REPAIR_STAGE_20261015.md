# FID1 take09真实拒绝后的完整修复与SH903下一次受控试拍合同

STATE: PLAN_COMMITTED
TASK: c2c_fid2
BASE_BRANCH: codex/fid1-remote-repair
AUDITED_BRANCH_HEAD: 778cfec2dbcd13d51b8d0c7c832e46347d008675
ACCEPTED_ENGINEERING_BASE: 1bd1c6e1cc5b47d4fccf18766f42fdb61c0221ad
ACCEPTED_TAG: fid1-v0.1.1
PR: https://github.com/Jovifei/AI-short-vidio-claw/pull/12
SCOPE: T1_SOURCE_ONLY
STATUS: HUMAN_CHANGES_REQUIRED; DOWNSTREAM_SH901_SH902_BLOCKED

> 该文档是网页侧只读审查后提交的**完整本地执行合同**，不是已经改代码、运行GPU或实现修复的声明。本次只创建此docs文档。由E盘Codex在同一大阶段内执行审核→必要实现→回归→本地综合复审→一次有界试拍→证据与人工QA→固定中文Commit/版本/CI；网页侧在固定新实现SHA回传后独立复审。不得凭源图获批、CPU绿灯或视频可播放宣称视觉通过。

## 0. 已实际读取的事实/证据

1. C2C工作区04f9cfdf549f/AI-short-vidio-claw，分支codex/fid1-remote-repair，当前短HEAD778cfec，GitHub PR12 open/unmerged、40位HEAD `778cfec2dbcd13d51b8d0c7c832e46347d008675`。本地仅有未跟踪tasks/todo.md、tasks/lessons.md，不纳入Git。
2. `local/reports/TAKE09_REJECTION_20261015.md` 与真实 `local/review_evidence/FID1_SH903_TAKE09_FEEDBACK.json` 一致。反馈SHA256 `e09b6471ee2b9a9fcbf78248466355a81407f0e057f93b975e00ef821a30b473`；用户原话：“人物的头并没有任何的移动，然后背景的话也虚幻糊掉了，所以说需要去修改。你自己也能检查出来这些画面的区别。”
3. `local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09/qa/qa_report.json` 已实际记录 `CHANGES_REQUIRED`：full_playback/identity/limbs=CHANGES_REQUIRED，costume=PASS，decision=CHANGES_REQUIRED，后续门禁 `BLOCKED_CHANGES_REQUIRED`；这是已应用的**真实用户反馈**，不要再将take09称为PENDING。报告中遗留的 `human_full_playback:PENDING` 是旧顶层显示字段，与 `visual_review.full_playback` 不一致；下阶段应修正状态读取/显示派生，不能修改旧take09字节来“修复历史”。
4. V005源图 `REFB02_01.png`，SHA256 `6476cf1e17105b3589095918a46546baced0db35ef2a6ca235551f4b7002149f`；输出视频SHA256 `dbdd44e4bdd39b13c8881c3f413a7889f0823c052b99df41698b1d5f61be2db8`。Wan2.2-TI2V-5B、576×1024、49帧/24fps、13 latent时格、seed2026100803、20 steps、CFG5、uni_pc/simple、denoise1、ModelSamplingSD3 shift8；本地take09运行719.809秒、采样VRAM峰11808MiB、采样最低物理可用RAM约10.8MB。该RAM指标显示很小的安全余量，不得直接开拍。
5. 真实V005 `positive_prompt` 含 `An almost motionless portrait`、`hold the starting pose throughout`、`Motion limited to faint water ripples and tiny fabric breathing`；`negative_prompt` 含 `head rotation`、`pose changes`、`hand movement` 等。它们和用户要求头部自然微动直接冲突。
6. 真实Comfy API图：LoadImage 56→Wan22ImageToVideoLatent 55；ModelSamplingSD3 48→FID1WanTimestepAwareROIAnchor 59 MODEL输入；latent55→FID1 59 LATENT输入；FID1输出MODEL0、LATENT1分别进KSampler3相应端口→VAEDecode8→CreateVideo57→SaveVideo58。并非只出现“reference”关键词。
7. 实际节点 `scripts/fid1_wan_latent_anchor_node.py`：`anchor_future_rois_timestep_aware` 保持Wan基础noise_mask（slot0=0，future=1），将首格source拷贝到未来ROI（alpha>0处），在克隆MODEL的KSampler hook用 `denoise_mask*(1-alpha)` 抑制未来ROI更新；`scale_latent_inpaint` 用生效ModelSamplingSD3的 `noise_scaling(sigma,noise,latent_image)` 对齐sigma。非ROI仍可生成，ROI内部较稳定。feather_latent=4是**空间**衰减不是时间衰减；目前没有明确支持“头部自然转动”的时序松弛机制。
8. take05/take07的场景马赛克/伪文字与改动Wan条件mask有关，V005修复其全场景坍缩但仍有视觉缺陷。不能把这三个实验误当“加大噪声/减小掩膜必定改善模糊”的证明。本轮网页没有可验证完整MP4回放/逐像素客观比对，因此对背景糊的机制只给可检验假设，不给已证实根因。
9. E盘记录：当前8188无监听、4070SUPER可用显存约10GiB、RAM可用约6.7GiB，均为可能漂移的观察值；上一次采样VRAM峰11808MiB大于本次声称空闲VRAM，说明没有新的资源门槛检查不能试拍。

## 1. 工程诊断与优先假设

- **H1：明确的提示词抑制（已由源码证实、效果幅度待验证）**：禁止head rotation/pose changes、almost motionless与需求冲突。最小变更应该先只改变“运动语义提示”而保持ROI算法、ROI坐标、seed等完全相同；这能明确估算prompt的贡献，但不能保证突破强ROI锁。
- **H2：持续ROI采样保留造成面部运动受限（机制已证实、影响程度待实验）**：中心alpha=1等于未来时格在采样过程中完全保留source面部局部，不具备明显刚性转动自由度；靠提示词未必能产生头动。应在H1未改善且诊断通过时执行**预先限定的第二个单变量实验**：只改变ROI的未来时间衰减，不触碰Wan基础noise_mask和非ROI；若这种方案破坏身份则立即停止，不循环试参。
- **H3：背景变糊/细节衰减（原因未确认）**：可能涉及生成网络的帧间信息变化、源图-视频对齐、输出编码、decoder及非ROI自由生成，或强脸ROI与周围生成的不连续；不能从接收失败文字直接断定“mask方向反了”。必须从真实MP4全49帧和批准原图同尺度看局部背景锐度/纹理/边缘、脸部清晰度、服装、微动、首尾连续性；计算锐度/光流是辅助，不替代Jovi判断。保持VAE/model/采样和输出编码相同以免混杂。

## 2. 固定实验矩阵和可停止决策

**A / 优先执行：新SH903 V006 + 新未占用take（首选take10，仅在目录确实不存在时使用）。**
- 改动：**运动语义提示包一项**。保留V005其它JSON字段：源图SHA、width/height、frames/fps、seed、anchor_strategy、anchor_rois、feather、模型、shift、steps/CFG/sampler/scheduler和原工作流连接/实现哈希。仅 `profile_id`、`hypothesis`、`positive_prompt`、`negative_prompt` 与profile文件自身SHA随实验自然变化。
- 正向提示只改变为**轻微可观察但不改身份**：允许两位角色保持原侧脸姿态和头饰、衣服、牵手关系基础上的微小自然点头/视线微动及呼吸，水面和背景要保留清楚纹理、自然的局部运动，摄像机固定；禁止剧烈转身、口型讲话、换装、换人、重构背景。避免用“头绝对静止、hold throughout、almost motionless”字眼。新prompt需逐字保存在profile及review对照表；不要让算法自动拼装。
- 负向提示删掉笼统的 `head rotation` / `pose changes` / `hand movement` 禁令；保留具体不希望发生的 *large rotation, frontal redesign, unexpected hand separation, extra limbs, camera movement, wardrobe change*。正负两条共同组成**一个运动语义干预包**，不得把两处变化谎称两次独立物理变量。
- 预期证据：V005 vs V006同seed/source/算法/ROI/采样/尺寸，能评价解除提示束缚是否改善头动；如果仍基本不动或身份/背景变差，A判`CHANGES_REQUIRED`，停止A，不因“成功生成”放行下游。
- V006执行前，先把A的完整字段diff和边界写到README/review合同；保持旧V005+take09原字节。

**B / 有条件的第二次试拍：新V007 + 新未占用take（首选take11）**。
仅在A完整QA明确指出“提示更开放但头仍受ROI固定限制”、资源安全、且Jovi/本地执行范围允许新一次SH903试拍时实施。以V006为固定对照，仅改变**未来时格的ROI保护强度随时间递减**，不改变prompt、ROI空间边界/feather、seed或采样。建议预注册简单单调非增时间权重，例如对future时格t=1..12，前四格1、随后线性降到0.6，最后四格保持0.6；属于诊断候选而非已证明最佳数值，优先实施为profile显式的 `temporal_anchor_schedule` 数组且仅经严格验证进入新节点策略。不得悄悄给V005 strategy改变默认语义。
- 新 `wan22_timestep_aware_future_roi_v3` 或等价新受控策略必须映射到真实节点输出MODEL/LATENT；修改节点/KSampler patch时确保同一future ROI source latent值和掩膜时间权重一致，source首格仍不变。若中途的内部实现需要与原base的条件mask交互，拒绝该路线，不能重复take05/take07的全场景坍缩。
- 12个future时格对应49视频帧的12个非首时间位置（总13个latent时格）。对每个future时格只对已批准ROI使用alpha=spatial_alpha×temporal_weight；区域外仍为alpha=0，基础LATENT.noise_mask仍为原Wan mask，首格仍完全保留。绝不“复制未来零latent”、修改全帧mask或把默认模型路径换成另一模型。
- 仅当真实Torch CPU数学/负例、Graph+prepare/submit+deploy兼容、同SHA CI、资源前检全部通过，才允许B作为**单次**受控GPU试拍；B后不自动继续修改w值/羽化或执行take12。B必须与V006产生独立profile+node代码hash，旧待执行job失效而旧完成任务保持只读。
- 若A视觉明显改善，**不执行B**。若A失败且资源不足或B合同未通过，报告停止点，不自作主张刷GPU。

注：两次GPU均为上限条件试验，不是每阶段必须消耗2次。计划允许在真实资源阻塞时只完成工程交付，不宣称已跑过试拍。

## 3. 文件级改动与当前入口合同

| 文件 | A必做 / B条件实现 | 严格边界 |
|---|---|---|
| `config/source_fidelity_trials/SH903_FID1_V006.json` (新增) | A：基于V005另存，新prompt与diff冻结，schema4保持；`hypothesis`清楚写唯一运动语义干预 | 禁止覆盖V005 |
| `config/source_fidelity_trials/SH903_FID1_V007.json` (仅B) | B：版本独立、仅时序权重/策略差异，字段精确限制 | 不混入再次prompt修改 |
| `scripts/source_pilot.py` / `scripts/preproduction.py` | A原则上零实现改动；B若需新schema/strategy，严格字段白名单、策略映射、hash冻结和拒绝错误时间权重 | 不影响普通V5/default与现有schema1–4 |
| `scripts/fid1_wan_latent_anchor_node.py` | A零改动；B只加有界时间alpha，不在Wan原mask加空间冻结、不影响旧strategy | 不改首帧、非ROI、metadata、noised_source轨迹语义 |
| `scripts/fid1_graph_audit.py` / `scripts/submit_prepared.py` | A按原严格真实graph接线；B新增策略要检查MODEL/LATENT到KSampler真连线、profile/schedule frozen SHA、空队列/runtime节点socket | 不接受关键词、caller bool作证据 |
| `scripts/fid1_deploy.py` | A以verify为主，原则上不部署；B如果节点变化按原幂等deploy/manifest/rollback安全流程，核对Comfy源码commit、先验证后单实例重启 | 不覆盖未知plugin、不自动重装平台 |
| `scripts/fid1_qa_report.py` / `scripts/fid1_visual_feedback.py` | 工具尽量复用；QA可新增同尺度对比/帧映射/运动测量的衍生报告，不改变旧QA | 用户真实意见独立，不能自动PASS |
| `tests/test_fid1_profile_schema_unittest.py`、`tests/test_fid1_timestep_aware_node_unittest.py`、`tests/test_fid1_graph_audit_unittest.py`、`tests/test_source_fidelity_profile.py`、`tests/test_fid1_qa_report_unittest.py` | A/B相应语义diff、真实Torch CPU数值/负路径、无Torch prepare/CLI/QA、submit防重和依赖漂移、正常旧策略回归 | 不能只写新helper或Fake shape |
| `docs/reviews/20261015-fid1-motion-repair/` 与运行期local/reports | A/B冻结对照、批准图/视频和hash、精确配置diff、资源、真实测试/CI、红绿与复审、视觉反馈；真实MP4可保留本地并提供manifest，不强制提交大视频 | 不把source微动诊断当正式30镜交付 |
| `VERSION.json`、`CHANGELOG.md`、`AGENTS.md`(必要时) | 真实工程实现时中文commit，按兼容性增补patch/minor版本，最终不可变tag; 本docs提交不改版本 | v0.1.1标签不移动 |

A和B无论哪一个都必须让 `source_pilot.prepare_trial` 生成新job而非覆盖旧job；`submit_prepared.py`默认dry-run，明确 `--execute` 才允许新任务，GPU并发1；history未知绝不二次POST。当前版本 `FID1_DEPENDENCY_FILES` 的实际hash不可遗漏；实现改动引起新依赖hash时，尚未提交job须作废并另起新take。

## 4. 数据不变量和拒绝路径

- scope必须`T1_SOURCE_ONLY`，shot必须SH903；approved source/hash/identity/costume裁片/原source批准快照不变，不改原LOOKREEL01/EP001 plans/registry/approval。
- 工作流为当前Wan2.2-TI2V-5B，576×1024、49/24、batch1、13latent slot、48通道、ModelSamplingSD3 flow shift8/1000，steps20 CFG5 sampler uni_pc scheduler simple denoise1。真实MODEL和LATENT两路必须进入KSampler。哈希覆盖profile、源码、workflow、input、source批准和依赖。
- 新A任务不可选以前已存在的take或非 `video/SH903/jobs/takeNN` 路径；旧take01–09全部只读。take09的human审片已是`CHANGES_REQUIRED`；仅由其所拒绝的输出不能解锁SH901/902。
- 负例应拒绝：任何NaN/Inf、全冻结ROI、超过既有ROI数量/面积/坐标上限、时间向量不是12个、非有限/越[0,1]/非单调限制、wrong device/dtype/channel/time、未保持首格、非ROI被改、Wan base mask被改、alpha应用两次、错连sampler、旧node hash、依赖漂移、视频hash或predecessor receipt漂移。
- 如果B真实数学数值需要改变sigma采样hook，必须保留噪声轨迹对齐及metadata；测试首格0保护、未来ROIs逐格的alpha、非ROI仍可生成；计算失败拒绝提交。不能由“mask字段存在”推出生效。
- 真实反馈`record-review`使用已实现的锁、run原始快照、preview双hash pin、发布恢复标记；`CHANGES_REQUIRED`与`PASS`单项分开。V006/V007运行与视觉接受互不替代。

## 5. E盘连续执行步骤及准确命令

### 5.1 安全起点和基线冻结（不删除任何本地数据）

```powershell
Set-Location E:\project\AI-short-vidio-claw
$Accepted='1bd1c6e1cc5b47d4fccf18766f42fdb61c0221ad'
$Start='778cfec2dbcd13d51b8d0c7c832e46347d008675'
$Plan='<此文档提交的40位SHA>'
if ((git branch --show-current).Trim() -ne 'codex/fid1-remote-repair') { throw 'wrong branch' }
git rev-parse --show-toplevel
git status --short
git fetch origin codex/fid1-remote-repair
git cat-file -e "$Plan^{commit}"
git diff --name-only "$Start..$Plan"
# 只有本文档新增才允许安全fast-forward；原tasks等不跟踪文件保留。
git merge --ff-only $Plan
git rev-parse HEAD
```

先完整读取AGENTS.md、START_HERE_LOCAL.md、上一工程R1–R4报告、此计划、真实反馈以及本地Obsidian相关记录；记录旧take01..09、源图、批准、Comfy节点和原正式30镜的受保护SHA清单与数量。旧take09反馈/QA现在已经是用户明确拒绝，冻结**当前状态**而不是用旧20261013历史PENDING副本覆盖。

### 5.2 生成受控profile和静态验证（无Torch可执行）

```powershell
python -m unittest discover -s tests -p "test_fid1_profile_schema_unittest.py" -v
python -m unittest discover -s tests -p "test_fid1_graph_audit_unittest.py" -v
python -m unittest discover -s tests -p "test_source_fidelity_profile.py" -v
python -m compileall -q scripts tests
git diff --check
```

新增合成fixture覆盖A：V006相对V005只有prompt语义+profile_id+hypothesis；真实源图hash/seed/ROI/fps/model/sampler不变；B单独覆盖12项时间schedule且prompt==V006，历史schema1–4保持。无Torch subprocess显式阻止 `torch` 导入仍能执行prepare/dry-run及只读review工具，不能把skip称为成功。

### 5.3 A:新job prepare及dry-run（正式一次运行前）

```powershell
python scripts/fid1_deploy.py verify --root . --comfy-root local/comfyui/image/ComfyUI

python scripts/source_pilot.py prepare --root . --shot SH903 --seed 2026100803 --out local/production/T1_SOURCE_PILOT/video/SH903/jobs/take10 --trial-profile config/source_fidelity_trials/SH903_FID1_V006.json

python scripts/submit_prepared.py --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take10 --url http://127.0.0.1:8188
```

命令中的take10仅当未存在时使用，否则**先枚举已存在take并改用新的unused take**，不可覆盖。prepare成功只能说明冻结合规，**不能马上加--execute**。

### 5.4 本机资源/Comfy前检（不满足则安全停止）

1. 重新核对Comfy实际目录与启动脚本、源commit `6b747c0428c343e1417219641db93a4fb7cb69ae`、模型/VAE/text encoder、custom node对象 `/object_info/FID1WanTimestepAwareROIAnchor`、唯一服务进程和空队列；当前8188无监听不能当服务就绪。
2. 真实监测 `nvidia-smi` 的总/空闲/占用/其他进程、CPU RAM可用、pagefile/磁盘、GPU时序峰、环境版本。历史峰11808MiB与最近空闲约10GiB存在张力；先降低其他内存占用/检查受支持CPU-offload设置和既有Comfy运行条件，**不得为了开拍私改模型/分辨率/采样预算**。
3. 当显存/内存不足，出资源报告并停止单次GPU；不得靠强制重试、并发或脚本忽略OOM/掉驱动恢复。资源条件由本机实测与既有成功环境对照判断，不依据网页猜测。
4. 保存预检快照与唯一GPU任务锁。状态未知先检查queue/history、submission_intent及run_record；不是重新POST。

仅在预检过、dry-run/hash通过、无历史POST、用户有界本机试拍授权有效时才单次执行：

```powershell
python scripts/submit_prepared.py --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take10 --url http://127.0.0.1:8188 --comfy-root local/comfyui/image/ComfyUI --execute
```

A完成后一次执行实际QA（已有命令，不能覆盖已有QA）：

```powershell
python scripts/fid1_qa_report.py create --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take10
python scripts/fid1_qa_report.py review-page --root . --job-dir local/production/T1_SOURCE_PILOT/video/SH903/jobs/take10 --out local/production/T1_SOURCE_PILOT/review_sessions/SH903_take10_NEW
```

### 5.5 B:仅条件解锁

A的完整QA和视觉检查未通过“能辨认的微小头动”而又未发生大面积坍缩时，依照第2节预注册权重实施V007、真实CPU测试、graph/prepared job/hash/deploy及CI，再按第5.4重新资源检查，使用新unused take（首选take11）单次采样、QA。若A表现良好、资源不足、数学验证失败、发生马赛克/身份断裂，B=NOT_RUN并说明停止原因。不可从A自动连发B/SH901/SH902。B不能使用已prepared旧A任务的SHA，也不覆盖旧图/节点部署manifest。

## 6. QA对照必须完成的输出

新stage目录至少包括 `baseline_manifest.json`、`profiles_diff.json`、`graph_audit.json`、`resource_preflight.json`、`actual_run_record.json`（脱敏）、`ffprobe.json`、`full_decode.txt`、`qa_report.json`、`first_middle_last.png`（帧1/25/49）、`all49.png`、`frame_hashes.json`、`frame_motion_metrics.json`（仅辅助）、`human_review_template.json`（默认空）、`tests_local.txt`、`tests_comfy_cpu.txt`、`ci.json`、`final_diff_review.md`、`protected_hash_comparison.json`、`README.md`。保留prompt_id与视频SHA/bytes/49帧/24fps/576×1024/完整解码、峰值VRAM及最低RAM、ffmpeg/ffprobe版本。
- 完整观看原图、take09和新take，在同分辨率对比头部位移（相对肩/头饰，不把镜头漂移充作头动）、身份相似、眼神与头饰、脸部清晰、两人牵手关系、袖纹与背景边缘清晰度、连续运动/闪烁/拼块。客观指标可用ROI局部Laplacian方差、边缘保留率、首尾光流/特征追踪的趋势，但不能自动把数值转换视觉PASS，也不能把整个静图平移当头动。
- 接受条件：无scene-wide mosaic/伪文字/硬贴片；存在可辨认、自然且有界的头/表情微动；背景和服装细节没有无法接受的额外糊化；角色身份、服装、手/肢体关系与源图一致。满足基本媒体/工程门槛之后**仍须Jovi独立对full_playback/identity/costume/limbs逐项明确判断**。UI默认不勾，真实反馈经preview + pinned apply；SH901只有具体新视频真正 `ACCEPTED_FOR_NEXT_SOURCE_ONLY_TRIAL`才可能解锁。
- 若新视频只是runtime/ffprobe PASS，但头仍不动、背景糊、身份漂移、手异常或静态硬贴片，视觉状态为 `CHANGES_REQUIRED`，停止后续GPU，保存失败take，不再次调用模型去碰碰运气。

## 7. 全量测试、CI及独立复审

必须在新实现固定HEAD执行，而非套用旧1bd/fid1-v0.1.1绿灯：

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
local/comfyui/image/venv/Scripts/python.exe -m unittest discover -s tests -p "test_fid1*unittest.py" -v
python -m compileall -q scripts tests
git diff --check
python scripts/sync_repo_media.py --check
python scripts/validate_production_package.py --project-dir episodes/LOOKREEL01
python scripts/validate_production_package.py --project-dir episodes/EP001
```

要求新增测试被GitHub Actions真正收集；CI CPU Torch有真实张量运算，不能Fake通过、不能删既有测试、不能修改旧V5守卫，四项关联Actions全部SUCCESS且新case出现在完整日志（关联HEAD、checkout合成PR merge ref分别报告）。失败要读logs后在本地同一次阶段修复并重跑；全量独立diff复审后仍有问题则先修正再完整重测。

版本规则：中文Commit，保存原 `fid1-v0.1.1` 注释标签；新工程修复如只兼容扩展可采用 `fid1-v0.2.0`，若只改prompt/实验配置而无新接口，则依据本项目版本规则选择新的兼容版本，不移动旧tag。每次更新 `VERSION.json`、`CHANGELOG.md` 并指向固定40位实现SHA/新不可变tag；不得合并main或强推。旧take09既然有已应用真实拒绝记录，保护清单必须包含其最新QA和feedback，和v0.1.1时期的PENDING快照不可混淆。

## 8. 阶段验收与停止条件

**工程可交付**：A profile/prepare/submit/QA基础链、完整测试、真实同HEAD CI、资源评估、单次试拍执行记录或真实资源阻塞及其证据、必要时B的有界实现与负路径、最终独立diff复审、旧资产保护、固定SHA/tag闭环。资源外部阻塞时可工程交付 `ENGINEERING_READY_GPU_BLOCKED`，绝不报GPU成功。

**视觉未自动接受**：新take没有Jovi实际逐项认可则 `VISUAL_PENDING` 或 `CHANGES_REQUIRED`；下游 `SH901/SH902=BLOCKED`。正式LOOKREEL/EP001 20张剧情图及30镜原批准仍各自独立。

**明确拒收**：改/覆盖旧take或V005、未冻结source/hash、同时改prompt+ROI+seed+model而无法归因、V007弱化Wan base条件mask、未初始化未来ROI或first slot被动、非ROI冻结/全场景静图、错连Sampler、缺真实Torch测试、无Torch入口抛异常、未知history重POST、未做资源检查依然GPU、GPU效果被自动记PASS、生成后擅自运行SH901/SH902、CI不是新HEAD、测试未被收集、伪造用户意见、版本标签被移动、使用英文单独Commit违反用户版本策略。

本地一次完成后回传：

```text
[C2C] STATE: EXECUTED TASK_ID:c2c_fid2
PLAN_SHA:<本docs提交40位SHA>
IMPLEMENTATION_SHA:<新40位SHA>
TAG:<新不可变tag及其解析出的40位SHA>
EXPERIMENT_A:<profile/take/真实状态或资源BLOCKED>
EXPERIMENT_B:<NOT_RUN或条件性执行的独立结果>
TESTS:<全量pass/skip；Torch CPU；无Torch；失败及修复>
CI:<同HEAD四项run_id/job_id/checkout_sha/实际结果>
PROTECTED:<起止hash对比，当前take09真实拒绝未损>
MEDIA:<每次视频prompt_id/hash/ffprobe/decode/帧/资源>
VISUAL:<Jovi真实判断或PENDING/CHANGES_REQUIRED；不自动PASS>
GATES:<SH901/902及正式30镜仍关闭/仅真实接受后改变>
REVIEW:<本地独立最终diff审计及网页下一轮审计所需证据>
```

本网页侧本轮只提交本文docs。未修改业务代码/工作流/已批准配置，未使用GPU，未产生新视觉认可。
