# FID1：SH903 take09真实拒绝后的微动作与画面细节修复整阶段合同

STATE: PLAN_TO_LOCAL_IMPLEMENT
TASK: c2c_fid2 / 2026-10-15
ENGINEERING_ACCEPTED_BASE: 1bd1c6e1cc5b47d4fccf18766f42fdb61c0221ad (fid1-v0.1.1)
REVIEW_EVIDENCE_HEAD: 778cfec2dbcd13d51b8d0c7c832e46347d008675
BRANCH: codex/fid1-remote-repair
PR: https://github.com/Jovifei/AI-short-vidio-claw/pull/12
DELIVERY: 本文仅是远端独立诊断、确定路线及可执行完整计划；实现、测试、GPU、CI由同一E盘本地Codex工位连续完成。本文提交不修改任何业务代码、现有profile、workflow、PR元数据或人工批准。
FINAL_GATE: SH903 take09 = CHANGES_REQUIRED；SH901/SH902 = BLOCKED；正式30镜不获新增批准。

## 0. 审核事实、权限与不能夸大的部分

1. 本轮真实调用本项目C2C：workspaceId 04f9cfdf549f，workspaceName AI-short-vidio-claw，rootAlias workspace:/；本地Git分支 codex/fid1-remote-repair。C2C别名并非对E盘绝对路径的证明；本地执行前核对 git rev-parse --show-toplevel 为 E:\project\AI-short-vidio-claw。
2. GitHub PR12实际为open/unmerged，工程接受版本是不可变标签 fid1-v0.1.1 → 1bd1c6e1cc5b47d4fccf18766f42fdb61c0221ad。审核过程中新增778cfec2dbcd13d51b8d0c7c832e46347d008675，已通过 compare 确认仅增加真实拒绝证据/CHANGELOG，不改节点、测试、profile或workflow；故选它为本计划的新文档基线，保留1bd为实现基线。
3. 已读真实 local/reports/TAKE09_REJECTION_20261015.md、local/review_evidence/FID1_SH903_TAKE09_FEEDBACK.json、实际take09 QA、run_record、config/source_fidelity_trials/SH903_FID1_V005.json及GitHub已提交审核包。
4. 真实反馈原文：“人物的头并没有任何的移动，然后背景的话也虚幻糊掉了，所以说需要去修改。你自己也能检查出来这些画面的区别。”反馈原始SHA256为 e09b6471ee2b9a9fcbf78248466355a81407f0e057f93b975e00ef821a30b473；output SHA256为 dbdd44e4bdd39b13c8881c3f413a7889f0823c052b99df41698b1d5f61be2db8。
5. QA真实字段：full_playback=CHANGES_REQUIRED、identity=CHANGES_REQUIRED、limbs=CHANGES_REQUIRED、costume=PASS、decision=CHANGES_REQUIRED、next_shot_gate=BLOCKED_CHANGES_REQUIRED。源图的早期T1_SOURCE_ONLY批准不因此撤销，但该视频未获视觉接受。真实拒绝已preview及双hash pin apply；不再次apply、不重写既有反馈与历史QA。
6. 真实take09：Wan2.2-TI2V-5B，576×1024，49帧/24fps，seed=2026100803，SH903_FID1_V005，20steps/CFG5/uni_pc/simple/denoise1；媒体ffprobe/full-decode PASS；Comfy提示ID 1edc8f9a-e40b-445e-b67e-a969a83d53d6，时长719.809秒，采样显存峰11808 MiB；原运行记录采样的最低可用RAM约10.8 MiB，已经说明资源余量非常紧。
7. 本轮已实际查看仓库已提交的take09第1/25/49帧正确标注拼图，以及无FID1的take03 control第1/25/49帧静态图。take09人物朝向和面部中心变化很少；远山/树木有明显柔化。take03也有相当的远景柔化，并有小幅头/口/冠翎变化。静态图无法代替完整视频播放，不据此宣称量化头部角度、准确身份或最终视频通过。
8. 新增审核包 docs/reviews/20261015-take09-jovi-changes-required/metrics.json 以同尺度区域记录：背景树木Laplacian方差SOURCE resized约218.58、帧1约145.55、帧25约114.20、帧49约106.08；悟空脸约2481.02→1693.11、黛玉脸约841.93→332.96（帧1到帧49）。该指标受构图、照明、运动与压缩影响，证明有频域细节衰减迹象，不证明其全部由ROI或某一种代码造成，更不代表用户接受。
9. 当前源文件 941×1672，实际视频576×1024且先经Wan VAE编码：不能拿未经同尺度缩放的原图边缘分数直接要求576视频达到941原图锐度。
10. 当前本机ComfyUI 8188无监听；近期诊断约10GiB VRAM可用/6.7GiB系统RAM可用会漂移。没有GPU已启动或资源满足的远端证据。此次远端不运行GPU、不改人类反馈、不开放SH901/902。

## 1. 因果审核：两种症状需要区分

### A. 头部几乎不动：高信心的双重约束冲突

- V005 positive原文要求“almost motionless”、“hold the starting pose throughout”、“Motion limited to faint water ripples and tiny fabric breathing”；negative原文直接含“head rotation”、“pose changes”、“hand movement”。它们与Jovi要求自然头部微动冲突，必须修正，但单改提示词并非足够的数值修复。
- 已读既有scripts/fid1_wan_latent_anchor_node.py：_anchor_future_rois在未来12个latent时间格对face ROI写入首格源latent；schema4分支保留原Wan noise_mask，使用clone MODEL上的denoise_mask_function返回base_mask*(1-alpha)，scale_latent_inpaint使用当前ModelSamplingSD3的noise_scaling(sigma,noise,latent_image)。
- 已读仓库内installed_comfy_source/comfy/samplers.py的KSamplerX0Inpaint：模型输出按denoise_mask与原latent按1-denoise_mask混合。ROI中心alpha=1时未来对应位置denoise_mask=0，实际上跨全部采样步持续保留源值；文字即使允许转头，也不能让这个中心产生完整的生成运动。
- 49视频帧=13 latent时间格。原Wan条件mask首格0/未来格1；绝不能再次走曾让take05/take07崩成马赛克的“直接篡改LATENT.noise_mask局部格”路线。
- 因此需要同时消除语义禁止和未来面部ROI全强度固定，且保持源图身份、头饰及已经PASS的服装。

### B. 背景与人脸细节衰减：已观测，但因果归属未确定

- ROI原先只覆盖两处脸部，背景未被当前FID1 ROI直接固定。山树纹理在take03无锚对照中亦柔化，说明背景发糊可能包含Wan5B原生时序重建、VAE空间缩放和运动/压缩等共同因素，不能声称放松face ROI一定治好背景。
- 先用现成静态视频、批准源图与同尺度crop复算背景/脸部区域的方差、差异和结构变化，并追踪原始帧数/PTS；不能用单帧画面直觉替换人类完整播放。
- 对于固定远山/树木，可考虑在同一源图的一个小范围静态区域做部分时序保真，而不是冻结整个背景。水面/流水、头发与衣摆必须继续生成，不添加静态全画面锁。
- CPU指标是诊断，不是视觉PASS；即使sharpness分数增加，出现静态矩形拼块、身份漂移或抽搐仍应CHANGES_REQUIRED。

## 2. 本阶段选定的最小实现路线（唯一主路线）

选择“**在现有schema4 timestep-aware节点内增加逐ROI有界 preserve_strength、配套修正运动提示词**”。用一个新schema5/V006 profile描述一个预注册的综合修复候选；不新建节点平台、不替换KSampler、不改变Wan采样时间表、不升级14B、不训练LoRA、不做换脸或视频后处理。保留v0.1.1节点的现有两条MODEL/LATENT活边和所有默认行为。

为何不是prompt-only：旧alpha=1的脸部中心经过KSampler混合仍被完全保留，提示词没有数值权限使其移动。
为何不是换回旧ROI mask：take05、take07已经证实会使Wan局部mask改变整个时格条件并导致场景崩坏。
为何不是全背景锁定：会制造静帧/接缝，违反非ROI生成约束。
为何不直接改变分辨率/采样器/seed：会引入额外变量和资源成本，且当前4070S峰值显存已接近容量。

具体单次修复候选：
- 面部两处ROI保持V005原有坐标与feather_latent=4，但各自新增preserve_strength=0.55：中心原alpha1有效alpha变0.55，未来中心KSampler去噪许可为0.45，容许少量运动且保留部分身份锚。
- 只新增一个局部静态背景ROI，采用已测量的BACKGROUND_TREES：[0.39,0.18,0.64,0.30]、feather_latent=4、preserve_strength=0.65。它以部分源保真抵抗树木细节逐帧消退，非全场冻结；必须用原批准PNG的ROI叠层再次确认未压住动态瀑布/水面。如果该区实际有明显运动，则不强行选择背景ROI，另以版本化profile明确调整并重新预检，而不是悄悄修改已经冻结的job。
- positive/negative作为一个一致的运动意图合同共同修改：取消“几乎不动/禁止所有头部转动”，只允许小幅自然头部倾斜、眨眼与呼吸；防止突然大幅转正、换脸、手分离、换装、明显镜头运动。背景描述保持清晰的山脊、亭台、树枝/花卉，允许水面小幅连贯波纹。
- 固定其它全部变量：已批准PNG/hash、人物、seed2026100803、576×1024、49/24、Wan2.2-TI2V-5B、20steps/CFG5/uni_pc/simple/denoise1、ModelSamplingSD3 shift8/flow/multiplier1000。
- 候选增益0.55/0.65是有界工程试验值，不是假称实测最优。此次同时改变提示词和alpha策略且增加静态背景ROI，**属于预注册综合质量修复，不能把任何改善归因到某个单独变量**。为节约4070S资源只允许一个新的真实SH903 take10；失败后提交证据并停止，不自动另跑take11或随机扫参数。

重要tradeoff：面部增益变小可能导致身份细节漂移；背景增益偏大可能导致局部静态接缝。需同时比较身份一致性、自然头部运动、服装原有PASS、背景清晰与动态连续性，任何一项明显劣化不能用其他项弥补。

## 3. 数值与工作流合同（不得靠字符串或调用方布尔值作证据）

### 3.1 保持既有Wan输入事实

- 原生 Wan22ImageToVideoLatent 的真实输出 samples 为 [1,48,13,64,36]、noise_mask为[1,1,13,64,36]（宽576高1024）；t=0源图编码，未来t=1..12为待生成。严格验证batch/channel/time/H/W、finite、dtype/device。
- 原始 LATENT 字典全部元数据保持，首latent完全不变；原始noise_mask首格0、未来1，一律保持不变传给Wan条件编码。
- 生成独立spatial ROI alpha，未来t>0才非零。引入preserve_strength后 effective_alpha = spatial_feather_alpha × preserve_strength。必须是有限实数，禁止bool、NaN/Inf、负数、>=1的schema5数值；本阶段冻结0.55/0.65，允许的schema5边界建议0.25..0.80，兼容旧schema4默认强度1.0。
- 当前timestep-aware的 prepared["samples"] 在alpha>0位置仍写入完整源首格，绝不把未初始化future零latent当条件；实际KSampler hook使用effective_alpha决定保留权重，不要在写samples时再乘一遍alpha造成alpha²。
- KSampler denoise_mask_function必须保持 base_mask × (1 - effective_alpha)；t=0始终0，future非ROI始终1，face核心约0.45、背景有效alpha最大<1；不能全0、全1失去意图，也不能冻住整帧。
- scale_latent_inpaint继续通过实际ModelSamplingSD3 flow当前sigma产生noised_source，不直接把z0硬塞进zt。禁止改变sample scheduler、噪声seed、VAE、采样频率。
- Comfy的48通道repeat mask必须接受且逐channel相同；其它channel、形状/时格漂移、非有限mask、device/dtype不匹配拒绝。

### 3.2 图链是强门禁

API graph必须存在并真的使用：
- LoadImage -> Wan22ImageToVideoLatent.start_image；
- ModelSamplingSD3 -> FID1WanTimestepAwareROIAnchor.model -> KSampler.model（FID1输出0）；
- Wan22ImageToVideoLatent -> FID1WanTimestepAwareROIAnchor.latent -> KSampler.latent_image（FID1输出1）；
- KSampler -> VAEDecode -> CreateVideo -> SaveVideo。
- 精确冻结roi_boxes_json（含preserve_strength）与profile字节SHA、提示词两路CLIPTextEncode、source SHA、seed、模型文件/采样预算、依赖实现hash与graph hash。禁止绕过节点、节点悬空、插入未知节点、让调用者传入“已接线=true”骗过校验。
- Comfy object_info验证实际载入的节点socket以及输出类型，节点新增的强度只作为roi_boxes_json合同字段，不增加第三个socket；历史schema4 JSON仍可加载。运行时还核验已部署节点的真实SHA与准备包一致。

### 3.3 数据合同版本和向后兼容

新增 config/source_fidelity_trials/SH903_FID1_V006.json，建议 schema_version=5、profile_id=SH903_FID1_V006、scope=T1_SOURCE_ONLY、shot_id=SH903、anchor_strategy=wan22_timestep_aware_future_roi_v3；外层字段仍遵循当前冻结字段集合，ROI对象比schema4严格多一项 preserve_strength。只允许本次SH903的schema5；SH901/SH902不自动接受新策略/新增益。

新schema5每个ROI严格键：id,x0,y0,x1,y1,feather_latent,preserve_strength；老schema4 ROI仍严格不允许此附加键。严禁“宽松接受所有未知键”。字节SHA与序列化ROI一致性在prepare/submit实时校验。

FID1 job contract沿用现有schema2结构、job_integrity沿用schema1，T1_SOURCE_ONLY、eligible_for_final_cut=false。新增策略映射到**同一个**FID1WanTimestepAwareROIAnchor Comfy节点类。新策略代码和依赖变更使旧未运行prepared job失效；历史已完成take01–take09及其QA仍只按原冻结job/run/output验证，不要求历史代码SHA=新实现。
版本策略：本阶段是兼容功能增加，建议发布FID1 v0.2.0、不可变tag fid1-v0.2.0；若本地实施实际破坏旧schema4，则不能自称兼容，必须先修好或按主版本合同处理。所有commit中文，更新VERSION.json、CHANGELOG.md且不移动fid1-v0.1.0/v0.1.1标签。

## 4. 文件级实施路线：同一完整工程阶段连续做完

| 实际文件/新增文件 | 实现内容和验收 |
|---|---|
| scripts/fid1_wan_latent_anchor_node.py | _validate_rois兼容schema4老ROI和schema5增益ROI；旧策略不变，新v3下逐ROI计算有效alpha；将旧“必须有alpha=1全固定像素”断言限定到要求强固定的旧路径，v3接受有界fractional但仍拒绝零锚/全帧冻结/非法输入；原LATENT/flow/hook不变 |
| scripts/source_pilot.py | load_trial_profile仅对SH903 schema5严格验证新策略/键/强度/ROI总面积与输入SHA；准备时冻结profile、source、依赖；仍默认离线、不调用Torch，不解锁SH901/902 |
| scripts/preproduction.py | FID1_NODE_CLASS_BY_STRATEGY新增v3→现有timestep-aware节点；validate_graph按schema5要求model、latent、roi_boxes_json真实连线与值；采样、文本、模型冻结 |
| scripts/fid1_graph_audit.py | v3走原v2双MODEL/LATENT边，不可走legacy LATENT-only；审计报告记录候选与基图SHA、三块ROI含strength、模型与潜变量边 |
| scripts/submit_prepared.py | job和profile/schema/策略/node/object_info的真实校验；执行锁前、锁内、runtime后复验全部hash；未知历史不POST，dry-run不POST |
| config/source_fidelity_trials/SH903_FID1_V006.json | 单次预注册候选：沿用V005源、seed、fps、sampler、面部几何与feather；新增局部背景ROI、有界强度；用一致的微动作/清晰背景prompt，hypothesis明确承认综合干预 |
| scripts/fid1_motion_detail_qa.py（如新增） | CPU/Pillow/ffmpeg离线读取历史和新take；比较同尺度源图、take03/take09/take10的1/25/49及all49，输出ROI可视化/清晰度和运动诊断及文件hash；不自动授予视觉PASS |
| tests/test_fid1_timestep_aware_node_unittest.py | 真实Torch CPU验证gain0.55/0.65、noised_source流、alpha一次、源首格不变、ROI外仍可生成、旧schema4结果完全不变 |
| tests/test_fid1_profile_schema_unittest.py、test_fid1_graph_audit_unittest.py、test_source_fidelity_profile.py、test_fid1_submit_runtime_unittest.py | V006 schema5严格合同、实际图链、漂移失败、无Torch入口、Comfy节点输出、提交负路径；保留全部既有断言 |
| tests/test_fid1_deploy_unittest.py、test_fid1_qa_report_unittest.py | 安装冲突/幂等/回滚、历史QA只读兼容、新take的帧映射/QA/PENDING、旧反馈不覆盖 |
| docs/preproduction/LOCAL_SHOOTING_RUNBOOK.md、scripts/README.md | 记录V006完整参数、actual准备/部署/试拍/QA命令、资源门禁和准确回退，不改正式30镜流程 |
| docs/reviews/20261015-fid1-sh903-motion-detail/ | 实际root-cause依据、profile+源码+source的哈希、CPU矩阵、部署回执、graph报告、同HEAD Actions；如果已实际GPU，则另追加take10真实run/ffprobe/MP4 hash/完整视觉材料，否则明确NOT_RUN |
| VERSION.json、CHANGELOG.md | 中文变更与版本固定，只有本地实现测试/复审完成后发布新不可变tag；本文档计划提交不修改它们 |

注意：不要额外引入所谓ReferenceConditioning、遮脸后处理、随机人脸替换、第三方生成平台、VAE切换或旧take复写。除以上边界内的兼容增益扩展，不重构既有已经通过工程验收的R1–R4反馈事务链。

## 5. V006预注册配置意图（本地用真实素材叠层核验后创建一次）

新profile草案的变更区块示意如下；其它字段必须复制V005原始source SHA、seed、尺寸、帧数、fps并经真实原图绑定，不可省略或用此示意代替完整JSON：

~~~json
{
  "schema_version": 5,
  "profile_id": "SH903_FID1_V006",
  "scope": "T1_SOURCE_ONLY",
  "shot_id": "SH903",
  "anchor_strategy": "wan22_timestep_aware_future_roi_v3",
  "anchor_rois": [
    {"id":"WUKONG_FACE","x0":0.11,"y0":0.20,"x1":0.36,"y1":0.36,"feather_latent":4,"preserve_strength":0.55},
    {"id":"DAIYU_FACE","x0":0.69,"y0":0.20,"x1":0.89,"y1":0.37,"feather_latent":4,"preserve_strength":0.55},
    {"id":"BACKGROUND_TREES","x0":0.39,"y0":0.18,"x1":0.64,"y1":0.30,"feather_latent":4,"preserve_strength":0.65}
  ]
}
~~~

positive_prompt建议表达的具体意图（本地写入完整JSON，严格记录与V005的diff）：

“Keep the two approved subjects' exact identities, species, facial proportions, red-and-gold and lavender costumes, ornaments, joined hands and original composition. During this two-second shot, allow a very small natural head inclination or slight gaze adjustment, a soft blink and subtle breathing; joined hands stay connected, sleeves make tiny coordinated movement. Keep the distant mountain ridges, trees, pavilion and flowers clear and stable; allow coherent small water ripples. Locked camera, no focus pull, no identity redesign.”

negative_prompt保留“no large head turn, no frontal face, no identity/species/armor/dress change, no separated hands, no extra limbs, no jump cut, no camera movement, no defocus/blurred or smeared distant scenery, no rectangular frozen patches”，但**删除**泛化的“head rotation”“pose changes”“hand movement”等与有限微动作直接冲突的禁词。画面是否遵循角度和细节指令仅凭实际试拍与人类审片判断，prompt不是运动度数的硬约束。

背景ROI坐标来源为仓库已提交的同一输出测量patch；开始prepare前必须出一张对原批准源图叠加三处ROI并带source SHA的核对图。若实际有动水/瀑布穿过该框，则保持面部增益方案，调整背景框到静态树木后冻结一个不同的V006最终SHA；**不要**修改已prepare的V006 job。此处不能把几何核对变成原30镜审批。

## 6. 实测诊断与接受口径

CPU诊断固定三个基线：take03无锚参考（output SHA 433c63b311adee879d011aabbeedce2cc08f192e4395e036d0f2deffba796ed1）、take09真实失败（输出SHA dbdd44e4…），以及新候选take10。源图SHA 6476cf1e17105b3589095918a46546baced0db35ef2a6ca235551f4b7002149f。

- 源图与每段视频先缩到相同576×1024坐标、固定色彩/ROI几何。不能使用原始941×1672对576帧直接下清晰度结论。
- 人脸：分别对悟空/黛玉脸做同尺度1/25/49、all49 crop和identity参考对比；记录自然头部朝向/眨眼/嘴型/毛发轮廓、脸部稳定和双人关系。不能把纹理变化或失焦误报为真实头部运动。
- 服装：沿用Jovi对take09已PASS的要求；胸甲、披风、头饰、发钗、裙装与人物对应关系不应劣化。
- 动作/肢体：实际完整播放检查是否至少有可见而克制的头部微动，手保持牵连、不生成多手/坏指/跳动身体；背景水纹与衣摆有自然时序，不能全帧近静止假视频。
- 背景：分别看静态树木、远山亭台、水面三个区域；边缘方差/局部差异/光流仅作为diagnostics，是否清晰由Jovi决定。take09背景树木基线 145.55（帧1）→106.08（帧49），观察新take是否减少衰减并且没有可见贴块/闪烁/画面裂缝。
- 消融限制：本次V006同时改动提示词及部分alpha，单次GPU结果只能判断综合候选是否达标，不能声称某一因子具有单独因果效果。若候选失败，完整报告明确归因仍未定，不自动启动更多GPU实验。
- 硬门槛：codec/dim/fps/frame count/full decode/hash真实PASS；出现马赛克、伪文字、块状脸/背景、NaN或时序断裂都FAIL。工程/媒体通过仍不自动视觉通过。

## 7. 必测回归与负路径（不能只跑新增helper）

1. schema4/V005字节及ROI JSON行为兼容：strength缺省按1.0，旧MODEL/LATENT输出和mask数值与v0.1.1基准相等（Torch真实张量）。
2. schema5合法V006三块ROI和强度：effective_alpha计算符合0.55/0.65；在首格全0、未来ROI>0且<1、非ROI完全1去噪；不会出现全冻结、mask反向或alpha²。
3. 强度负例：负数、0、1、>1、bool、字符串、NaN/Inf、额外/缺失字段均拒绝；schema4带strength以及schema5未带strength均拒绝；重复ID/过大面积、非法范围拒绝。
4. 真实Torch CPU：dtype/device/rank/batch=1/channel48/T13/H64/W36、原noise_mask[1,1,13,64,36]、48通道repeat mask一致性及异样拒绝；不使用Fake替代运算。
5. timestep-aware采样：对实际clone MODEL patch进行scale_latent_inpaint当前sigma测试，首格源值不变、未来选区noised_source有效、输出有限；模型不为WAN22、无ModelSamplingSD3、patch对象共享错误时拒绝。
6. 实际graph结构：FID1同时真正连接KSampler.model output0与latent_image output1；ROI strength、提示词、source、steps/CFG/denoise/shift等任意漂移失败；文字“reference/approved”或调用者bool不能充当接线证据。
7. 旧生产12节点及原V5 guard测试仍通过；不允许新FID1组件混入未授权原30镜；V006只能SH903 source-only，不给SH901/902新能力。
8. noTorch子进程明确阻断torch导入，仍能加载schema5、prepare、hash/graph验证、submit dry-run、review-page；数学测试必须在实际Torch CPU跑，不能skip成PASS。
9. prepare期间profile/节点/源码/批准快照/依赖变化、准备路径冲突、旧take覆盖、旧schema下游任务、错误shot/非法路径必须失败且无发布。
10. submit默认dry-run零POST/零attempt；执行前完整source/profile/dependency/installed node hash和Comfy object_info/queue检查，锁内及runtime后的再校验与未知history防重POST有效。
11. FID1部署的同版本幂等、不同版本拒绝覆盖、用户文件冲突拒绝、精确rollback及插件所有权；不删除其他custom_nodes。
12. take09真实拒绝和证据SHA保持；历史take01–09/job/approval/MP4及原30镜hash不变；真实下游SH901/902仍不得prepare/POST。
13. 新QA工具对同源同尺寸ROI记录真实1/25/49帧、0/1/2s、全部49帧及MP4/帧/源SHA，缺帧/尺寸/解码/异常路径拒绝；不能把模糊区域的自然变化归因于已证的头部旋转。
14. 资源门禁CPU测试：内存或显存不足、Comfy未启动、队列占用、模型/object_info不匹配、未知submission history都返回明确BLOCKED并且无POST。
15. Node端如确实新增了schema5可选功能，已批准的v0.1.1 V005完成历史仍可只读复审；不能借新实现漂移重封/重放旧take。

命令从E盘项目根执行（每条实际记录exit code、解释器、版本、输出路径）：

~~~powershell
python -m unittest discover -s tests -p "test_fid1*unittest.py" -v
python -m unittest discover -s tests -p "test_source_fidelity_profile.py" -v
python -m unittest discover -s tests -p "test_*.py" -v
.\local\comfyui\image\venv\Scripts\python.exe -m unittest discover -s tests -p "test_fid1*unittest.py" -v
python -m compileall -q scripts tests
git diff --check
python scripts/sync_repo_media.py --check
python scripts/launch_readiness.py --project all
~~~

原正式输入不完整的launch_readiness应按实际缺口报告，不能篡改原批准让它假变绿。原CI应真正发现全部新测试并在Media recovery CPU Torch工作流运行；不得删guard或调低测试范围。

## 8. 本地从本计划开始的一次连续执行合同

### A. 只快进接收文档、保护历史

~~~powershell
Set-Location E:\project\AI-short-vidio-claw
$Baseline = '778cfec2dbcd13d51b8d0c7c832e46347d008675'
$PlanSha = '<本轮网页提交的40位计划SHA>'
if ((git branch --show-current).Trim() -ne 'codex/fid1-remote-repair') { throw 'wrong branch' }
git rev-parse --show-toplevel
git status --short
git fetch origin codex/fid1-remote-repair
if ($LASTEXITCODE -ne 0) { throw 'fetch failed' }
git cat-file -e "$PlanSha^{commit}"
if ($LASTEXITCODE -ne 0) { throw 'plan SHA unavailable' }
git diff --name-status "$Baseline..$PlanSha"
# 必须只含本文档；出现业务改动则停止检查并发写入者。
git merge --ff-only $PlanSha
if ($LASTEXITCODE -ne 0) { throw 'cannot fast-forward, preserve local state' }
git rev-parse HEAD
~~~

绝不reset/clean/force-push/改main，保留两个Owner tasks未跟踪笔记和Obsidian。先对源PNG、v001–v005 profile、take01–09的job/workflow/run/QA/MP4/证据、已接受标签和正式两集批准建立保护hash。take09 QA已记录真实CHANGES_REQUIRED，不能重写回PENDING；保护其完整当前字节。

### B. 同一工程任务连续完成实现、测试和自审

读取AGENTS.md、START_HERE_LOCAL.md、V005与本计划，按第4节改现有实现、新建V006、增加测试；先用Torch CPU验证本机制，离线prepare只生成take10。对每一个失败日志修复再运行全量；自审完整diff，避免盲目改动既有MODEL采样算法。审核无误后本地提交中文Commit、更新VERSION.json+CHANGELOG.md，产生候选实现SHA并推送PR12；四项CI针对最新HEAD完成且全绿，独立Web复审再按门槛给最终工程结论。若需要自审修复，修复后再次测试，最后只有一个真正的固定实现HEAD和对应新标签。

### C. 精确部署与回退

已有FID1插件由 scripts/fid1_deploy.py 管理：不同node源码SHA的直接deploy应拒绝覆盖。记录当前已部署插件、FID1_DEPLOYMENT.json、local/reports/fid1_deployment.json及其hash；验证无运行任务后，使用现有命令进行受控rollback和新deploy，不手工覆盖未知文件或更换Comfy核心源码。部署后按v0.2.0新源码hash验证，并重启**本机现有**ComfyUI服务，检查/queue与/object_info/FID1WanTimestepAwareROIAnchor（原有MODEL/LATENT/roi_boxes_json插口不变）。服务仍只允许127.0.0.1/localhost。

~~~powershell
$ComfyRoot = 'local/comfyui/image/ComfyUI'
python scripts/fid1_deploy.py rollback --root . --comfy-root $ComfyRoot
if ($LASTEXITCODE -ne 0) { throw 'owned plugin rollback refused; do not manually remove files' }
python scripts/fid1_deploy.py deploy --root . --comfy-root $ComfyRoot
if ($LASTEXITCODE -ne 0) { throw 'deploy failed' }
python scripts/fid1_deploy.py verify --root . --comfy-root $ComfyRoot
if ($LASTEXITCODE -ne 0) { throw 'verify failed' }
~~~

这些命令是本地实现完成并核验工具所有权后的条件步骤，不是远端已执行事项。若新插件需回退，先用owner-aware rollback删除本版本精确文件，保留插件撤销证据；如确需恢复v0.1.1旧节点，从固定旧SHA受控版本独立校验再部署，不能通过reset/clean、直接覆盖node、移动标签或删除旧jobs回退。原已生成媒体保留不变。

### D. 单次SH903 take10的资源门禁与运行

先确认当前服务已启动并处于现有Wan5B环境。重读nvidia-smi与Comfy/system_stats、模型SHA、CPU/RAM/pagefile、磁盘空间、驱动、队列、node SHA；take09曾峰值11808/总约12282MiB，GPU余量仅数百MiB，RAM曾仅余约10.8MiB。**不能以“之前能跑”当本次安全证明**。建议优先使可用物理RAM至少约8GiB，GPU/系统内存达到经本机采样历史增长量加安全余量的实测预估；达不到或服务异常则报告RESOURCE_BLOCKED，不硬触发POST、不自动换模型、扩容分辨率或再次提交。采样峰不等于瞬时硬件最大值。

在现有take01–09均不覆盖的前提下，已核对take10暂不存在，开始时必须重新确认：
~~~powershell
$J10 = 'local/production/T1_SOURCE_PILOT/video/SH903/jobs/take10'
if (Test-Path $J10) { throw 'take10 exists: do not overwrite or re-use' }
python scripts/source_pilot.py prepare --root . --shot SH903 --seed 2026100803 --out $J10 --trial-profile config/source_fidelity_trials/SH903_FID1_V006.json
if ($LASTEXITCODE -ne 0) { throw 'prepare failed' }
python scripts/submit_prepared.py --root . --job-dir $J10 --url http://127.0.0.1:8188
if ($LASTEXITCODE -ne 0) { throw 'dry-run refused' }
# 只有资源、CI、现场Comfy节点SHA、queue和用户授权均满足后，单次执行：
python scripts/submit_prepared.py --root . --job-dir $J10 --url http://127.0.0.1:8188 --comfy-root local/comfyui/image/ComfyUI --execute
~~~

严格GPU并发1。创建submission_intent后若超时/未知状态，先查prompt/history并保留回执，不能重POST或换新目录重投。失败后本阶段立刻停止额外GPU试验并提交日志；成功后只进入QA，不自动发布视频或解锁下游。

### E. 新take10真实QA与用户决策

~~~powershell
python scripts/fid1_qa_report.py create --root . --job-dir $J10
# 如增加独立 motion_detail_qa，仅在真实MP4存在后对source/take03/take09/take10作离线对比，不提交新GPU。
python scripts/fid1_qa_report.py review-page --root . --job-dir $J10 --out local/production/T1_SOURCE_PILOT/review_sessions/SH903_take10_motion_detail_01
~~~

审核包必须含：job/profile/source/workflow/model/node/dependency SHA、graph活边签名、original Comfy history/prompt_id、一次POST记录、真实MP4哈希/字节、ffprobe原始信息、full-decode退出码和stderr、1/25/49+all49、原批准源图同尺度、take03/take09并列对照、定量诊断、GPU/系统RAM/pagefile采样、真实QA和完整视频审片页。历史take09真实拒绝必须保留，不改写它的QA和全部旧take。

take10默认visual_review=PENDING；只有Jovi真实完整播放并导出身份/服装/四肢/完整播放逐项判断与原话后，才可通过原严格preview及两hash pin apply。若CHANGES_REQUIRED，完整工程和媒体结果分别报告，SH901/902继续BLOCKED；若Jovi明确接受该具体take的输出SHA，才在另有范围授权、前驱receipt和资源门禁成立时讨论SH901串行试拍。不得由Codex自评、视频播放ended或自动指标生成Jovi的PASS。

## 9. 验收标准、CI、版本与固定SHA

工程层（不需要人类视频接受）：
- schema5/v3的增益实现严格、有界、实际数值有效，原Wan mask和采样flow不被破坏；真实Torch测试覆盖gain非1、非ROI可生成、历史v2行为恒等、所有无效参数拒绝。
- 新profile/hash/双MODEL+LATENT live graph/prepare/submit/部署object_info闭环，noTorch离线入口和负路径通过；原R1–R4/正式V5 guard/旧profile与历史完成QA回归不降低。
- 完整本地unittest、Comfy真实CPU、必要CLI集成、独立最终diff复审及同HEAD四项GitHub Actions完成且success；必须读失败日志修复后重跑。不能引用v0.1.1旧CI假装新版本通过。
- 原32PNG、正式30镜/registry、take01–09/profile V001–V005、历史真实CHANGES_REQUIRED反馈/当前QA、两个既有标签和Owner笔记保护hash无未批准变化。除新take10及其独立输出/QA外不写历史生产目录。
- 新增兼容功能按版本规则建议FID1 v0.2.0、中文Commit、VERSION.json/CHANGELOG.md与不可变fid1-v0.2.0标签；实际final SHA为40位，不能将本文档SHA、PR merge SHA或阶段中间提交当实现交付。
- 若资源外部阻塞，允许ENGINEERING_READY_RESOURCE_BLOCKED，但必须说明实际工具/资源值且绝不谎报GPU。

媒体与视觉层：
- 若GPU真正运行，实际单次take10符合576×1024/49/24/Wan5B等合同、mp4 hash和ffprobe/full decode通过；整场无马赛克/接缝/静态拼块。
- Jovi必须看到自然克制的头部微动、身份未换、服装持续保留PASS、牵手关系/肢体自然、背景细节与动态不发生不可接受恶化；自动清晰度/差异指标仅供比较，不自动升格用户接受。
- SH901/902无论工程结果如何默认BLOCKED，除非未来同一具体前驱take得到Jovi可核hash的明确视觉接受；不触及正式LOOKREEL/EP001与20张精确剧情图/HOME/RAIN/受伤状态原缺口。

本地完整交接格式：
~~~text
[C2C] STATE: EXECUTED TASK:c2c_fid2
PLAN_SHA: <本轮文档提交40位SHA>
ENGINEERING_BASE: 1bd1c6e1cc5b47d4fccf18766f42fdb61c0221ad
FEEDBACK_EVIDENCE_HEAD: 778cfec2dbcd13d51b8d0c7c832e46347d008675
IMPLEMENTATION_HEAD: <最终40位SHA>
VERSION_TAG: <实际不可变标签>
PR: 12 open/unmerged
CHANGED_FILES: <实际diff>
TESTS: <完整/CPU Torch/noTorch/CLI/负路径、命令和真实通过/跳过/失败>
CI: <同实现HEAD的4 run+job+checkout_sha+日志结果>
GRAPH: <真实双边/ROI及gain/source/prompt/model/node和依赖hash>
DEPLOY: <安装与回退清单/实际节点SHA>
PROTECTED_HASHES: <旧source/profile/take/approval/Obsidian保护记录>
GPU: NOT_RUN / RESOURCE_BLOCKED / 单次真实take10的prompt_id/history/资源结果
QA: <媒体hash/ffprobe/full decode/1-25-49/all49/诊断>
HUMAN: take09=CHANGES_REQUIRED; take10=PENDING或Jovi真实签收结果
DOWNSTREAM: SH901/SH902 BLOCKED，正式30镜未批准
REMAINING_GATES: <确切剩余条件>
~~~

必须判CHANGES_REQUIRED的情况：仅改prompt却仍全强锁脸；错误地修改Wan原条件mask；alpha被重复乘导致平方衰减；full-frame freeze/没有真实生成区域；非法ROI gain绕过；新策略graph未进入KSampler；使用Fake测试替代真实Torch；改变旧take/用户反馈/正式审批；自动POST未知历史；GPU失败假称成功；把“背景方差升高/截图似乎正常”冒充Jovi视觉PASS；CI指向旧HEAD；版本标签移动或未维护中文版版本记录。

## 10. 本轮远端交付边界

本轮网页已做的工作：读取真实反馈、QA、V005和take03/05/07/09对照及已安装Comfy源码副本；核对工作区和PR12；审查Wan采样和timestep-aware hook，读取第1/25/49静态图与诊断指标；制定唯一主要修复路线、具体文件/数学/负例/QA/部署/回滚/单次GPU/资源/版本/固定SHA执行合同；将本文**文档**提交到PR12指定分支。

本轮网页没有做的工作：没有改业务代码/profile/workflow/版本文件，没有运行本机Shell/Torch/GPU，没有完整播放MP4，没有虚构用户重新批准，没有尝试开放SH901/902或合并PR。计划SHA与后续本地实现SHA必须分别核验。
