# V5 本轮验证报告

日期：2026-10-06。测试环境为本轮Linux容器，Python 3.13.5；不是用户Windows主机。

## 实际执行

- `python -m unittest discover -s tests -p "test_preproduction_v5.py" -v`：**53 tests，全部通过**。
- 核心脚本compileall：通过。
- EP001计划检查：20镜，1440帧，24fps，60.000秒；6个I2V候选。
- LOOKREEL01计划检查：10镜，648帧，24fps，27.000秒；4个I2V候选。
- 两个项目的批准表全为DRAFT，队列production_ready=false；没有误放行。
- 实际17项图像文件均存在；13张原图与4张裁片有hash/尺寸。索引没有将其自动批准。

## CPU参考审片

使用 `render_reference_review.py` 与本轮容器FFmpeg生成 `REFBATCH02_reference_review_v5.mp4`。

ffprobe实测：720×1280；24/1fps；480帧；20.000000秒。视频无对白，逐图2秒，永久标注REFERENCE REVIEW / NOT EP001 / CANDIDATE。**这不是图生视频测试，也不是EP001成片。**

## 测试覆盖摘要

单人/双人身份需求；错误/缺失/被替换的引用；批准scope/hash/时间戳；candidate目录冒充approved；M0/M3过滤；路径穿越；重复JSON键；非法源尺寸/帧数；时间线缺帧/超长；LoadImage未进入最终链路；保存链错误；14B/错VAE/未知节点；双人负向词错误；不可覆盖的任务快照；导入幂等与全包预检；批准失败不改原记录。

## 没有执行/没有验证

- 没有连接用户本机ComfyUI，没有提交任何GPU job。
- 没有验证新I2V的画质/峰值VRAM/RAM。
- 没有完成新关键帧批量生成、配音、口型或正式成片。
- 没有训练LoRA/生成三维网格。
- GitHub Actions结果以远端本次PR实际状态为准，不由本文件预先声称通过。

## 回归原则

fixtures在临时目录构造，只为测试合同，含TEST FIXTURE标识。不得把测试批准复制到真实registry。
