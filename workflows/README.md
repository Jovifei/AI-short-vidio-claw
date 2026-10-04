# workflows

只保存经过测试、可复现的生产 workflow。

目录：
- image/
- video/
- lipsync/
- post/

每个 workflow 必须配同名 metadata yaml 或写在 manifest 中：
- workflow_id
- version
- expected ComfyUI commit
- required custom nodes
- required models
- input contract
- output contract
- benchmark
- known issues

Production 与 Lab workflow 不混用。

当前预期首批：
- IMG_identity_human_v001
- IMG_keyframe_dual_v001
- VID_wan22_native_i2v_v001
- VID_wan22_lowvram_v001
- VID_framepack_long_v001
- LIP_musetalk_v001
