# PROJECT_STATE

更新：2026-10-07。

**本地执行书与输入检查已补齐；OA001实图已取回审核但有大水印；完整远端图片制作未完成，不能宣布批量开拍。**

## 当前入口

`START_HERE_LOCAL.md` → `docs/preproduction/LOCAL_SHOOTING_RUNBOOK.md`。

状态台账：`tasks/shooting_handoff_status.json`。

## 本轮实际完成

- 实际取回OpenArt已完成的OA001：WEBP 768×1376，70,472 bytes，SHA256 `0607e4f1cb05757f135415995961d0caecfd702a29fb62da3a1a2b34f5791349`。
- 确认是单幅完整站姿，但中央OpenArt水印覆盖腰部/前臂，且服装细节有变化；只存供应商审片，未当生产参考，未去水印，未授予批准。
- 默认静帧通道改回ChatGPT Images参考编辑。Nano Banana仅保留一次单图输出试验；本轮没有新增第三方生成、扣费或升级。
- 修正整集validator只检查I2V而可能漏掉STILL输入的缺口；新增只读launch_readiness逐镜解码、引用和hash检查。
- 新增独立T1试拍任务：33/49/81帧副本，不改27秒/60秒计划，不把49帧的2.0417秒试验冒充正式3秒镜头。
- 助手Python3.13.5/Pillow12.3.0：53项既有V5 +31项新回归，共84项选定离线测试通过。不是用户Windows/GPU测试。

## 当前真实输入状态

助手测试目录原17项来源文件存在且hash有效；不意味着用户E盘已收到。两集计划合同有效，但LOOKREEL01获批有效输入0/10、EP001为0/20。所有原审批表保持原样，未代签。

OA001 provider COMPLETED不等于人物定妆完成。42个独立生成请求也不等于42张图片。

## 仍由远端负责

独立无水印服装/状态图、LOOKREEL来源差异修复、EP00120张精确剧情关键帧，以及对应实图hash、bindings与审片尚未全部完成。不得把没产出的图称为“只等用户审批”，不得让本地Codex补图后声称只剩显卡工作。

## 本地当前可以做

安全接收代码和既有来源包、离线测试、只读检查ComfyUI实际端口/队列/模型/RAM/显存。

至少三张合适获批I2V输入有效后才启动局部T1；完整Look Reel仍需10/10图片输入，EP001需20/20。输入齐不等于本机T1、动态画质或最终成片验收通过。

## 路线不变

V2产品路线、V3创作知识、V5计划/批准/工作流全部保留。视频仍为单ComfyUI+Wan2.2-TI2V-5B、GPU串行；不升级14B，不训练LoRA作为首片前置。三句台词先画外音。

来源接收仍用`AI_short_drama_MEDIA_READY.zip`（26项既有来源，SHA256 `6259e103d41af94a3c984d6d47a62b65b70579ba7694bede2c338ad3ba3e6906`）和既有import_reference_bundle.py；不新建另一个恢复入口。git pull只取文本/脚本，不凭空恢复附件PNG。
