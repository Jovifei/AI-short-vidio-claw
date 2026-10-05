# V5｜从“写了门禁”到可验证合同

审核基线：`f3d9d3b59525efff372f3d60d3982ff2b09a545b`。下面区分仓库事实、本轮修复与尚未验证事项。

## 1. 发现的问题及处理

| 原问题（源文件） | 后果 | 本轮措施 | 验证方式 |
|---|---|---|---|
| `production_guard.py` 无条件循环DAIYU和WUKONG | EP001_SH001明明只拍悟空也必须编一个黛玉ref | 读取执行计划中的出场名单，逐个检查实际出场角色 | 单人、双人分别测试 |
| `build_render_queue.py` 不校验M0/M3，只按状态与同名文件搜索 | 静帧/高风险镜头也可能排进I2V；同名candidate与approved冲突 | 按render_mode+tier过滤，精确相对路径，不使用rglob找同名资产 | 静帧排除、hash变化测试 |
| `approve_asset.py` 参数可省略refs后直接写USER_APPROVED | 批准记录可能缺人物/服装关联 | 先构建临时记录并完整校验，再原子写入 | 缺bindings失败且原对象不改 |
| 旧门禁只查LoadImage接到某个latent | latent可能没有进入最终保存视频的实际链路 | 检查source→latent→sampler→decode→create→save完整链 | 断链、错误输出槽、未使用输入、未知节点测试 |
| 参考ID只是非空字符串 | 虚构ID也可能过 | 查registry、角色、role、stage、批准证据、真实文件hash | 假ID、换文件、错角色/服装测试 |
| 只记录approved_by_user=true | 无法知道批准的是哪张图 | 证据绑定subject_id、图hash、scope、实际反馈来源、时区时间戳 | 通用风格反馈、错hash、无时区拒绝 |
| 旧计划常把49帧描述成3–5秒 | 成片缺时长或被无声减速 | 精确帧级计划；动态源必须覆盖剪辑帧数 | 49帧不足72帧剪辑时拒绝 |
| 旧路径说明存在project/shot与project/approved两种结构 | Agent可能把候选当批准图 | V5只从`local/production/<PROJECT>/approved/`读取关键帧 | candidate路径即使同hash也不作为生产输入 |
| 只有手动先跑guard的约定 | 之后修改图/提示词可脱离原批准 | prepare冻结image、workflow、输入文件hash；submit前再验 | 任务目录不可覆盖、文件修改使任务失效 |

## 2. 不夸大“门禁”的能力

这是一套可追溯的工程合同，不是能识别真人批准身份的认证系统。人可以手工编辑JSON，低层ComfyUI也能被手工调用；没有把整个电脑锁住。不能因为提供了`--user-confirmed YES`就断言真人已经确认。

规范执行入口是 `preproduction.py / submit_prepared.py`。实际用户反馈必须如实抄录，禁止Agent虚构。新的`approval_evidence`结构用于发现误绑定和无意越级，不是防恶意伪造的数字签名。

## 3. 不重复改写已有视频引擎

保留仓库已有`VID_wan22_5b_i2v_prod_v001.json`和`p1_comfy_probe.py`。本轮没有换节点、换采样器、自动下载模型、增加第二个ComfyUI。

本轮新增的离线prepare只做参数装配和输入冻结。它不POST；`submit_prepared.py`默认也只打印命令，明确`--execute`才调现有probe。本次远端没有执行该开关。

官方ComfyUI说明5B同时支持文生/图生；要做图生需要启用LoadImage。仓库过去T2V成功不等于角色I2V成功。来源见 `SOURCES_AND_LIMITS_V5.md`。

## 4. 失败与恢复状态

`PREPARED_NOT_SUBMITTED` → 写`submission_intent.json` → 调probe → 写`run_record.json`与`submission_result.json`。

提交意图已经存在但run_record缺失时，状态是“需要查history”，不是“肯定没提交”。不要删文件后立即重试。先找到prompt_id、现有队列、输出与日志；无法确定时保持阻塞。不同seed或批准图更新后创建新任务目录，不覆盖旧take。

共享`.gpu_submission.lock`只串行化本项目支持的提交入口；其他UI或外部程序不受此锁控制，仍需probe的队列检查。程序异常退出留下锁时，先核对对应进程和ComfyUI队列，再人工清理。

## 5. CPU测试和GPU验证分开

已运行53项离线回归，覆盖数据合同、批准边界、路径、hash、live graph、单/双人、静态过滤和任务冻结。

仍待本机：ComfyUI模型加载、I2V画面稳定、VRAM/RAM峰值、上传/输出兼容、异常服务恢复。单元测试没有验证这些，不把`53 passed`写成“生产片已验收”。

## 6. 尚需后续处理但不阻碍继续前期工作的事项

- HOME服装参考需要具体资产批准，当前OUTDOOR裁片不能自动替代。
- 裁片分辨率较低，正式训练数据仍需清晰无字近景。
- 新工具严格使用v5 JSON，旧approval_manifest不会自动迁移成批准；当前旧文件没有需要保留的已批准镜头。
- 旧日期的环境端口与RAM统计只作历史证据，本机下次运行前重新确认。
- 历史probe里Windows内存API带pagefile名字的字段不能直接当作物理页面文件大小；资源统计需结合API含义和系统实测解释。
