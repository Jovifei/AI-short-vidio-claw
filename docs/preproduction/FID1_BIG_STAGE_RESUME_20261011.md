# Jovi：新对话的一次完整远端工程阶段

## 2026-10-13 分工更新与本地恢复点

Jovi随后明确：先用同一短剧Project的ChatGPT网页端核验真实执行能力；网页端不能完成完整执行时，由它给方案/复审，E盘Codex负责实施。网页端已确认缺少可运行ComfyUI、Wan 5B权重与GPU，也不能保证Actions运行/修复闭环，并已明确停止PR12写入；它继续作为方案咨询和接收固定SHA后的独立复审方。以下2026-10-11“远端全权实施”段落是历史授权记录，不覆盖这次角色更新。

本地已安全快进到远端当时提交`c2d58e1c40563c8c588ac12e08cd421ea8b4d46f`，分支`codex/fid1-remote-repair`；不含本地`tasks/`笔记。工作开始前独立核对Wan源码快照和当前项目Comfy实例：当前Comfy根`local/comfyui/image/ComfyUI`、Python `local/comfyui/image/venv/Scripts/python.exe`、源码SHA`6b747c0428c343e1417219641db93a4fb7cb69ae`；`nodes_wan.py`、`latent_formats.py`、`samplers.py`、`sample.py`与审核manifest全部逐字节匹配。F盘`F:\ComfyUI`只是模型/桌面数据目录，不是本项目源码根。

**必须遵从的实测mask极性：** ComfyUI `noise_mask=1`表示采样/denoise，`0`表示保持传入latent。Wan22image latent对49视频帧输出`[1,48,13,H,W]`，首时间格mask为0、未来12格mask为1；采样节点把该mask当denoise mask。故source ROI锚定必须使用独立anchor mask A，未来ROI复制首latent后令`D = D_base * (1-A)`；绝不能把A直接当noise_mask。`1`全denoise，`0`全冻结。

本地实现进度与后续证据更新见`tasks/todo.md`、`local/reports/fid1_*`及Obsidian工作笔记`E:/AI_Tools/Obsidian/data/notes-work/codex_prj/AI-short-vidio-claw/11-远端保真修复接力与PR12验收.md`。SH903 take04仍是单次新任务，`visual_accepted`及正式30镜批准不会由单测、ffprobe或试拍自动授予。

这是同一保真修复目标的接续。2026-10-11，Jovi明确要求保留旧聊天和GPT-6极高，在既有短剧Project新开对话。工具核对成功后，一次完成审核、修复、下一阶段规划与实施、完整测试复审及GitHub固定提交；本地在E:/project/AI-short-vidio-claw按最终SHA验证。不交付只审计/辅助helper/待下一步的中间结果。

## 角色与交付

远端负责全部工程设计、实施、回归、CI失败修复和自审，持续到PR12最终可验证HEAD。C2C是只读数据连接，不等于GitHub不能写；需要时先动态搜索/加载工具再调用，不因顶层命名空间未展开而声称缺权限。GitHub文件写入必须显式branch=codex/fid1-remote-repair，禁止main写入、重置历史、强推或自动合并未验收PR。原聊天保留，新对话不依赖加载旧长历史。

当前精确基线：5bc90cb86fc8587ea5ecf28270f97bb08f6b5eee。诊断及审核材料共同祖先：acab47dddc58ef563b433af7ae327cc07d351be0。完整早期合同为FIDELITY_REPAIR_REMOTE_STAGE_20261011.md；本文件补充最新失败和下一工程阶段，不能以早期入口中的已完成接收任务取代当前目标。

## 需要实际读取的证据

- PR12及本地验收评论：6106873879、6106938239、6107128188、6107307415、6107367249、6107429482、6107455158、6107480577。
- docs/reviews/20261011-source-fidelity/：5个实际ComfyUI视频、首中尾/all49及53项原字节审核/路径归一化metadata的manifest。视频是审核副本，不是已批准成片。
- comparisons/faces_last_comparison.png、face_boundary_comparison.png；实际使用read_image或等效可视工具检查，不能只读QA文字。
- 精确本机ComfyUI源码审核副本：installed_comfy_source/comfy_extras/nodes_wan.py，installed_comfy_source/comfy/latent_formats.py、comfy/samplers.py、comfy/sample.py；含GPL license和hash manifest。与本机关键模块Git内容相同，来源Comfy-Org/ComfyUI@6b747c0428c343e1417219641db93a4fb7cb69ae。
- source_pilot.py、preproduction.py、submit_prepared.py、p1_comfy_probe.py，当前全部fid1 helper/node/test和6份GitHub workflow；不能忽略旧测试或脱离真实prepare链。
- 本地最新收尾详证：local/reports/fid1_relay_closeout_20261011.json、pr12_5bc_actual_node_contract.txt、pr12_5bc_graph_closeout.txt，可通过本项目C2C读取。

## 已经完成的输入与批准

32PNG已接收并全部hash匹配，重复同步copied=0、already_present=32。Jovi真实批准SH901/902/903仅T1_SOURCE_ONLY；原LOOKREEL/EP001仍0/30精确输入批准，不能把这说成仓库无图片。原source approvals/snapshot、原registry和30镜批准表保持不变。人物、剧本、技术主线不更换。

SH903来源REFB02_01.png，原941×1672，SHA6476cf1e17105b3589095918a46546baced0db35ef2a6ca235551f4b7002149f。take01 480×832明显转头/人脸化；take02仅改提示仍需修改；take03同提示576×1024有改善但未获视觉批准。均seed2026100803、49帧/24fps、现有Wan2.2-TI2V-5B、20steps/CFG5/uni_pc/simple/denoise1。再换一套同尺寸提示不算实际保真修复。

## 当前真实失败

现有latent primitive的4项真实CPU tensor测试通过；shape-only Fake对象4项通过，不代表实际节点行为。实际Comfy LATENT dict形状[B,48,T,H,W]，noise_mask为[B,1,T,H,W]；49视频帧对应T=13，不能混淆。

本地对5bc90cb现有FID1LatentROIMerge做真实CPU数值复现：输出仅samples，丢掉原noise_mask；首源ROI=7而未来ROI仍=0，未从首格初始化；全帧mask、NaN mask被接受，输出出现NaN。MASK接口不能假定直接提供五维时间mask。未安装该错误节点，未提交任何新增GPU任务。

graph_audit5项：3通过、1失败、1KeyError，exit1；GitHub对应CI3通过、Media recovery失败。旧pytest-only3个常量断言也没有集成到unittest CI。prepare/submit尚未集成实际新机制、没有有效take04冻结包与部署/回退交付。

## 一次完整完成的工程范围

### 核心修复

审计并选择有依据的现有5B保真数值干预。可验证候选是将指定未来ROI从实际已编码首格latent初始化，同时更新真实noise_mask，保持首帧原约束和非ROI区域的微动。不能直接锁住未初始化未来零latent，不能整帧/全时冻结后冒称微动，不能做输出换脸或替换源人物。候选局限需要如实描述，离线正确不等于视频视觉通过。

实现可由既有ComfyUI加载的独立有界节点/包；兼容真实LATENT dict并保留元数据。拒绝非有限/无效ROI、全帧冻结、shape/channel/时间/dtype/device不匹配等。源码、参数、source hash和节点实现版本必须可冻结并校验；部署需最小化、幂等、不覆盖冲突，并给准确回退步骤。不装14B、新runner/平台或训练LoRA。

### 运行链与下一工程阶段实施

完成source_pilot prepare与submit_prepared严格集成：实际冻结graph从已批准LoadImage→正确Wan22 latent→真实anchor→KSampler→VAE→Video/Save；不能靠调用者填写布尔值或包含reference文字证明条件存在。保留旧默认prepare、原V5 guard和正式30镜不变；依赖/实现hash/graph链接/源或批准漂移必须明确拒绝。离线prepare不要求普通本地Python装Torch，不能在失败时跳过guard继续POST。

下一工程阶段在既有源图诊断范围实施：支持SH903通过本机验证后的SH901→SH902串行扩展，逐镜明确输入hash、profile/ROI和seed，禁止泛用SH903 ROI或代批。实现统一实际QA/回传工具：真实ffprobe、完整输出hash、首中尾/all49、资源统计及身份/服装/肢体的待人工判定记录；区分latent timestep、视频frames、runtime_success、visual_accepted和final_approved。给完整可执行runbook、job目录与再prepare规则，规范未知history先核对、不重复POST。

规划后续正式LOOKREEL/EP001接力并落实允许的代码/状态/门槛工具，明确远端仍欠的20张精确剧情图、来源修订及HOME/RAIN/受伤独立状态。不得越过当前批准和媒体缺口，不能以source小样替代成片或生成假的正式批准。

### 完整测试与复审

补真实CPU张量和实际prepare/submit/CLI/部署的集成与负路径测试，不用Fake形状断言替代运算验证。覆盖首格保护、未来源ROI初始化、非ROI仍可生成、NaN/Inf/全mask拒绝、有效尺寸/模型/帧数、错误/未批准源图、hash与依赖漂移、孤立节点、错误边/参数、幂等/冲突/旧take不覆盖、普通Python无Torch的离线入口。测试批准fixture必须标注合成，不能冒充Jovi。

让新增测试被CI真正执行，数学测试用真实受支持的CPU Torch；修复所有旧测试和所有相关workflow失败，不能只跑新增文件。通过GitHub Actions完成远端可执行测试；没有shell并不阻止使用Actions。针对最终HEAD完成独立复审并修复再跑，报告测试数量、命令、CI链接和真实NOT_RUN项。

### 固定交付

更新PR12和状态/runbook，给最终40位HEAD、变更/机制/风险、全部测试与复审证据、精确部署及回退命令、固定source/seed/frames/fps的新take04 prepare与默认dry-run命令、资源边界、完整本地接收验证步骤。不要把中间commit、只有helper的PR或下一阶段计划当最终交付。除不能自行解除的外部阻塞外，持续完成整个阶段后再结束回复。

## 本地接收边界

E:/project/AI-short-vidio-claw保留未提交tasks笔记、local素材与Obsidian；按远端最终精确SHA安全fetch/ff-only验证。只有实现/guard/tests/dependency均通过后才部署到现有ComfyUI并准备一次新take04。Jovi已有本地试拍授权，GPU并发1，49帧/24fps、5B；状态未知不重POST。实际输出仍需Jovi视觉批准，原30镜及正式生产T1不能据此通过。
