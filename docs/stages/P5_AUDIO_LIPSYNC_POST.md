# P5 音频、口型与后期执行报告

## 目标

在视频生产已经稳定后，再增加声音和对白口型。

## P5A TTS

主候选：GPT-SoVITS。

上游 api_v2：
- bind 默认 127.0.0.1
- port 默认 9880

任务：
- voice_map
- 授权声音
- text normalization
- emotion/speed
- per-line wav
- cache

Gate：
同角色跨句/跨集声线一致，无错字。

## P5B LipSync

主候选：MuseTalk 1.5。

上游 app.py：
- Gradio 默认 7860

注意：
Gradio UI 不等同于稳定 production REST API。
本项目需：
- 明确调用方式
- 或写 adapter/CLI wrapper

第一阶段只测林黛玉标准人脸。

悟空：
单独专项，不承诺 MuseTalk 有效。

## P5C 后期

确定：
- source fps
- final fps
- 是否需要插帧
- upscale
- subtitle
- loudnorm
- codec

必须先 A/B：
“直接编码”与“插帧/放大”是否值得时间和质量成本。

## GPU 调度

video model unload
→ verify GPU memory
→ TTS/lipsync
→ unload
→ post

避免 32GB RAM 内长期堆积多个模型。

## Gate

accepted clips + audio 一条命令可输出 final。
