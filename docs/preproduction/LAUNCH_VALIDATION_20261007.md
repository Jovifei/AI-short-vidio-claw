# 本地启动方案验证记录｜2026-10-07

## 范围

本记录是助手CPU容器的真实离线验证与一个已完成供应商预览的取回，不是用户Windows、ComfyUI或4070S验收。未执行新的图像生成任务、未购买积分、未修改原30镜批准表。

## 实测

- Python3.13.5，Pillow12.3.0。
- `test_preproduction_v5.py` 53项通过。
- `test_launch_readiness.py` 31项通过。
- 合计84项选定离线回归通过；不声称本轮重跑了所有历史恢复工具测试。
- 四个新/改动Python脚本通过py_compile。
- 用实际V5计划与原17项已挂载素材执行launch_readiness：两集contract_ok=true；无丢失/变化的原17项参考；LOOKREEL01有效获批输入0/10，EP001为0/20，whole_project_inputs_ready均false。

## 回归覆盖

1. I2V三镜齐但静帧未齐：只允许报告局部试拍输入，不能整集ready。
2. 静态镜头图片不存在、伪PNG、过小缩略图、横板、错误衣服stage、引用/hash/证据不匹配：拦截。
3. 单人镜頭只要求实际出场角色，不虚构另一个人物。
4. 只读报告不改文件、不联网、不写批准；可选择用退出码拦截下一步。
5. T1副本只改试验长度和输出前缀；原计划/批准表不变；T1_ONLY不能自动进正式剪辑。
6. 未批准输入、静态镜头、非法帧数、重复任务目录：拒绝prepare。
7. 供应商预览只读获取默认不联网；按真实字节解码格式，不把provider的PNG标签当事实。

## OA001实物

GitHub Actions run37642626667成功取回已完成的旧任务，artifact11493008203保存到2026-11-06。下载artifact后实际打开WEBP：768×1376，70,472bytes，hash `0607e4f1cb05757f135415995961d0caecfd702a29fb62da3a1a2b34f5791349`。中央有明显OpenArt水印；不作为生产或训练输入，不做去水印。

## 未测

用户本机文件是否接收、当前端口、驱动、RAM/VRAM峰值、49/81帧获批人物I2V、声音和成片。不能由这84项测试推导开拍通过。

完整执行书：LOCAL_SHOOTING_RUNBOOK.md。结果机器台账：tasks/shooting_handoff_status.json。
