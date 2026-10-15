# FID1 / FID2：并行计划冲突对账与唯一下一阶段执行合同（2026-10-15）

STATE: RECONCILED_PLAN
TASK: c2c_fid2
SCOPE: T1_SOURCE_ONLY
BRANCH: codex/fid1-remote-repair
PR: https://github.com/Jovifei/AI-short-vidio-claw/pull/12
AUDITED_REMOTE_HEAD: 73248825bc8d17c0c2969518383d654a9847d9b8
ACCEPTED_ENGINEERING_BASE: 1bd1c6e1cc5b47d4fccf18766f42fdb61c0221ad
ACCEPTED_TAG: fid1-v0.1.1
NEW_GPU_IN_THIS_RECONCILIATION: NOT_AUTHORIZED / NOT_RUN
LATEST_REAL_USER_RESULT: SH903 take09 = CHANGES_REQUIRED
FOLLOW_ON: SH901 / SH902 = BLOCKED

> **唯一有效的新实施合同**：本文件只为冻结现状、消除两条并行技术路线的身份冲突，并让同一个E盘Codex工位连续完成工程闭环。它不是业务修复、GPU运行、CI通过或用户视觉接受的证明。两份旧计划仍原样保留为历史依据，但其与本文冲突的候选编号、策略/配置复用和自动GPU步骤均停止适用。网页仅提交这一份docs Markdown，不修改本地暂存区、仓库业务代码、既有source/job/QA/媒体、VERSION、标签或PR元数据。

## 0. 实际核对的版本谱系与状态（不得重写）

- GitHub PR12真实HEAD为73248825bc8d17c0c2969518383d654a9847d9b8，Open/Unmerged。历史关系：778cfec2dbcd13d51b8d0c7c832e46347d008675 → fea10412233353a2931d338cc30832accccf0d66 → d47f3adabf2269b6ae80bb77c7ab080b663d40f1 → 73248825bc8d17c0c2969518383d654a9847d9b8。对比确认fea到732只增加较新的计划文档，不包含代码实施。
- C2C工作区04f9cfdf549f/AI-short-vidio-claw，分支相同，短HEAD7324882；当前**已有约58条已暂存的本地工程/证据变更**，另有tasks/lessons.md、tasks/todo.md两项未跟踪Owner笔记。它们仍在E盘索引/工作区，不是GitHub上已提交的实施，也不是网页方可以覆盖/清除的对象。不可reset、clean、stash丢弃、强推；接收新文档必须保留这些已暂存修改。
- 并行计划一：docs/preproduction/FID1_TAKE09_REJECTION_REPAIR_STAGE_20261015.md（fea104...）将A定义为V006/schema4的提示词对照，将B定义为V007/schema5的未来12格时间衰减。**其中A已执行、B仅CPU工程候选；禁止按旧文字再次执行同一take。**
- 并行计划二：docs/preproduction/FID1_SH903_TAKE09_REJECTION_MOTION_DETAIL_STAGE_20261015.md（较新732...）要求“perROI preserve_strength”却继续占用V006/schema5/v3命名，和上述**已冻结的V006与V007**冲突。这段命名和同一次试验的多重方案无效，不得按它覆盖profile、变更job或部署已有v3。
- 已接受的v0.1.0与v0.1.1标签/commit只属于既往工程，不授予take10新视频视觉接受。GitHub目前没有fid1-v0.2.0标签；本地VERSION.json暂存0.2.0仅是**未发布工作版本**，不可宣称已发布、已CI或已验收。

### 0.1 已发生的实验，不许再计划成“尚待执行”

| 资产 | 当前真实事实 | 保护/处理 |
|---|---|---|
| SH903_FID1_V005 / take09 | Wan5B真实媒体，输出SHA dbdd44e4bdd39b13c8881c3f413a7889f0823c052b99df41698b1d5f61be2db8。Jovi明确CHANGES_REQUIRED；服装PASS，完整播放/身份/肢体不通过；下游关闭 | 保存已应用的QA与原始用户反馈，不得恢复旧PENDING副本 |
| SH903_FID1_V006 / take10 | **schema4、strategy=wan22_timestep_aware_future_roi_v2、prompt-only干预**；确实POST一次，prompt_id cb0a1e46-3422-477b-93a4-1805ec4869bd，117.773s，输出SHA 32e93baca62c6a95d63433a526f85dc78fec239f9e8f09b64cd34509a6663435，821029 bytes，49帧/24fps/576x1024、解码PASS。本地观察头仍偏固定/叠影、背景更软化；**Jovi未对take10作最终人审** | profile、job/workflow/run/video/QA/源图/审核session冻结，只读保留；不能把本地观察写成Jovi的CHANGES_REQUIRED |
| SH903_FID1_V007 | **schema5、strategy=wan22_timestep_aware_future_roi_v3、class=FID1WanTemporalROIAnchor**，12格权重 [1,1,1,1,.9,.8,.7,.6,.6,.6,.6,.6]；真实CPU工程候选 | 保留暂存代码和V007 JSON，不改其含义，不将其静默转换成strength |
| take11 / take12 | 已prepared的历史包；因脚本依赖hash漂移拒绝，不能重封/复投 | 保留作拒绝证据 |
| take13 | 由V007准备，dry-run返回submitted=false，未生成新prompt/MP4；对应v3插件未安装，B的执行资源门禁拒绝 | **保留冻结job；不更新其dependency hash，不自动deploy/POST**。后续加v4代码自然会令未运行包失效 |
| 现有Comfy插件 | SHA c1d4c573a1e6bbd63793398293be16f3b7a6a2a3042d3340f08dc8870cb2e0b3，为旧节点；未部署V007 | 不得将“本地源码含v3”冒充“服务已加载v3” |

- 本地已暂存阶段的日志显示：全量349 tests，346通过/3既有Windows权限skip；Comfy CPU107通过。这**不是同一固定GitHub实现HEAD的CI验证**；docs/reviews/20261015-fid1-motion-repair/ci.json仍写PENDING_FIXED_HEAD。因新增v4代码，最终完整测试要重新跑。
- A取样VRAM峰11084MiB、物理可用RAM最低42385408字节（约40MiB）；B预检RAM 7774740480字节（约7.24GiB）低于现有8GiB硬门槛，旧插件SHA也不符。新资源截图若不充分，一律阻止GPU。A使用fast-disk、reserve-vram1，与旧take09运行环境有差别，不能单凭对比视频将清晰度差异完全归因于提示词。
- 局部静态背景树木指标：take09最后一帧Laplacian方差约106.08，take10约65.46；来自本地局部crop辅助指标，不是视觉通过或某一组件导致模糊的因果证明。Jovi原始关注头运动、人物身份/肢体及背景糊，必须全部保留为后续QA目标。

## 1. 单一决策：不跑V007，以全新V008/schema6/v4为唯一“下一候选”

### 1.1 选定策略

本阶段**唯一新增候选**：
- Profile：config/source_fidelity_trials/SH903_FID1_V008.json（新文件，既有V001–V007不动）。
- schema_version：**6**（不能继续把schema5拿来改语义）。
- anchor_strategy：**wan22_timestep_aware_roi_strength_v4**（不能挪用wan22_timestep_aware_future_roi_v3）。
- Comfy类：**FID1WanStrengthROIAnchor**（独立类名，不覆盖FID1WanTemporalROIAnchor或FID1WanTimestepAwareROIAnchor）。
- 下一次可准备的目录仅建议 local/production/T1_SOURCE_PILOT/video/SH903/jobs/take14；当前目录枚举实际只有take01..take13。**本轮只立合同，不能创建take14、POST或部署。**本地执行前重新检查该目录完全不存在，存在则停止并另获确定的编号，绝不覆盖。
- V008的正负prompt、seed 2026100803、源图hash 6476cf1e17105b3589095918a46546baced0db35ef2a6ca235551f4b7002149f、尺寸576x1024、49帧/24fps、两处人脸坐标/feather、Wan2.2-TI2V-5B与采样预算**逐字/逐值等于V006**。只增添一种**空间逐ROI部分保留强度**机制，不使用V007的temporal_anchor_schedule字段。
- 无逐时间权重：所有future 12格的“时间系数”均视为1，但**不得把这个列表塞回schema6**；保留强度只来自各ROI自己的preserve_strength。这保证V008和V007在数学语义、配置、节点类、签名和job记录上完全不混淆。
- 一次预注册**综合质量候选**：两处face strength分别0.55，另有小型静态背景BACKGROUND_TREES strength=0.65；feather_latent均4。背景ROI是新增的几何因素，因此V006→V008变化同时包含局部保留强度与局部静态背景区，**不得宣称单变量消融，也不能把改善单独归因于strength或新背景ROI**。它旨在同时验证自然头动/叠影与局部背景细节的权衡，执行次数最多1次且仅在以后重新获准GPU时。
- **背景区必须先审查**：BACKGROUND_TREES参考框 [x0=.39,y0=.18,x1=.64,y1=.30]；两处face分别 [0.11,.20,.36,.36] 和 [.69,.20,.89,.37]。本地需从SHA绑定的941x1672批准原PNG生成叠层图，确保树木而不是动态水流/两人脸、尽量避免语义内容穿界，核验在latent H64/W36下映射后的区域、feather边缘与重叠情况。若不符合，**停止该候选**，不能就地默改已冻profile/job或自动再规划第二轮。

### 1.2 为什么不把V007当下一GPU候选

V007的前四个future latent格仍保护强度1.0，核心面部在视频前段持续全强度锁定，而take10已经证明提示放松后依然没有明显可见头动且叠影持续。V007是有效的CPU工程隔离样本，尚未作GPU证明；它的时间衰减不等同于“从第一future格开放部分生成”。逐ROI分数从全部future格开始允许部分更新，更直接对应头固定问题。此选择属于**有证据的工程优先级判断，不保证视觉效果**；没有额外GPU结果不能断言V007不可能成功。

既有v3时间节点和V007测试/配置/历史job必须保留，状态标记**ENGINEERING_ONLY / NO_GPU_IN_THIS_STAGE**，后续不能引用较新的并行计划将“perROI_strength”塞进V007的schema5或v3名称。

## 2. V008冻结数据合同与数值不变量

schema6/profile_id=SH903_FID1_V008、scope=T1_SOURCE_ONLY、shot=SH903，外层字段严格等于现有schema4的字段集合，不含temporal_anchor_schedule；anchor_rois恰好三项，每项严格字段 id,x0,y0,x1,y1,feather_latent,preserve_strength。两处face的原坐标保持；背景使用核对后固定的上述坐标，不能增大框、改换源图或改变prompt。取值：

- WUKONG_FACE: x0 .11,y0 .20,x1 .36,y1 .36,feather_latent 4,preserve_strength 0.55
- DAIYU_FACE: x0 .69,y0 .20,x1 .89,y1 .37,feather_latent 4,preserve_strength 0.55
- BACKGROUND_TREES: x0 .39,y0 .18,x1 .64,y1 .30,feather_latent 4,preserve_strength 0.65

严格拒绝：额外/缺失键、重复ROI ID、未批准source、shot不为SH903、未知source/hash、非法归一化坐标/面积超界、重复或交叠（交叠必须显式拒绝或预先确定不可歧义的max合并）、feather不在1..4、strength为bool/字符串/NaN/Inf/0/1/负值/>=1或不在[.25,.80]、错误schema/策略组合、出现temporal_anchor_schedule字段。历史schema1–5继续按原规则严格解析；尤其schema5只代表V007时间权重，绝不接受strength。

### 数学语义（明确不与时间衰减叠加）

- Wan original LATENT.samples:[1,48,13,64,36]，noise_mask:[1,1,13,64,36]；batch1、48ch、首格t0、未来12格及float/finite/device/dtype严格验证。保留原LATENT字典元数据、首格samples和基础noise_mask：原mask首格0、future全1，不能再让Wan条件编码看见空间掩膜。
- 每个ROI独立空间羽化alpha_space（中心≤1）；有效保留系数 alpha_eff = alpha_space × preserve_strength。所有future时格相同；ROI外alpha_eff=0。当前三块ROI可在latent坐标检验无交叠；如果重叠必须拒绝或以明确的预注册规则合并，不允许修改其几何以绕过重叠测试。
- 在future且alpha_eff>0的位置，将prepared.samples初始化为源首latent的**完整数值**，绝不预乘alpha，别的future/非ROI完全保持原LATENT；这是避免alpha²的必要条件。
- KSampler的denoise_mask_function仅接收Wan原base denoise mask，返回base_mask × (1-alpha_eff)。在面部核心允许约45%的去噪更新，在背景核心约35%，非ROI future为1，首格仍为0。该mask仅在克隆MODEL采样hook内使用，**LATENT.noise_mask保持原始字节/语义**。
- scale_latent_inpaint继续用当前生效ModelSamplingSD3模型sampling的noise_scaling(sigma,noise,source)，使源anchor服从sigma噪声轨迹；不能z0硬插到zt。传来的1/48通道mask必须严格检测repeat、shape/finite、保留源slot0，错误dtype/device拒绝。
- **重要已有断言**：当前 _anchor_future_rois 即使blend_alpha=False也检查“future存在mask由1→0的完全冻结像素”。全部ROI strength<1时不会存在完全0的denoise mask，这种断言会让合法schema6无条件失败。必须为新v4使用单独正值非全冻结验证（存在future alpha_eff>0、非ROI仍能denoise、无full-frame freeze），不能粗暴放宽旧v2/v3的断言或改动旧行为。
- 新class严格MODEL/LATENT输入与输出，必经KSampler MODEL0/LATENT1。FID1WanTemporalROIAnchor有单独temporal_anchor_schedule_json插口；FID1WanStrengthROIAnchor**没有此插口**，只接model/latent/roi_boxes_json。不得把两类节点注册成相同class_type。

## 3. 逐文件实施工作包（同一完整工位，无平行重复实现）

| 实际文件 | 本次工程实施与不变量 |
|---|---|
| scripts/fid1_wan_latent_anchor_node.py | 在保存v2、v3原函数行为和既有Torch测试的前提下，新增独立v4强度构建与FID1WanStrengthROIAnchor；新mask合法性按部分强度判断，原Wan mask、首格、未来ROI源初始化与sigma轨迹不动；节点类、display名独立 |
| scripts/preproduction.py | 新v4→FID1WanStrengthROIAnchor策略映射；schema6的graph真实MODEL0/LATENT1检查、严格roi_boxes_json与prompt/seed/sampling/source、禁止temporal字段；现有v2/v3分支不变 |
| scripts/source_pilot.py | 仅为SH903新增schema6严格字段/strength校验，更新策略映射与FID1_DEPENDENCY_FILES（如有新helper）；原v006/v007字节和source批准不动；prepare默认离线、原可用性不下降 |
| scripts/fid1_graph_audit.py | v4走MODEL+LATENT双边，ROI JSON含strength且与冻结profile完全一致；错误边、孤立节点、假关键词/调用方布尔不得通过；审计输出源/候选图sha |
| scripts/submit_prepared.py | v4的object_info必须识别新节点精确socket，执行锁、job/source/profile/代码依赖hash、空队列与历史检查不减弱；**把当前v3的最新RAM≥8GiB、VRAM空闲≥8192MiB门禁扩展到v4**；未知值拒绝，禁止v007/take13被当v4执行 |
| scripts/fid1_deploy.py | 保留精确插件所有权、旧插件冲突拒绝、同版本幂等、精确rollback；v4需要实际node源码SHA对应部署，不能默认旧plugin已加载，非空队列不升级 |
| scripts/p1_comfy_probe.py | 复用已有资源/历史/单POST监测，不换runner；除确有错误外不修改，保证无tzdata环境仍能稳定运行 |
| scripts/fid1_motion_qa.py、scripts/fid1_qa_report.py、scripts/fid1_visual_feedback.py | 复用本阶段已存在的同尺度源图/头部/背景定量工具、1/25/49和all49页，补充source、take09、take10、新候选的明示比较；仅诊断不自动PASS，保留take10用户PENDING与take09真实拒绝 |
| config/source_fidelity_trials/SH903_FID1_V008.json | 唯一新profile，schema6、v4，prompt和源/hash/seed/采样与V006相同，三ROI强度和geometry一次冻结，hypothesis明确“与V006相比为预注册综合改变，不单变量归因” |
| tests/test_fid1_strength_node_unittest.py、tests/test_fid1_strength_profile_unittest.py（拟新增） | 真实Torch CPU alpha/模型hook/轨迹、有效strength、背景ROI、不变量、legacy v2/v3 bitwise回归、双边图、严格负路径 |
| tests/test_source_fidelity_profile.py、tests/test_fid1_graph_audit_unittest.py、tests/test_fid1_submit_runtime_unittest.py、tests/test_fid1_deploy_unittest.py | 真实prepare→dryrun、job hash、resource floor、不部署/错误节点拒绝、stale-job refusal、旧schema1–5和V5全量回归，不删原断言 |
| docs/reviews/20261015-fid1-motion-repair/ | **现有暂存证据只读保留**；后续v4另建docs/reviews/20261015-fid1-v008-reconciliation/保存新ROI叠层/CPU测试/精确diff/资源证据；不要覆盖已有A/B证据 |
| VERSION.json / CHANGELOG.md / AGENTS.md | 现有staged v0.2.0**尚未GitHub发布**，实现闭环通过后更新为“v3时间候选保留、v4强度候选唯一下一路线”及中文commit，发布新不可变fid1-v0.2.0（前提tag仍未占用）；已发布v0.1.0/v0.1.1绝不改动 |

不得另起第二套短剧/Comfy实现工位，不切换main，不擅自修改正式30镜、已批准source素材、SH901/SH902、旧take01–13、两份冲突历史计划。旧计划只作为历史记录；不删除或改名。

## 4. 离线、CPU、真实加载、GPU四层边界和必测负路径

**无Torch离线层**：Python子进程显式屏蔽torch导入，schema6/V008解析、ROI/strength范围、source hash、API graph、source_pilot.prepare及submit默认dry-run必须通过；不联网、不模型推理、不写approval、不创建GPU intent。错误profile/策略/旧take目录必须exit非0且无新job。

**真实Torch CPU层**（本地Windows Comfy venv及CI CPU Torch）：必须使用真实Tensor形状[1,48,13,64,36]（可先用小H/W进行快测并有一条全尺寸shape正例）、dtype/device/finite正确。至少覆盖：
- alpha_eff核心0.55/0.65、羽化边0..1×强度、未来12格恒定、首格0；
- 有效强度全部<1仍通过新class；旧v2/v3原完全冻结断言及数值结果不被改变；
- ROI内future原样拷贝首格source，hook再按strength只乘一次，真实sigma/noise_scaling生成无误；ROI外future可生成，首格及元数据/原mask完全保留；
- NaN/Inf、bool、0/1、超范围、缺字段、重复ID、非法坐标、ROI交叠规则、wrong strategy/schema、带temporal字段、shape、mask1/48ch不重复、wrong device/dtype、全帧freeze、sampler绕过均拒绝。
- v3时间候选原107项Comfy CPU样本仍全部过；新增v4测试真正进test_*.py发现，不能以“349/107”旧本地结果充当新完成测试。
- 模拟Comfy object_info，老节点/错插口/实际部署SHA不匹配时拒绝；资源RAM<8GiB、VRAM<8192MiB或查询失败、队列非空、未知submission history必须在POST前拒绝。不得为通过而卸掉R1–R4证据校验/原V5守卫。

**Comfy真实加载层**：只在以后工程合规时、由本地先验证旧实例/模型/VAE/text encoder/Comfy源commit及部署清单。已安装plugin仍为旧SHA；新v4不得“只更新manifest”绕过。所有部署必须经现有owner-aware deploy/verify/rollback与单实例重启和/object_info校验；不修改Wan核心源码、原workflow模板或新平台。必须先空队列/无运行任务，未知缓存/历史状态阻断。

**本轮GPU层**：明确 **NOT_RUN / NOT_AUTHORIZED**，无--execute，无新submit intent，无新take GPU。任何未来针对V008单次SH903试拍均需要Jovi另行具体授权、最终实现固定SHA及同HEAD CI、实际部署SHA一致、队列空、历史明确、严格资源余量和现场审查。不得把本计划写作未来GPU执行的自动授权。

## 5. 资源、安全与唯一未来take规则

- A历史take10 RAM谷值42385408 bytes（约40MiB）；B现有RAM7774740480 bytes小于8589934592（8GiB）门槛。GPU型号4070SUPER，总VRAM约12282MiB。**目前无可核验的安全余量**，现在不可新GPU。旧采样VRAM峰11084MiB（take10）、11808MiB（take09）仅是5秒采样峰，不是连续最大。CPU/GPU内存管理、fast-disk、reserve-vram1、pagefile、磁盘及其他进程均须重新量测。
- 对新v4使用和现有v3一致的至少8GiB可用物理RAM、至少8192MiB空闲显存的硬拒绝；还需与A实际峰值增长量比较保留非零余量、空队列、模型路径/sha或明确bytes证据、Comfy节点加载以及实际nonce intent/history；任一未知/不足返回RESOURCE_BLOCKED，**不降低门槛或自动改变模型/帧率/分辨率**。门槛即使满足也不保证安全，更不替代另行运行授权。
- V008准备工作必须在所有代码及依赖SHA固定**之后**才选择新路径：先检查take14是否存在；目前C2C枚举仅take01–take13，故take14仅为候选名。take14目录已存在/并发写入，则STOP，不能覆盖、删掉、改名复用、自动换到take15刷试验。
- 已prepared take11/12/13不可重封、不可改历史job_integrity或sources来追新依赖；当v4代码改变时，它们自然因依赖hash不一致被拒绝。不要把旧take13执行失败写成V008实验失败。
- 如未来另获GPU授权，最多一次SH903 V008单任务，dry-run后再在资源/节点SHA和用户许可全部成立时调用已有submit_prepared --execute；状态未知先查Comfy history/queue及submission_intent，不重POST。默认输出仍属于T1_SOURCE_ONLY、不作正式成片。

## 6. E盘接收和本地一次完整工程执行顺序

**当前本地有大量已暂存变更。** 本次远端docs提交只前移GitHub分支HEAD，不会修改C2C工作区索引。执行方先用git status及git diff --cached --name-status确认保留全部暂存路径；不要先提交到旧HEAD制造平行历史。核对GitHub新PLAN_SHA只在732之后新增单个docs文件；优先安全git fetch并尝试 --ff-only 合入（未提交暂存改动如果阻止快进则**停止合并但保留暂存区**，直接用git show读取新计划；禁止reset/clean/覆盖暂存文件）。任何提交实现代码前都须保证新文档已安全纳入最终HEAD祖先或明确记录受阻，不为避免冲突推送分叉/强推。

从E盘根执行：
~~~powershell
Set-Location E:\project\AI-short-vidio-claw
if ((git branch --show-current).Trim() -ne 'codex/fid1-remote-repair') { throw '错误分支' }
git rev-parse --show-toplevel
git status --short
git diff --cached --name-status
git fetch origin codex/fid1-remote-repair
if ($LASTEXITCODE -ne 0) { throw 'fetch失败，不动索引' }
$PlanSha = '<本轮最终回传的40位文档SHA>'
git merge-base --is-ancestor 73248825bc8d17c0c2969518383d654a9847d9b8 $PlanSha
if ($LASTEXITCODE -ne 0) { throw '计划不是既有HEAD的后继' }
$diff = @(git diff --name-only 73248825bc8d17c0c2969518383d654a9847d9b8 $PlanSha)
if ($diff.Count -ne 1 -or $diff[0] -ne 'docs/preproduction/FID1_FID2_PLAN_COLLISION_RECONCILIATION_20261015.md') {
    throw '计划提交包含非docs业务修改'
}
git merge --ff-only $PlanSha
if ($LASTEXITCODE -ne 0) {
    Write-Host '暂存区保护：未快进，停止Git写操作。可用 git show 浏览已获取的固定计划；不reset/clean/stash。'
    throw '需要本地安全协调暂存区'
}
git rev-parse HEAD
~~~

接收后一个本地Codex工位连续执行：
A. 冻结source/profiles V001–V007/takes01–13包括take09已拒绝与take10用户PENDING、原审批与32PNG/Comfy插件/Obsidian的当前hash；确认所有冻结job及用户证据保护。
B. 仅增新v4策略/schema6/V008，保留已暂存v3时间机制原样；先合成CPU负例和旧v2/v3回归，再跑源图背景ROI叠层与source hash核对。
C. 先小套件、无Torch、Comfy venv真实Torch，再全量；独立审查完整 staged+unstaged diff，失败同一阶段修复后重跑；不能只说“本地初测349/107”。
D. 安全生成新V008 profile/graph；只在所有实现SHA固定且目标目录不存在时offline prepare新take14，校验默认dry-run绝不POST；**本阶段到此停止GPU**。
E. 更新VERSION.json、CHANGELOG.md（中文）、提交明确文件列表到同一PR12实现分支，读真正实现HEAD的四项Actions及新测试完整日志，修复至绿；再固定40位提交与不可变新tag（若fid1-v0.2.0仍无tag且兼容，则用它；禁止移动v0.1.0/v0.1.1）。
F. 本地独立终审并回传新实现SHA、tag、tests/CI、artifact/保护hash、V008工程准备情况/资源阻塞；网页侧再只读独立审查。不把新工程接受冒充视频视觉接受。

命令清单（实际次数、exit code、环境须留证）：
~~~powershell
python -m unittest discover -s tests -p "test_fid1*unittest.py" -v
python -m unittest discover -s tests -p "test_source_fidelity_profile.py" -v
python -m unittest discover -s tests -p "test_*.py" -v
.\local\comfyui\image\venv\Scripts\python.exe -m unittest discover -s tests -p "test_fid1*unittest.py" -v
python -m compileall -q scripts tests
git diff --check
python scripts/sync_repo_media.py --check
python scripts/fid1_deploy.py verify --root . --comfy-root local/comfyui/image/ComfyUI
~~~

部署verify如因旧插件节点不符而拒绝是**真实阻塞**，不是要求现在执行rollback/install。V008离线prepare可在无Comfy运行时完成；submit默认dry-run只做离线合约，不执行POST。正式两集launch readiness可能因原30镜缺精确素材继续不通过，必须如实报告，不调假批准。

## 7. QA与证据打包（现在准备标准，不能造新媒体）

新增目录建议docs/reviews/20261015-fid1-v008-reconciliation/，至少保存：
- RECONCILIATION.md：既有fea计划、较新732计划、真实已执行A和保留B的一一对照，唯一候选V008；不能复制旧plan当已执行结果。
- baseline_hashes.json、protected_hash_comparison.json：source、V001–V007、take01–13、原Jovi反馈/审批及插件、版本tag、32PNG与正式30镜的前后sha。
- new_profile.json/profile_delta.json/ROI_overlay.png：V008 schema6、三ROI叠层/空间权重可视化、source hash、变化白名单、为何这是综合候选不做单变量归因。
- graph_audit.json、cpu_torch_tests.txt、no_torch_tests.txt、full_tests.txt、ci.json、deployment_verify.json、resource_state.json、dry_run.json、final_diff_review.md、VERSION/CHANGELOG与tag哈希。
- GPU remains NOT_RUN：新candidate不得出现新prompt_id、MP4/ffprobe/人工PASS字段；不得复制take10视频hash冒充V008效果。日志清楚写“只有工程准备，未作视觉验证”。
- 当且仅当未来Jovi明确批准单次GPU后，新增独立不可变take14/run_record/ffprobe/full_decode/49帧/帧1-25-49/动态与局部清晰度对照、人审模板（默认PENDING）与用户真实反馈的严格preview/双hash pin流程。背景树木局部指标、面部真实移动相对肩部、面部叠影、原服装PASS和手部关系都要检；自动锐度/光流不自动PASS。
- 只有同一具体take实际Jovi视觉接受并有输出SHA绑定的QA，才可改变下一shot前驱门禁；当前take09明确CHANGES_REQUIRED，take10仅本地视觉观察不佳/Jovi尚未签收，take13 GPU未运行，SH901/902仍BLOCKED。

## 8. 工程接受、拒收和最终回传合同

若达成：v4新schema与真实Torch和无Torch负例、v2/v3/V5兼容、原R1–R4、双边graph、冻结hash、源保护、准备和dry-run拒绝、资源/部署失败关闭、同实现SHA Actions全部SUCCESS以及本地独立diff复审，可回传ENGINEERING_READY_GPU_NOT_RUN。资源不满足，则RESOURCE_BLOCKED并冻结不可执行job，绝不当作GPU完成。V008未经实际视频和Jovi逐项审片，绝不说视觉已通过。

必须CHANGES_REQUIRED的具体情况：
1. 改写V006/schema4、V007/schema5/v3或旧prepare包take10–13的任何源/证据hash、标签/批准；删掉或未保留暂存内容。
2. 以wan22_timestep_aware_future_roi_v3代表strength，或把12格时间衰减和perROI strength同时塞进同一V008而不区分数学语义；V008没有独立class/策略/schema。
3. 新class仍沿用旧“必须存在完全冻结像素”导致所有合法fractional strength失败，或为了过它改变旧v2/v3断言/结果。
4. Wan基础noise_mask被局部篡改、源首格改变、source latent在future ROI乘alpha两次、非ROI冻结、ROI重叠歧义或采样MODEL/LATENT断边。
5. 假Torch代替真实数值、无Torch prepare错误、profile/schema字段宽松、错误node/object_info/资源漂移仍允许POST、历史状态不明自动重投。
6. 以349/107未提交的旧本地测试、旧GitHub CI或旧v0.1.1标签作为新HEAD验收，或只有文档SHA没有最终实现SHA。
7. 本阶段执行任何新GPU、部署覆盖旧插件、自动换take15、运行SH901/902、伪造Jovi反馈，或把take10观察写作Jovi决策。
8. 模糊原因被未经受控实验写成已确定因果，客观指标或浏览器ended冒充视频质量/人物身份人工PASS。
9. 实现版本没有中文commit/VERSION.json/CHANGELOG.md或强推/移动旧标签。

本地完整回传格式：
~~~text
[C2C] STATE: EXECUTED TASK_ID:c2c_fid2
PLAN_SHA:<本单文档40位提交>
START_REMOTE_HEAD:73248825bc8d17c0c2969518383d654a9847d9b8
ACCEPTED_BASE:1bd1c6e1cc5b47d4fccf18766f42fdb61c0221ad
FINAL_IMPLEMENTATION_SHA:<真实40位SHA，不得用PLAN_SHA替代>
VERSION_TAG:<解析到对应实现SHA的不可变标签>
CONFLICT:<两份旧计划保留，V006/v2，V007/v3，V008/v4且无混义>
PRESERVED:<V001–V007/take01–13与用户反馈/审批/原媒体的hash对照>
NEW_CANDIDATE:<V008/schema6/v4, 新take14若prepared则submitted=false>
TESTS:<完整通过/跳过/CPU真Tensor/noTorch/失败路径与日志>
CI:<同实现HEAD四项run/job/checkout_sha/conclusion>
NODE_DEPLOY:<现有旧plugin SHA、新代码SHA与未部署/未来部署阻塞事实>
RESOURCE:<本机RAM/GPU/pagefile/磁盘与硬门禁>
GPU:NOT_RUN
HUMAN:take09=CHANGES_REQUIRED;take10=Jovi PENDING;V008=NOT_RUN
DOWNSTREAM:SH901/902 BLOCKED;正式30镜未批准
REVIEW:<完整差异独立复审结论/待审核证据路径>
~~~

## 9. 本网页执行边界

本轮已真实核对GitHub/C2C当前branch和完整E盘已暂存代码、两份冲突计划、V006/take10执行与资源指标、V007/schema5/v3独立节点、take11/12漂移拒绝和take13离线dry-run、349/107测试日志及插件未部署证据。此文档是**唯一新增的网页写入文件**；网页没有运行Shell/模型/GPU，没有改任何已暂存业务代码或版本tag，没有批准任何视频或给SH901/902开门。旧两份计划完整保留，新的单一候选v4不能借旧名字执行。
