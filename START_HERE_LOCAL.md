# 本地执行先读此页

## 现在可以做什么

接收素材、离线检查、查看本机ComfyUI环境。**不能把仓库有计划当作当前可批量开拍。** 新增单图OA001已经返回并取到实际文件，但中心有OpenArt大水印，未进入生产参考。

## 唯一详细操作入口

[本地开拍执行书](docs/preproduction/LOCAL_SHOOTING_RUNBOOK.md)：代码/媒体接收 → 全镜输入检查 → 具体批准 → 本地环境探活 → 49帧T1独立试拍 → 81帧生产参数验证 → 27秒Look Reel → 60秒EP001 → 声音与最终验收。

新增图像通道政策：`config/image_channel_policy.json`。默认ChatGPT Images，第三方不自动扣积分；视频仍是本机Wan2.2-TI2V-5B。

```powershell
python scripts/launch_readiness.py --project all
```

报告区分 `t1_input_threshold_met`、`whole_project_inputs_ready` 和未验证的本机运行；静态镜头同样检查。只有缺口真的补齐才推进，不让本地Agent猜脸或替远端补尚未交付的图。

测试：`python -m unittest discover -s tests -p "test_launch_readiness.py" -v`。

实际进度及责任：`tasks/shooting_handoff_status.json`。本页不是自动生产批准。
