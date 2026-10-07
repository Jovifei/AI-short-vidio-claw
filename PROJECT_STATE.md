# PROJECT_STATE

更新：2026-10-07。**实体素材FIX2已打包并验证；完整远端创作交付未完成；生产未就绪。**

## 当前接收入口

使用 `docs/preproduction/DELIVERY_FIX2_20261007.md` 和 `tasks/media_delivery_fix2.json`。

实际包名：`AI_short_drama_MEDIA_HANDOFF_FIX2.zip`。大小65,965,628 bytes；SHA256 `e7c90d0d5885445eb650cfefdeb1512cfc316a706b896dbf0cdad3ffe5189f6a`。

这是对话附件，不是GitHub Release。git pull只拿脚本/清单，不会把PNG传到E盘。旧PR7包名/hash不能拿来验证这个FIX2包；使用 `receive_delivery_fix2.py`，不要混用旧接收脚本。

## 这次实际补交

- 原V5 17项原件，hash与既有registry完全一致。
- 10张古装构图来源，独立编号，与REFBATCH02分开。
- 1张手部上下文、4张带父图与裁框的局部选项。
- 共32个真实PNG和32个不同内容hash；不是32张新生成图片，不是30镜完成图。
- 32项本地审片页，明确默认未审核；27秒/24fps/648帧来源静态审片，标注非正式产品。
- 实体导入、重复导入和hash核查均成功；原registry及两份30镜批准表保持不变。
- 本轮78项离线回归通过（53既有V5+25本轮）。用户Windows/ComfyUI/GPU未在本轮测试。

## 未完成事项不转嫁

EP00120张精确剧情关键帧仍未交付；LOOKREEL10张来源与计划仍有差异；独立HOME/雨天/受伤等状态图仍不完整。本轮出图尝试未达到独立镜头规格，未计入完成量。

这些事项仍是REMOTE_PREPARATION。不能再把“还没产出图”表述成“只差用户批准”，也不能交给本地Codex假装只剩GPU。

## 当前Gate

具体参考与30镜批准未自动提升。两个V5计划仍contract_ok=true、ready=[]、production_ready=false。

本地此时可以接收素材、审核实际图、检查合同；不能据此批量提交正式I2V。

## 既定路线与历史证据

V2产品路线、V3创作知识、V5执行合同全部保留；不换Wan2.2-TI2V-5B、不加14B、不重跑地铁T2V。三张合适的获批关键帧可以局部T1；完整Look Reel仍逐镜验收。

历史4070S/约32GB RAM/T2V十次成功/一次未批准I2V仅为Lab依据，不代表本轮画质或用户本机已验收。
