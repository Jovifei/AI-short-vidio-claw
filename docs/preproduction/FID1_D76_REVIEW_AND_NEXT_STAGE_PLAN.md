# FID1：d76 独立复审与完整下一阶段执行合同

STATE: PLAN
TASK: c2c_f2a1
AUDITED_COMMIT: d76a75b86c30c71e1f502afc6354734210317779
IMPLEMENTATION_BASE: d76a75b86c30c71e1f502afc6354734210317779
BRANCH: codex/fid1-remote-repair
PR: https://github.com/Jovifei/AI-short-vidio-claw/pull/12

> 本文是已进行代码/证据审核后形成的执行计划，不是修复已完成的声明。本文所在提交只改变计划文档。R1–R4 的代码修复、回归与最终实现提交由本地 Codex 完成；网页方在收到固定实现 SHA 后独立复审。当前 take09 人工视觉接受仍为 PENDING，不能以本计划授权或测试通过代替 Jovi 的真实反馈。

## 0. 本轮授权及工作区核对

Jovi 本次授权覆盖：审核 d76、把完整计划/复审文档提交指定 GitHub 分支。它只覆盖此前网页只读限制中的文档写入例外，不授权网页修改代码、配置、workflow、PR 元数据、main、合并或强推。

真实调用结果：

- C2C `workspace_info` 成功：workspaceId `04f9cfdf549f`，name `AI-short-vidio-claw`，branch `codex/fid1-remote-repair`，short HEAD `d76a75b`。
- C2C `git_status`：ahead=0、behind=0，staged/unstaged/conflicted 均空；仅未跟踪的 `tasks/lessons.md`、`tasks/todo.md`。保留，不加入提交。
- 工具只暴露 `workspace:/`，并不直接返回操作系统根路径。已读取 `local/reports/fid1_review_server_20261013_01.json`，其中实际记录的审片服务目录位于 `E:\project\AI-short-vidio-claw\local\production\T1_SOURCE_PILOT\review_sessions\SH903_take09_20261013_01`；本地接收时仍用 `git rev-parse --show-toplevel` 核对 E 盘根，不把别名当绝对路径证明。
- GitHub PR12 与 branch ref 实际读取均为完整 HEAD `d76a75b86c30c71e1f502afc6354734210317779`，open/unmerged。
- 已读本项目 `docs/preproduction/FID1_NEXT_SOURCE_STAGE_20261013.md`、`AGENTS.md`、下一阶段审核目录的四个文件，以及相关实际代码/测试。此前该合同的 C2C 错误/404 不再作为本轮阻塞。

## 1. 审核证据与边界

### 1.1 对比范围

`e94e992a544667fb91579b9bfc876c55eb54d711...d76a75b86c30c71e1f502afc6354734210317779` 为一个快进提交，19 个文件改变。改动涉及两份 V002 profile、原阶段合同/runbook/脚本说明、四份审核材料、前驱/反馈模块和相关测试；没有改变 Wan 核心节点实现、正式30镜批准或旧 take 媒体。

本轮实际通读的执行链：

- `scripts/source_pilot.py`：`prepare_trial`、`load_trial_profile`、依赖列表。
- `scripts/fid1_predecessor.py`：`validate_predecessor`、`validate_predecessor_receipt`。
- `scripts/fid1_qa_report.py`：`record_visual_review`、`verified_run_output`、`create_report`、`_contact_sheet` 和 CLI。
- `scripts/fid1_review_contract.py`：严格反馈 schema 与四项标准。
- `scripts/fid1_visual_feedback.py`：页面构建、材料 hash、导出 JavaScript。
- `scripts/submit_prepared.py`：离线校验、独占锁内校验、runtime 后再次校验。
- `tests/test_fid1_predecessor_unittest.py`、`tests/test_fid1_visual_feedback_unittest.py`、`tests/test_fid1_profile_schema_unittest.py`、`tests/test_source_fidelity_profile.py`。

固定代码入口：https://github.com/Jovifei/AI-short-vidio-claw/tree/d76a75b86c30c71e1f502afc6354734210317779

### 1.2 已核实的测试，不冒充本轮重新运行

C2C `execution_output(action=list)` 后实际读取 id=10，task `c2c_f2a1` iteration=1、exitCode=0。该输出有截断，所以另读完整本地日志尾部：

- `local/reports/fid1_next_stage_full_tests_20261013.txt`：Ran 306 tests in 127.918s；OK (skipped=3)，即303通过、3个既有Windows符号链接权限跳过。
- `local/reports/fid1_next_stage_comfy_tests_20261013.txt`：Ran 68 tests in 13.466s；OK。68是Comfy venv中的FID1套件，不表示68项全部是数值测试；其中保留真实CPU Torch运算测试。
- GitHub实际读取 d76 关联 Actions：
  - Preproduction V5 #44：38340040978，success。
  - Media recovery #42：38340040994，success。
  - Launch input contracts #34：38340041012，success。
  - Committed media/source pilot #32：38340041034，success。
- 实际读取 Media recovery job `115108736808` 完整日志：安装 `torch==2.14.1+cpu`，执行 `test_*.py`，Ran 306 tests in 54.132s，OK、无skip。反馈客户端测试、前驱漂移、无Torch入口、runtime期间漂移负例均在日志中出现。

CI链接：

- https://github.com/Jovifei/AI-short-vidio-claw/actions/runs/38340040978
- https://github.com/Jovifei/AI-short-vidio-claw/actions/runs/38340040994
- https://github.com/Jovifei/AI-short-vidio-claw/actions/runs/38340041012
- https://github.com/Jovifei/AI-short-vidio-claw/actions/runs/38340041034

准确的checkout限定：所读Media recovery日志测试的是PR合成merge commit `c18e23b366f15613368c3bafcd932f7faca6b3e9`（d76与main的测试合并引用），不是已合并main，也不能把这个值冒称分支HEAD。最终回传同时记录关联head_sha和checkout_sha。

### 1.3 人工与媒体证据

实际读取本地 take09 `qa/qa_report.json`：完整播放、身份、服装、肢体、decision均PENDING；输出仍绑定 `dbdd44e4bdd39b13c8881c3f413a7889f0823c052b99df41698b1d5f61be2db8`。

`docs/reviews/20261013-fid1-next-source-stage/browser_check.json` 记录浏览器播放到2.041667秒、七图加载、五个选择及reviewer/quote保持空、默认导出拒绝。这是Codex界面测试，不是Jovi验收，也不是本轮网页复审者播放了视频。本轮没有MP4完整播放能力证据；源图 `read_image` 尝试超时，因此不追加独立像素/ROI接受结论。profile几何检查目前来自已读取的 `profile_receipts.json`，不是新的人物审批。

### 1.4 审核结论

前驱固定到失败take04、submit不复验、缺独立V002等旧问题已在d76解决，不能重新列为未实现。测试绿灯真实成立。但人工反馈落盘仍有本次发现的事务漏洞，以及路径/帧标记问题；当前代码独立复审结论为 `CHANGES_REQUIRED`，不是全包无问题。

下面的修复均纳入同一个本地完整阶段。不要重写已经正确的前驱方案，不增加另一个runner或平行实现。

## 2. 可操作发现及关闭标准

### R1 / P1：失败写入者可能误删另一写入者的反馈证据

位置：`scripts/fid1_qa_report.py:142-197`，尤其 `open("xb")` 与异常分支 `evidence_path.unlink()`。

存在性检查与独占创建之间有窗口。若另一写入者抢先创建同名同字节文件，当前 `open("xb")` 抛 FileExistsError，但异常清理只比较文件hash，仍会删除他人已创建的证据。内容相同不等于当前调用拥有文件。

本轮在隔离临时目录复制该函数体、用合成材料和故障注入重现：FileExistsError；另一写入者文件被删除。没有操作E盘/真实批准，没有执行完整仓库套件。

修复：应用前获取该job专用review锁；保留独占创建；只清理由当前事务成功创建且仍属于本事务的对象。至少记录created/ownership token，必要时比较文件身份。创建失败时绝不删除目标。锁获取失败也不得清理他人的锁。QA发布失败时保留可诊断的状态；不得把相同hash当所有权证明。

关闭：两个竞争写入者只能有一个成功，失败者不得删除/覆盖胜者的证据、QA或锁；同内容与不同内容两种竞争均有确定性回归。

### R2 / P1：校验对象、保存字节及QA比较基线不是同一快照

位置：`scripts/fid1_qa_report.py:148,157,167,179-192`。

反馈先 `read_json` 校验，后 `read_bytes` 取保存字节；中间改动可造成QA记录ACCEPTED，而保存证据为CHANGES_REQUIRED。QA同样先解析，较晚才计算 `original_report_sha`，中间更新可能成为新的比较基线，随后被旧解析对象覆盖。

本轮隔离故障注入的实际结果：

1. 反馈在校验后更换：返回APPLIED，QA=ACCEPTED，保存证据=CHANGES_REQUIRED。
2. QA在首次读取后、后续hash捕获前改变：返回APPLIED，并丢失并发新增的QA字段。

现有前驱检查会拒绝第一种不一致，所以不声称已证明下游GPU绕过；问题是错误成功反馈、证据不一致以及潜在丢更新。

修复：在同一持锁事务内各读一次反馈raw和QA raw；用同一raw完成严格JSON解析、schema校验、hash及保存；用最初QA raw hash作比较基线。验证反馈、job/integrity/run/实际MP4绑定；发布前再次检查原快照，发生改变即拒绝且不覆盖。新代码仍不要求历史实现hash等于当前代码。所有新的apply路径统一使用这套逻辑。

可新增可选 `--expected-feedback-sha256` 和 `--expected-qa-sha256`（以及对应keyword参数）用于绑定上一条preview。它们是本阶段待实现接口，不是d76现有参数；现有preview/CLI入口保持，给定期望hash时必须严格匹配。stage交接中的人工apply使用这两个pin；不以用户姓名字符串/hash充当真实身份认证。

关闭：上述两种竞态各有红转绿测试；dry-run不写文件；成功返回前复读一致；异常/崩溃不留下可误认为已接受的半包。若落盘中断后有孤立证据，返回RECOVERY_REQUIRED并保留证据，不能自动删用户材料或自动重放接受。

### R3 / P2：新FID1 job输出路径与后续审片/前驱路径合同不一致

位置：`source_pilot.prepare_trial` 仅要求destination在LOCAL下；`fid1_visual_feedback.build_review_page` 和 `fid1_predecessor.validate_predecessor` 要求 `video/SH90x/jobs/takeNN`。

因此调用方可把新job放在 `quality_take02` 或另一个shot目录；prepare允许的产物后续可能无法进入审片/前驱链。现有部分合成测试本身使用非标准输出目录，未覆盖这类端到端拒绝。

修复：对新FID1 schema-2 job强制目标路径是 `local/production/T1_SOURCE_PILOT/video/<实际shot>/jobs/take[0-9]{2,}`；统一prepare、submit和反馈写入的路径/shot一致性检查。在resolve前检查路径组成、链接/junction/reparse，避免先解析后丢失别名信息。失败必须在创建最终目录前发生。非FID1旧默认入口不扩大修改；历史非标准job只读保留，绝不改名/重封已完成任务以迁就新规则。

关闭：错误shot目录、非标准take、`..`、跨scope、symlink/junction负例都拒绝；三个shot的标准路径正例、原默认入口和历史只读正例保留。

### R4 / P2：首中尾拼图把实际第1/25/49帧标成1/2/3

位置：`fid1_qa_report._contact_sheet` 按传入列表enumerate编号；`create_report` 传入 `[frames[0], frames[len(frames)//2], frames[-1]]`。

这是代码可直接确认的展示错误，不是第2/3个视频帧。过去根据三格图把中/末帧叙述为“Frame02/03”的审片描述不应继续使用。all49顺序本身不因此失效。

修复：拼图接受真实source frame index/时间；本49帧24fps片的三格应为1、25、49，时间0、1、2秒（片段结束时间约2.041667秒不同）。新QA保存frame索引映射。旧take09的job、run、QA、旧拼图不得重写；在新review_session生成带正确标记的衍生图，page_receipt绑定真实源帧/MP4与新图hash。可从已解码帧生成；缺源帧时从已核hash的MP4进行CPU解码到新session，不能再跑GPU。

关闭：验证传给绘图函数的索引和时间，不只测试文件存在；浏览器新页面显示正确标记，旧take09保护文件hash完全不变。

## 3. 下一完整工程阶段目标与不变项

阶段目标：关闭R1–R4，完成可安全记录真实反馈的事务链与准确审片界面，保留d76的显式前驱及独立V002，完成全部回归/CI/独立复审，交付固定实现SHA。人工反馈缺失时也必须完成所有可独立工程工作，最终状态使用ENGINEERING_READY_WAITING_HUMAN，而不是伪造全阶段视觉通过。

不变项：

- 本地实现目录 `E:\project\AI-short-vidio-claw`；唯一实现分支 `codex/fid1-remote-repair`、PR12。
- `scripts/fid1_wan_latent_anchor_node.py`、原生产workflow、模型与采样算法本阶段原则上零diff；除非新证据证明必须修改且另获确认，不再做羽化/噪声/seed调参。
- Wan2.2-TI2V-5B、576×1024、49视频帧/24fps、13 latent时间格、GPU并发1。
- 原生Wan条件mask保留首格0/未来1；timestep-aware节点仅在克隆MODEL的采样hook实施ROI保留；MODEL output0和LATENT output1必须都通向KSampler。noise_mask语义1=denoise、0=preserve，不能与anchor alpha混为同向mask。
- 20steps、CFG5、uni_pc/simple、denoise1、ModelSamplingSD3 shift8/flow/multiplier1000不变。
- take01..09和失败take08记录、原源图/审批快照、正式30镜registry/批准、tasks笔记及Obsidian原样保存。
- 无新增模型/LoRA/平台、无第三方付费、无正式剧情图猜补；32图存在和source试拍不等于20张精确剧情图、HOME/RAIN/受伤状态或正式30镜批准已完成。
- 本计划不授予任何下游GPU执行权。当前不运行SH901/902；后文是仅在真实前驱接受且本地执行授权均成立后的运行合同。

## 4. 文件级实施清单：复用已存在实现

| 文件 | 本阶段操作 | 不能做的替代 |
|---|---|---|
| `scripts/fid1_qa_report.py` | R1/R2事务修复；单快照解析/保存、锁所有权、preview pins；R4真实frame编号 | 不重建take09、不预填接受 |
| `scripts/fid1_review_contract.py` | 复用严格schema；必要时提供共用raw解析/路径校验小函数 | 不放宽字段、重复键或PENDING接受 |
| `scripts/fid1_visual_feedback.py` | 新session的正确帧标记和receipt；必要的记录入口一致性 | 不覆盖现有session；不把ended事件设为PASS |
| `scripts/source_pilot.py` | R3新FID1规范输出路径；保留--previous-job及发布前复验 | 不恢复take04常量，不扫描latest |
| `scripts/submit_prepared.py` | 复用同一目标路径校验；保留锁前、锁内、runtime后前驱复验 | 不从直接调用probe绕过门禁 |
| `scripts/fid1_predecessor.py` | 原八文件receipt保持；复用必要路径校验，增加端到端负例 | 不要求历史依赖hash匹配当前实现 |
| `tests/test_fid1_qa_report_unittest.py` | 事务竞态、同字节所有权、快照一致、pins、失败清理、帧编号 | 不只测新增helper，不跳过实际record-review |
| `tests/test_fid1_visual_feedback_unittest.py` | 新session/标记/receipt、页面默认空、真实导出schema | 合成用户输入只能在临时fixture |
| `tests/test_source_fidelity_profile.py` | 三shot规范路径、旧入口兼容、已接受合成前驱prepare→dry-run | 不改真实批准后跑正例 |
| `tests/test_fid1_predecessor_unittest.py` | 增加记录器→receipt→下游校验集成 | 不删除现有漂移/重封负例 |
| 现有四项CI | 原套件保留，新增unittest自动收集；仅必要时做有理由的覆盖修正 | 不降级、删断言、假Torch或允许失败 |
| `scripts/README.md` / `docs/preproduction/LOCAL_SHOOTING_RUNBOOK.md` | 更新精确命令、pin与事务恢复、真实帧号及状态 | 不把计划写成已测结果 |
| 新本地阶段报告及对应 `docs/reviews/` 目录 | 问题处置、命令/exit/计数/hash、最终CI和保护文件证明 | 不提交任务私记、密钥、权重或伪造反馈 |

SH901/902的V002在d76已经存在并有测试，不再新建一套同义profile。V001/V005也不改。新依赖模块若确需加入，必须进入 `FID1_DEPENDENCY_FILES` 并验证prepare期间漂移；只写本计划文档不会改变该列表或使旧实现依赖变化。

## 5. 必须维持的数据与事务不变量

### 5.1 历史与待运行任务分离

已完成take09：用冻结job/integrity/workflow/input/run/QA/视频验证历史，不能因当前脚本升级而要求重跑或重封。

新待提交job：当前代码/profile/source/approval/graph的hash必须与prepare时完全一致。实现发生改变后旧待运行包失效，只能选择新unused take重新prepare，不能重写旧包绕过依赖门禁。

### 5.2 前驱receipt

d76已实现八文件：job、job_integrity、workflow、input PNG、run_record、QA、MP4、真实反馈证据；再绑定shot/profile/prompt/output身份，放入 `fid1_contract.schema_version=2` 和 `job.sources`。`job_integrity` 本身仍是schema1，不混淆profile schema4、job contract schema2、review schema1。

直接顺序固定SH903→SH901→SH902。选择必须显式 `--previous-job`；禁止latest、fallback、自身或跨shot。

保留直接前驱语义：SH902重验SH901的完成证据，SH901 job字节中包含它冻结的SH903 receipt；不为本阶段引入递归祖先扫描，也不声称当前实现会处理所有祖先事后撤销。若Jovi撤销已有接受，先停队列/下游计划，另以明确修订契约处理；不可自动覆盖旧证据。

### 5.3 人工反馈原子性

同一raw用于parse→validate→digest→persist；原QA快照hash从第一次读取时确定。所有apply入口受同一job锁约束。对外成功状态必须以最终持久化的QA/证据一致为条件。任意失败不得用以前缓存的PASS结果重新提交；外部编辑检测到漂移则中止。

锁只能约束遵守协议的本项目写入者；不要声称hash和文件锁能防止任意管理员同时篡改全部材料。对非协作编辑尽可能做快照重验，检测到异常即fail closed。

### 5.4 人类判断的信任边界

反馈中的reviewer='Jovi'不是密码学签名。执行方必须确实收到Jovi主动导出的真实JSON或明确具体判断；合成测试即使字段为Jovi/PASS也永远不复制到真实local目录。

完整播放、身份、服装、肢体分开；动作自然、背景/水面、ROI接缝、闪烁、静态贴片纳入页面提示和原话。四项或decision任何未完成，下一镜关闭。自动分数、ffprobe、GPU成功、浏览器ended不代判。

## 6. 本地连续执行顺序及命令

所有命令从E盘项目根执行。先读取本计划，不要求用户逐项发“继续”。每个外部命令检查退出码；记录真实时间/结果。以下不存在自动GPU队列循环。

### A. 安全接收计划并记录保护基线

`PLAN_SHA`取网页本轮最终返回的40位文档提交，不能填成d76实现基线或PR合成merge SHA。

```powershell
Set-Location E:\project\AI-short-vidio-claw
$Base = 'd76a75b86c30c71e1f502afc6354734210317779'
$PlanSha = '<本轮返回的40位文档提交>'
if ((git branch --show-current).Trim() -ne 'codex/fid1-remote-repair') { throw 'Wrong branch' }
git rev-parse --show-toplevel
git status --short
git fetch origin codex/fid1-remote-repair
if ($LASTEXITCODE -ne 0) { throw 'fetch failed' }
git cat-file -e "$PlanSha^{commit}"
if ($LASTEXITCODE -ne 0) { throw 'plan commit missing' }
git diff --name-status "$Base..$PlanSha"
# 必须仅有本计划/复审文档；出现实现、配置、workflow等额外变化先核对，不合并猜测。
git merge --ff-only $PlanSha
if ($LASTEXITCODE -ne 0) { throw 'not a safe fast-forward; preserve local work' }
git rev-parse HEAD
```

保留tasks两个未跟踪文件。基线保护清单应包含正式两集plan/approval、generated_assets_v5 registry、source_kit、32PNG、当前source approval snapshot、旧job/profile/workflow/run/output/QA及节点文件。记录路径+SHA256到新 `local/reports/` 阶段目录；不写回历史文件。反馈真实apply前后允许的变化仅该job的QA与新增真实证据，另行列出，不能把它混入“所有历史文件都未改”的声明。

### B. 红转绿复现与修复

先把R1、R2三种确定性故障注入写成仓库unittest，在临时目录复现；再修改实现并验证它们转绿。接着完成R3与R4。不要将本轮scratch的helper替身当仓库最终测试；最终测试必须调用实际 `record_visual_review`/prepare/submit/页面构建。

为R1/R2选择单一清晰事务实现，不新增外部数据库或服务。可选preview pins在help与runbook标明；保持旧反馈JSON schema1、历史审片兼容。审片锁、证据临时文件、恢复记录全部限制到本job或review_evidence，不清理整个local。

### C. 全部工程验证（不需要真实人类批准）

```powershell
python -m unittest discover -s tests -p 'test_fid1_qa_report_unittest.py' -v
python -m unittest discover -s tests -p 'test_fid1_predecessor_unittest.py' -v
python -m unittest discover -s tests -p 'test_fid1_visual_feedback_unittest.py' -v
python -m unittest discover -s tests -p 'test_source_fidelity_profile.py' -v
python -m unittest discover -s tests -p 'test_*.py' -v
.\local\comfyui\image\venv\Scripts\python.exe -m unittest discover -s tests -p 'test_fid1*unittest.py' -v
python -m compileall -q scripts tests
git diff --check
python scripts/sync_repo_media.py --check
python scripts/launch_readiness.py --project all
```

普通python若无Torch，不给该环境的全量数值测试PASS；沿用本机已验证可运行完整suite的CPU环境或Comfy venv，记录解释器实际路径/版本。另用现有no-Torch subprocess测试显式阻断torch导入，完成schema4 prepare/dry-run、前驱和review-page入口；不通过全量suite的skip来代替数学验证。严禁默认在普通Python安装GPU包或改Comfy环境。

`launch_readiness`出现已有正式输入缺口是事实，不为把它变绿修改批准表。保留工具原exit语义，逐项解释，不能吞掉异常。

CI此前full=306、Comfy=68是基线，不是下一版预报。最终实际数量按日志统计，列新增测试名和skip原因，不硬凑数量。已有Windows三个权限skip逐项保留；新增关键测试不能因环境缺失悄悄skip。

### D. 新审片session，旧take09不重跑

现有可显示页面为：

`local/production/T1_SOURCE_PILOT/review_sessions/SH903_take09_20261013_01/review.html`

修复后创建新的unused session（例名仅在不存在时使用）：

```powershell
$J903 = 'local/production/T1_SOURCE_PILOT/video/SH903/jobs/take09'
$Session = 'local/production/T1_SOURCE_PILOT/review_sessions/SH903_take09_transaction_review_01'
if (Test-Path $Session) { throw 'Review session already exists' }
python scripts/fid1_qa_report.py review-page --root . --job-dir $J903 --out $Session
if ($LASTEXITCODE -ne 0) { throw 'review-page failed' }
Start-Process (Join-Path (Resolve-Path $Session) 'review.html')
```

页面打开/播放检查仅验证界面。可以使用本机现有浏览器测试能力；不装新浏览器平台，不启动新的生成runner。验证七图和实际视频正常加载，实际1/25/49帧标记正确；ended后选择、reviewer、quote仍空；默认导出拒绝。保存browser evidence及页面receipt，不填写真实页面来制造接受。合成正/负导出只在临时测试页面做。

此时人工反馈若仍缺失，结束独立工程部分并交付实现SHA/CI/审片页，状态 `ENGINEERING_READY_WAITING_HUMAN`。不是等待人而停止修复，也不是因为等待人就自动开始下一镜。

### E. 仅在收到Jovi真实反馈后记录

将用户真实导出的原始JSON原样放进 `local/review_evidence/`；不得拿template或fixture替代。如下文件名是operator选定路径，必须先确实存在：

```powershell
$Feedback = 'local/review_evidence/FID1_SH903_TAKE09_FEEDBACK.json'
if (-not (Test-Path $Feedback)) { throw 'No actual Jovi export; gate remains PENDING' }
python scripts/fid1_qa_report.py record-review --root . --job-dir $J903 --feedback $Feedback
```

preview应显示实际反馈/QA快照hash和具体decision。人工核对preview与收到的反馈完全一致后，使用本阶段已实现且测试的可选pin参数apply；以下参数不是d76现有接口，不在修复前运行：

```powershell
# $FeedbackSha / $QaSha 使用上一条preview输出的值，不在apply前重新计算并冒充已审阅pin。
python scripts/fid1_qa_report.py record-review --root . --job-dir $J903 --feedback $Feedback --expected-feedback-sha256 $FeedbackSha --expected-qa-sha256 $QaSha --apply
```

CHANGES_REQUIRED也是有效真实反馈，必须记录后保持下游关闭。PENDING不强行转换成拒绝或接受。若需修订一个已记录的决定，停止并保留原证据；本阶段不提供静默覆盖/撤销接口。

### F. 下游条件运行合同：现在禁止执行

开始任何真实SH901/902 GPU前，必须同时满足：R1–R4关闭、固定实现SHA复审/CI通过、实际前驱完整接受、当前镜头试拍执行权限确认、队列/模型/资源/部署检查全部通过。本文件本身不解除用户的“no downstream GPU”限制。

已存在且应保留的候选：

| Shot | Profile | 输入SHA256 | Seed |
|---|---|---|---|
| SH901 | `config/source_fidelity_trials/SH901_FID1_V002.json` | `09da40f244a0e3867627a3d6d6ba1a5d7b4c91110a3ec615fcd0234b35d85db5` | 2026100801 |
| SH902 | `config/source_fidelity_trials/SH902_FID1_V002.json` | `3629ba824aa49640f0f72c7d47b3eb0dddf16b3a9357d2a62c04573efa90e0ad` | 2026100802 |

SH901保留V001的两个ROI：(.31,.20,.53,.41)、(.60,.25,.84,.45)；SH902：(.10,.04,.48,.29)、(.40,.48,.73,.70)；V002均feather4。核对各自source实际布局，不借用SH903坐标。几何候选不是视觉接受。

获得全部门禁后，operator显式选未使用take，不能自动寻找一个“最新成功”前驱。例：

```powershell
$J901 = 'local/production/T1_SOURCE_PILOT/video/SH901/jobs/take02'
if (Test-Path $J901) { throw 'Old take must not be overwritten; explicitly choose a new unused take' }
python scripts/source_pilot.py prepare --root . --shot SH901 --seed 2026100801 --out $J901 --trial-profile config/source_fidelity_trials/SH901_FID1_V002.json --previous-job $J903
if ($LASTEXITCODE -ne 0) { throw 'SH901 prepare refused' }
python scripts/submit_prepared.py --root . --job-dir $J901 --url http://127.0.0.1:8188
```

没有 `--execute` 的submit必须无网络/无POST且不创建intent。真实execute只能另行确认权限后，使用同一个job追加 `--comfy-root local/comfyui/image/ComfyUI --execute` 一次。不得直接运行preview打印的底层probe绕过门禁。

SH901输出完成后做 `fid1_qa_report.py create --root . --job-dir $J901`、新review-page、真实完整播放与反馈；接受前停止。只有其真实接受且SH902执行权限成立后：

```powershell
$J902 = 'local/production/T1_SOURCE_PILOT/video/SH902/jobs/take02'
if (Test-Path $J902) { throw 'Old take must not be overwritten' }
python scripts/source_pilot.py prepare --root . --shot SH902 --seed 2026100802 --out $J902 --trial-profile config/source_fidelity_trials/SH902_FID1_V002.json --previous-job $J901
if ($LASTEXITCODE -ne 0) { throw 'SH902 prepare refused' }
python scripts/submit_prepared.py --root . --job-dir $J902 --url http://127.0.0.1:8188
```

任何timeout/unknown history/已有intent：保留job、prompt_id、record，先查现有Comfy history；不能再次POST、删除intent或把同任务换目录重试。失败take有失败结论且新的尝试被明确授权时才使用新take。

## 7. 测试矩阵及通过定义

| 编号 | 必测路径 | 通过定义 |
|---|---|---|
| T01 | 同字节两个反馈写入者，失败者open(xb)冲突 | 胜者证据/QA/锁保留；失败者不回报成功 |
| T02 | 不同反馈竞争、重复相同反馈、QA写失败 | 最多一个记录；不得覆盖既有记录；清理只涉及自身 |
| T03 | feedback校验后换字节 | 原快照被一致保存或明确拒绝；绝不QA A/证据B |
| T04 | QA首次读取后被修改 | 原比较hash仍有效，拒绝丢更新 |
| T05 | preview后反馈/QA漂移并带旧pin apply | exit2/no approval change；不自动更新pin |
| T06 | 崩溃注入：创建证据后、QA发布前、发布后 | 明确成功或恢复状态，无虚假OPEN；无误删 |
| T07 | 普通及Windows reparse/junction路径、跨shot/非法take | 创建/写入/POST前拒绝；同根链接别名也拒绝 |
| T08 | 完成的schema1 SH903 historical review | 不要求旧实现==新实现；无重跑或重封 |
| T09 | 标准SH901/SH902 schema2 prepare→dry-run（合成前驱） | 正确八文件receipt、MODEL/LATENT链、零POST |
| T10 | take04失败、take08失败、take09 PENDING、错顺序 | 全部拒绝，无下游job/intent；真实workspace只做拒绝正当性验证 |
| T11 | 前驱八文件逐一改变/receipt重封/lock或runtime期间改变 | 现有负路径保持通过，无probe调用 |
| T12 | profile/source/依赖/源审批漂移、孤立/错连anchor | 旧guard不减弱；准备期间变化不能发布 |
| T13 | 无Torch subprocess运行准备/前驱/页面/dry-run | 真正禁止torch导入仍可离线运行，不是skip |
| T14 | Comfy venv真实CPU运算 | 首格保留、未来ROI、非ROI可采样、13格/48通道、alpha一次、NaN/Inf等仍通过 |
| T15 | 首中尾索引映射 | 实际1/25/49及0/1/2秒，不是显示列表序号 |
| T16 | 新session图/视频/引用hash，旧take09全部保护hash | 新衍生图正确；旧QA/run/job/MP4没有重写 |
| T17 | 页面默认空、ended无批准、客户端导出与服务端schema一致 | 合成正/负例有效；实际人类字段保持空 |
| T18 | 默认非FID1/V5、原30镜、原媒体同步幂等 | 历史回归保留，未扩大正式批准 |

优先补实际record-review的集成测试，避免只对提取的新函数做断言。新增测试按实际行为细分，不能靠一个常量断言把整行T01–T18标完成。所有模拟运行/用户反馈清楚写SYNTHETIC并使用TemporaryDirectory。

## 8. 部署、资源与精确回退

本阶段核心节点无预期修改：先验证，不因脚本版本改变就卸载重装Comfy。现有入口：

```powershell
python scripts/fid1_deploy.py verify --root . --comfy-root local/comfyui/image/ComfyUI
```

实现触及了不应改变的节点bytes时先停止审查；不要通过更新deployment receipt蒙混过关。部署幂等/冲突/回退测试在临时Comfy根执行。若未来经批准需要部署原工具包，既有 `deploy` 和 `rollback` 命令必须匹配实际节点hash/所有权；rollback只移除该工具拥有的精确插件，不会神奇恢复旧算法/旧workflow/模型。

```powershell
# 仅在需要撤销工具所拥有的精确插件且已确认无任务运行时使用；不是本阶段默认操作。
python scripts/fid1_deploy.py rollback --root . --comfy-root local/comfyui/image/ComfyUI
```

代码回退保留Git历史：为本地实现提交做明确revert或安全检出固定旧版本到独立目录核验，不reset/clean/force-push，不删除旧jobs/证据。依赖变化导致尚未执行的prepared job作废，另准备新take；不能通过改job_integrity让它适应回退。

资源限定：take09曾采样峰值11808MiB、最低可用物理RAM10821632字节；这些不是安全余量保证。后续GPU前重新记录GPU总/已用/可用、RAM和pagefile、Comfy版本、模型文件、queue、node hash；低内存/资源未知先停止，不在接近耗尽状态自动试拍。沿用本机现有监测，不并发、放大尺寸、加帧或下新模型。采样峰值和连续硬件峰值分开描述。

## 9. CI、完整diff复审及固定实现SHA

本地实现方在唯一分支一次完成：复现→修复→相关套件→全量→自审整个diff→处理问题→再测→提交显式路径→push→读取最终HEAD关联四项Actions及full日志。CI失败则定位日志修复，同阶段继续，不把中间提交或waiting当交付。

- 不使用旧d76绿灯来证明新代码。
- 每个run记录head_sha、checkout_sha、run_id、job_id、conclusion；PR测试merge ref不等于main已经合并。
- 原workflow保留；如确需改覆盖，说明原因并证明原suite仍执行。CPU Torch必须真实安装/导入，不能静默跳过；Node客户端测试不能因Node缺失在CI悄悄skip。
- final diff应无源图、旧take、批准、节点算法、非本项目文件或tasks私记。仅允许本阶段必要代码/测试/文档。
- 自审与网页独立复审分开记录；不能将本计划作者的隔离复现或旧local review当新版本复审通过。
- 网页最终审查的对象是本地返回的完整40位实现SHA，不是本文档SHA。

## 10. QA与最终交接验收

### 工程交付（无需等待人）

R1–R4每项有修改路径、红转绿测试、真实输出证据；全量及CPU套件通过；新session可用；原take09仍PENDING；四项新CI通过；无下游GPU/新模型/正式批准变化。交付状态 `ENGINEERING_READY_WAITING_HUMAN` 合法且完整，不能写VISUAL_ACCEPTED或PRODUCTION_READY。

### 条件性source验收（只有以后取得权限才发生）

每个实际take需：input/profile/workflow/node/dependency/predecessor receipt、prompt history、run_record、MP4 SHA/bytes、ffprobe原始JSON、完整decode exit/stderr、1/25/49+all49及映射、资源采样、Jovi真实反馈原始字节与应用结果。运行成功和视觉接受分别记。SH902即使通过，也不授予原LOOKREEL/EP001的正式30镜批准。

### 本地返回格式

```text
[C2C]
STATE: EXECUTED
TASK_ID: c2c_f2a1
ITERATION: <真实下一迭代>
PLAN_SHA: <本文档提交>
BASE: d76a75b86c30c71e1f502afc6354734210317779
IMPLEMENTATION_HEAD: <最终40位SHA>
PR: 12 open/unmerged
FINDINGS: R1=... R2=... R3=... R4=...（每项链接到测试/证据）
TESTS: <collected/pass/skip/fail及解释器、命令、完整日志路径>
CI: <最终head及checkout/run/job/conclusion>
PROTECTED_HASHES: <保护清单与前后对比>
TAKE09: <实际输出hash；真实人工状态>
DOWNSTREAM_GPU: NOT_RUN（或仅在另行授权且真实发生时逐条列出）
REVIEW_PAGE: <新的实际session路径>
REMAINING_GATES: <人类反馈/独立复审等，不伪造结果>
```

必须判CHANGES_REQUIRED的条件：R1/R2仍有误删或不一致落盘；错误路径能进入新FID1任务；真实帧号继续误标；旧history被重封；用fixture代替Jovi；未真实收集/执行测试；跳过前驱或依赖guard；PENDING时发下游GPU；CI指向旧head；把文档提交、运行成功或contact-sheet改善冒充最终视觉通过。

## 11. 当前交付解释

本轮完成的是：真实工具核对、d76代码/证据审核、三个隔离竞态复现，以及包含所有处置/命令/测试/门禁的完整计划文档。没有修复业务代码、修改PR元数据、运行本地GPU或记录用户接受。文档所在SHA作为计划接收点；d76继续是被审核实现基线。R1–R4要到本地执行并回传新固定SHA后才能关闭。
