# benchmarks

所有技术路线必须在目标机器 RTX 4070 Super 12GB 上留下实测结果。

推荐文件：
- P1_ENVIRONMENT.md
- P1_4070S_BASELINE.md
- P2_DAIYU_IDENTITY.md
- P2_WUKONG_IDENTITY.md
- P2_DUAL_CHARACTER.md
- P5_LIPSYNC.md

每份 benchmark 至少写：
- 日期
- GPU/VRAM/RAM
- driver/CUDA/PyTorch
- ComfyUI commit
- workflow id/hash
- model id/hash
- resolution
- frames/fps
- seed
- peak VRAM
- elapsed time
- success/failure
- identity score
- motion score
- notes

不要只写“效果不错”。
