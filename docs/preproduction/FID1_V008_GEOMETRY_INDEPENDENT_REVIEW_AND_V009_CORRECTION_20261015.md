# FID1 v0.2.0 独立工程复审、V008几何拒收与V009唯一纠正合同

STATE: CHANGES_REQUIRED_CANDIDATE / ACCEPTED_ENGINEERING
TASK: c2c_fid2
AUDITED_IMPLEMENTATION_SHA: 111cb3fb07ab560cc88d346dcff02316f26e16c2
AUDITED_TAG: fid1-v0.2.0
PR: https://github.com/Jovifei/AI-short-vidio-claw/pull/12
PLAN_BASE: b37edc51236cf0b340401c0141a2e7687f5b394b
SCOPE: T1_SOURCE_ONLY
WEB_ACTION: DOCS_ONLY; NO_CODE / NO_DEPLOY / NO_GPU / NO_MERGE

> 最重要的区分：v0.2.0 的 schema6 / v4 **代码工程**通过本次独立审查，但 V008 **实际图像几何**不满足背景区保真意图。不能把 359/117 测试通过当作 V008可以试拍；不能把视觉反馈、图片存在或成功CPU推导成Jovi接受。本文件是唯一新的纠正合同，不修改已发行标签、V008、任何历史take或已批准人物/源图。

## 0. 复审实际范围与可证实证据

- GitHub PR12 open/unmerged，分支codex/fid1-remote-repair，HEAD=111cb3fb07ab560cc88d346dcff02316f26e16c2。相对b37edc51236cf0b340401c0141a2e7687f5b394b为一个实施提交，包含旧暂存的V006/V007阶段、新独立V008、新测试及审核证据；本次不修改任何这些文件。
- 不可变注释标签fid1-v0.2.0已由GitHub Git ref->tag object实际解引用到上述40位SHA；原fid1-v0.1.1仍指向1bd1c6e1cc5b47d4fccf18766f42fdb61c0221ad。新补修不可复用/移动fid1-v0.2.0。
- C2C本地工作区04f9cfdf549f/AI-short-vidio-claw与GitHub HEAD相同，branch匹配，无staged/unstaged修改；原tasks/lessons.md与tasks/todo.md仍未跟踪，不删除。
- 实际读取本地docs/reviews/20261015-fid1-v008-reconciliation下RECONCILIATION.md、ROI_geometry.json、candidate_preparation.json、new_profile.json、profile_delta.json、resource_state.json、protected_hash_comparison.json、full_tests、cpu_torch_tests、no_torch_tests、deployment_verify.json及local/reports/fid2_v008_fixed_head_ci.json；查阅真正的源码和测试，而不以summary替代代码。
- 同一HEAD的四项Actions通过：Launch input contracts run38615409512、Preproduction V5 run38615409307、Committed media/source pilot run38615409352、Media recovery run38615409232。读取Media recovery真实job 116029107343日志，PR测试merge checkout=c0da46042733ef87bfb29ad2902b77da9bd6d8c6，包含111cb3...，全量359项通过零skip、可核实新strength和noTorch负例。Preproduction job116029107566实际CPU Torch套件117项通过。它们是PR合成merge ref，不表示main已合并。
- 本地全量359 collected、356通过/3个旧Windows符号链接权限skip；Comfy venv 117通过；阻断torch导入的prepare+submit dry-run测试成功。646项保护哈希对比由本地扫描记录为646/646不变；网页还核对了清单中旧V005–V007及take09/take10/take13证据的覆盖范围，但未重新计算全部646项E盘字节哈希。
- 本轮实际通过GitHub读取了本阶段BACKGROUND_TREES.png的真实源图/时间帧裁片（不是文字猜测）：左侧批准来源局部及后面的第1/25/49帧里，可见橙红色长冠翎从所谓背景树木区域上方横穿。C2C ROI_overlay.png由工作区标记存在；完整2.5MB overlay未通过当前接口按原始像素加载，故不声称独立检查了其全部像素。视觉局部事实与本地ROI_geometry.json一致。
- C2C检查本机目录仅有take01–take13，take14不存在。schema6/V008未创建真实prepare/job、未部署新节点、未GPU；用户take09=CHANGES_REQUIRED、take10=Jovi PENDING，SH901/SH902=BLOCKED，正式30镜未变。

## 1. 独立工程审核结论：ACCEPTED_ENGINEERING（仅当前可测范围）

### 1.1 代码/数学

- 实际新策略wan22_timestep_aware_roi_strength_v4、schema_version6、独立类FID1WanStrengthROIAnchor，与V007的wan22_timestep_aware_future_roi_v3 / FID1WanTemporalROIAnchor含12格时间权重完全分离。旧v2/v3类仍保留。
- scripts/fid1_wan_latent_anchor_node.py 的新 _validate_strength_rois 要求严格7键、非bool有限strength∈[0.25,0.80]、feather1..4、面积<.5、潜空间不交叠；_anchor_future_rois_strength 在future非零alpha位置只拷贝**完整**首latent，先定义 spatial feather alpha×strength，再仅在克隆MODEL的采样mask hook做 base_mask×(1-alpha_eff)。保留LATENT原noise_mask（首格0/未来1）、samples首格、非ROI与metadata，不会把源值预乘alpha造成alpha平方。
- 采样hook仍验证Wan 1或48通道重复mask、设备/精度、finite、mask时空shape；scale_latent_inpaint使用生效ModelSamplingSD3的noise_scaling(sigma,noise,latent_image)，非在某一采样步将z0直接硬塞进zt。旧v2/v3全强度冻结规则没有为满足fractional alpha而整体删除；新v4以独立构造分支允许所有strength<1。
- 真正Torch CPU完整[1,48,13,64,36]正例检查有效alpha=0.55/0.65、羽化边0.1375、首格、未来数值拷贝、meta和Wan mask、sigma/noised_source、非ROI可采样及mask重复48ch；强度bool/NaN/0/1、ROI交叠/缺键、错误形状/mask/device均有负路径。已阅读tests/test_fid1_strength_node_unittest.py和test_fid1_strength_profile_unittest.py的调用实现，而不只引用通过数量。
- preproduction/source_pilot/fid1_graph_audit严格让v4类的MODEL output0、LATENT output1都实际接入KSampler，禁用temporal_anchor_schedule_json插口；冻结profile bytes、source、ROI JSON、prompt、seed、workflow和实现依赖hash。历史v2/v3/V5路径继续测试且没有本轮明确的回归错误。

### 1.2 运行安全边界

- submit_prepared.py:146–195严格限制本机环回地址，执行前校验已安装插件源码SHA、空队列、/object_info实际类和插口；v4/v3使用最新RAM≥8589934592 bytes、VRAM可用≥8192 MiB以及非负/有限计数门槛，数值未知或不足拒绝。提交仍默认dry-run、保留原GPU锁、未知历史不重复POST。
- 真正已安装插件仍旧SHA c1d4c573a1e6bbd63793398293be16f3b7a6a2a3042d3340f08dc8870cb2e0b3；deploy verify返回exit2「installed FID1 ComfyUI dependency contract changed」，符合拒绝逻辑。没有证据可声称Comfy进程已加载FID1WanStrengthROIAnchor，因此工程通过不等于runtime loaded或渲染成功。
- 目前没有独立证明某种语义背景ROI自动审核已内建在prepare：配置字段/几何重叠可以机器检查，但「这个区域真的只包含静态树木」仍是原始源图像素审查责任。这是下一阶段纠正合同须加强的操作级/证据级门禁，不倒推v4数值实现失败。

## 2. V008候选明确拒收：GEOMETRY_BLOCKED（P1阻断）

预注册BACKGROUND_TREES box=[x0.39,y0.18,x1.64,y1.30]，在来源941×1672像素上约x367..602,y301..502；在latent [W36,H64]映射 x14..24,y11..20。另两个人脸分别 x3..13,y12..24 和 x24..33,y12..24，三矩形不相交，但是「无几何相交≠场景为静态树木」。

**实际SOURCE/FRAME1/25/49裁片清楚显示悟空长冠翎横过背景框**，若以0.65 strength持续保留该区域，会把动态人物头饰误归为静态背景并增加穿帮/接缝的风险，违背Jovi的自然头动目标。可能涉及水雾/远景也需核实。人工语义审查已经拒绝这一具体参数，不能用CPU/CI绿灯、mask数学正确或锐度数值解除阻断。

同时B前RAM实测1,049,313,280 bytes（约0.98GiB），远低于8GiB；VRAM 12282-2392=9890MiB虽高于8192MiB仍不足以替代RAM；新插件未部署。因此 **GEOMETRY_BLOCKED + RESOURCE_BLOCKED + DEPLOYMENT_NOT_READY** 三项独立硬门槛都未满足。不得创建V008真实job/take14，也不得执行任何本阶段GPU。

## 3. 唯一完整纠正路线：新V009配置 + 专门的静态背景几何确认

本阶段纠正的是**具体ROI内容归类错误**，不是再另造第五套ROI数学算法。

- 只允许新增 config/source_fidelity_trials/SH903_FID1_V009.json，profile_id=SH903_FID1_V009，**仍为schema6 + wan22_timestep_aware_roi_strength_v4 + FID1WanStrengthROIAnchor**。因为数值语义未变，所以不要为同一个实现增造schema7/v5新节点类；不得覆盖/重写V008、V007、V006等任一原profile。
- V009必须与V008完全保留 approved source SHA=6476cf1e17105b3589095918a46546baced0db35ef2a6ca235551f4b7002149f、seed2026100803、正负prompts逐字、尺寸576×1024、49/24、Wan2.2-TI2V-5B、20steps/CFG5/uni_pc/simple/denoise1、shift8、两处face ROI [0.11,.20,.36,.36]/[.69,.20,.89,.37]、feather4、strength0.55；第三个ROI仍称BACKGROUND_TREES，strength0.65、feather4，**仅改变它的四个几何坐标**。profile_id与hypothesis自然更新；更改白名单为 {profile_id,hypothesis,BACKGROUND_TREES.x0/y0/x1/y1}。不能加任何新的时间权重，也不能暗改人物/负提示词/采样/ROI强度。
- **绝不猜一组新的背景坐标**：在E盘用同一源PNG的完整像素、正确SOURCExVIDEO对齐方式、原take10全49帧和原take09裁片，先划出至少一个真正静止的远景树木区，并逐像素确认不包含红/金冠翎、服装、人物肢体、流水/瀑布或明显运动雾气；还须检查人物冠翎在49帧中的实际轨迹并预留边界安全距离，不能只看首帧静态叠层。候选box应满足既有 schema6 潜网格不重叠及面积限制，并产生有效羽化区域；若要求中心实测alpha=0.65，应在36×64网格上至少有9×9个latent cells，否则如实记录实际最大alpha，不得误标达到0.65。
- 新生成 overlay/pixel crop/hash/coordinate mapping/report 必须绑定 source原字节SHA、V009 profile字节SHA、视频take09/take10真实hash、帧1/25/49及所有49帧参考。由本地审查者明确签署 **STATIC_BACKGROUND_GEOMETRY_INSPECTED**（仅表示工程几何已检查，不是用户视频视觉批准），同时记录plume动态边界、区域语义、羽化后的有效latent坐标和非动态内容截图。只读保存V008_GEOMETRY_BLOCKED证据，不覆盖既有旧overlay或QA。
- 如果完整源图和49帧中**找不到满足静态、非人饰、非水流且潜空间尺寸合理的背景框**，本次纠正阶段必须返回NO_SAFE_BACKGROUND_ROI / GEOMETRY_BLOCKED，**不建立可执行V009、不偷偷移除BACKGROUND_TREES、不去改旧schema6的三ROI白名单、不自动增加GPU试验**。这是一条完备的失败停止路径，而不是让执行工位自行猜图。
- take14已由V008计划占位但并无真实job，本合同不复用这个身份。新的候选任务目录只可能是unused take15；正式离线prepare前先验证目录不存在，存在则停止，不能自动take16。
- 允许 V009 工程数学使用已经审核的v0.2.0节点和策略：不重构MODEL sampling、不改Wan条件mask、不动source latent、noTorch仍可离线prepare。该纠正原则上可不改业务节点源码，仅增加新profile、几何/图链验证、相关测试及文档；需要对语义几何环节做硬门禁时，加入最小独立metadata receipt校验，但不能把OCR/简单颜色自动判定等同于有真实审核者看过图像。

## 4. 逐文件/验证/门禁（整个纠正阶段一次完成）

| 文件或目录 | 必做行为 | 拒收条件 |
|---|---|---|
| config/source_fidelity_trials/SH903_FID1_V009.json（仅几何通过后创建） | 复制V008，仅背景ROI坐标+ID+hypothesis受控变化，唯一 profile_id | 修改既有V008/V007/v0.2.0；变更seed、prompts、faces、strength |
| docs/reviews/20261015-fid1-v009-geometry/（新增） | 保存原图/ROI叠层、静态内容与冠翎轨迹核对、整段49帧对照、hash和可复验的几何检查结论 | 原source/历史图被覆盖或把局部拉普拉斯方差当静态语义通过 |
| scripts/fid1_geometry_guard.py（必要时新增） | 对V009 geometry receipt做不可变字节hash、source/profile/ROI几何/overlay绑定；证据缺失或标记GEOMETRY_BLOCKED时拒绝 | 默认自动写PASS、假装机器能确认场景语义、无权限越过Jovi人审 |
| scripts/source_pilot.py / scripts/submit_prepared.py（仅门禁接线所需） | 若新增receipt guard，对新V009的prepare和dry-run/execute一致校验，receipt hash纳入job.sources，并在prepare发布前/submit锁内/runtime后复核 | V008在无几何确认时被真正submit；改变旧schema1–5历史语义；重封旧jobs |
| scripts/fid1_wan_latent_anchor_node.py / preproduction.py / fid1_graph_audit.py | 原则零业务算法修改；继续使用v4真实双边MODEL0/LATENT1、同样alpha数值与runtime node class | 换用V007时间权重、改老v2/v3、mask方向或MODEL链错误 |
| tests/test_fid1_strength_profile_unittest.py及独立几何负例 | 实际V009白名单、所有49帧叠层证据hash、无torch准备/默认dryrun、旧V008 block测试、乱序/错sha/动态区域的负例，资源门禁不降级 | 只有字段存在测试、没有非法几何和证据漂移拒绝 |
| VERSION.json / CHANGELOG.md | 若本阶段有真实受控修复，使用中文Commit并发布新的fid1-v0.2.1不可变标签（或按实际兼容影响选择版本），保留v0.1.0/v0.1.1/v0.2.0 | 把本计划docs SHA当修复SHA、移动已发布tag、英文独立提交 |

- schema6的现有严格三ROI IDs和强度范围可复用；源码已有load_trial_profile、MODEL+LATENT graph、submit资源守卫，默认不重写第二套。带新geometry receipt时区分**工程几何审核**与**Jovi视觉批准**。即使新V009能离线prepare，也不能以此替代新插件部署、真实RAM充足或Jovi今后视频的接受。
- 不允许为修复几何直接操作take10/11/12/13或take09用户反馈：take09 Jovi已CHANGES_REQUIRED，take10 Jovi仍PENDING；现有V008纯工程候选记录仍GEOMETRY_BLOCKED。旧644/646等哈希基线不可被本次提交更改。

## 5. 资源/部署/GPU硬门禁和下一次唯一可能运行

- 当前有三项关闭条件：V008背景几何失败、约0.98GiB可用RAM低于8GiB、已部署插件旧SHA。修复V009几何不自动解除另两项。V009离线准备可在没有ComfyGPU服务时完成，但必须先证明来源和geometry receipt有效。
- 保留现有submit_prepared强制8GiB可用物理RAM + 8192MiB空闲VRAM，同时验证数值真实可信、驱动/模型/依赖hash、Comfy单实例和/queue空、/object_info/FID1WanStrengthROIAnchor插口、精确部署node文件SHA。任一不满足：exit失败、零submission_intent、零POST；未知history禁止重投。
- 精确部署只使用现有fid1_deploy.py的owned package校验/幂等/rollback。没有另行授权不拆卸已有节点、重启Comfy或清理其他项目进程；不能为通过门禁修改内存阈值/降低分辨率/换14B/新平台。
- **本纠正阶段：NO NEW GPU。** 若未来Jovi明确给出单次V009 SH903试拍授权，在几何审查、同SHA新CI、现场资源与节点校验均通过后才能最多1次新的take15，49帧24fps576×1024/Wan5B/GPU并发1；未知Comfy history先调查而不重新POST，不自动运行SH901/902。
- 如果RAM仍不足或静态树木区域找不到，允许返回ENGINEERING_READY_GEOMETRY_OR_RESOURCE_BLOCKED，必须给出真实观测/错误退出码，而不是强行生成媒体。

## 6. E盘连续执行步骤、命令与验收

从E:\\project\\AI-short-vidio-claw单一Codex工位接收本文档。先核对当前分支、Git HEAD、状态、旧v0.2.0 tag、Owner tasks、Obsidian、source/png与历史take01–13/hash；获取本docs PLAN_SHA 后比较111cb3f到PLAN_SHA**恰好一份新docs**。不要reset/clean/force-push/main merge；如果当前有新的并行修改则先保全并停止冲突合入。

（一）静态审计与图像修正：使用批准PNG/source sha与真实take10 49帧、旧take09只读帧，通过本机Pillow/openCV（若既有依赖可用，优先Pillow）产生候选背景静态区叠层及具时间轨迹的可核验图；人工检查冠翎与动态水雾绝不交叉，并选择唯一安全框。**无可用框即阶段STOP，保留证据。**

（二）数据冻结：新V009与V008 JSON差异只容许profile_id/hypothesis/BACKGROUND_TREES四坐标，ROI几何review绑定profile/source/overlay/frame hashes且当前明确为STATIC_BACKGROUND_GEOMETRY_INSPECTED；不得自动预填用户视觉PASS。

（三）离线准备与逻辑回归：先在TemporaryDirectory合成来源/批准fixture检验V009 prepare→default submit dryrun、lock与依赖漂移拒绝、schema/ROI/receipt越权；只有源图几何真实通过且新代码hash固定后，才允许现实E盘 unused take15 的offline prepare。所有原V008 job未创建和历史take11–13不重封；所有新jobs仍T1_SOURCE_ONLY与eligible_for_final_cut=false。

（四）全部工程验证，真实命令：

    python -m unittest discover -s tests -p "test_fid1*unittest.py" -v
    python -m unittest discover -s tests -p "test_source_fidelity_profile.py" -v
    python -m unittest discover -s tests -p "test_*.py" -v
    .\\local\\comfyui\\image\\venv\\Scripts\\python.exe -m unittest discover -s tests -p "test_fid1*unittest.py" -v
    python -m compileall -q scripts tests
    git diff --check
    python scripts/sync_repo_media.py --check

保存解释器、真实exit、skip原因、真实CPU Tensor和noTorch子进程日志；不得借用历史359/117作为新版通过。复核不可变旧tag、旧source/profiles/takes、批准及原30镜644+保护hash；有差异必须解释并fail closed。

（五）同一个完整阶段本地自审和Git交付：核对所有staged/unstaged diff、解决负例失败→全量重测→中文Commit、更新VERSION/CHANGELOG、新fid1-v0.2.1注释tag（不覆盖v0.2.0），保持PR12 open/unmerged。读取**新真实实现40位SHA**对应四项GitHub Actions并核对全量/CPU Torch日志及PR merge ref，失败就修正后再次完整回归。这个版本只代表工程/几何准备完成；不是新视频已生成。

（六）本地回传固定字段：

    [C2C] STATE: EXECUTED / BLOCKED TASK:c2c_fid2
    PLAN_SHA:<本docs唯一提交40位SHA>
    BASE_SHA:111cb3fb07ab560cc88d346dcff02316f26e16c2
    IMPLEMENTATION_SHA:<本地真实新40位SHA或NO_NEW_IMPLEMENTATION>
    TAG:<新不可变版本或NOT_CREATED>
    V008:GEOMETRY_BLOCKED; OLD_FILES_PRESERVED
    V009:<GEOMETRY_APPROVED_FOR_ENGINEERING或NO_SAFE_BACKGROUND_ROI>
    GEOMETRY:<原图/source SHA/新box/latent映射/图像+49帧路径与hash/审查记录>
    TESTS:<真实full、TorchCPU、noTorch、负路径>
    CI:<新HEAD四个run/job/checkout_sha/conclusions>
    PROTECTED:<旧source/profile/take/原审批前后hash>
    DEPLOY:<旧/新node字节与加载状态/NOT_DONE>
    RESOURCE:<最新RAM/VRAM/磁盘/queue/intent>
    REAL_JOB:<take15 NOT_CREATED 或 OFFLINE_PREPARED_NOT_SUBMITTED>
    GPU:NOT_RUN
    HUMAN:take09=CHANGES_REQUIRED;take10=JOVI_PENDING;V008/V009=NOT_RUN
    DOWNSTREAM:SH901_SH902_BLOCKED; FORMAL30_UNAPPROVED
    FINAL_REVIEW:<独立diff结论与剩余真实门禁>

## 7. 明确必须退回CHANGES_REQUIRED的情况

1. 用原V008名字/hash/背景框“修正”成不同视频任务或覆盖旧take/profile/人类反馈；使用take14做本次后继实验。
2. 原批准PNG与新叠层SHA未对应；背景树木候选仍包含红色头冠长翎、人物服装、流水/瀑布/动态雾，或仅检查矩形不相交就自动允许准备。
3. V009改变prompt/seed/face ROI/强度、Wan2.2-5B、49/24、576×1024、模型/采样预算，或将V007 temporal权重混入v4。
4. 丢失旧R1–R4事务保护、历史schema2–5、Wan基础mask首格/未来条件、sigma-noise对齐、非ROI自由生成、MODEL0/LATENT1真实活边。
5. 未实际测试真实Torch数值、来源保护、noTorch/legacy、非法geometry和资源/部署阻断，或CI指向旧SHA。
6. 视觉几何/新资源失败时仍触发GPU、部署覆盖未知节点、降低资源阈值、进入SH901/SH902、伪造Jovi视觉接受。
7. 缺中文Commit/版本文件或移动现有fid1-v0.2.0标签、PR被合并。

## 8. 本网页任务结束状态

实际完成：独立读v0.2.0代码数学、schema/graph/runtime部署门禁、相关real Tensor/noTorch测试、同一HEAD四项CI及完整日志、注释tag、646项保护记录；通过GitHub读取BACKGROUND_TREES.png实际裁片并发现清楚红冠翎，几何映射与ROI_geometry.json吻合。得出工程接受但V008几何拒收，提交本纠正合同一份docs。没有对原型或Git工作区写业务代码，没有GPU、没有部署、没有修改Jovi反馈/旧审批，不把人类视觉评价伪造为通过。
