# 仓库中的真实图片

32个PNG原件，不是下载链接。用户要求直接提交图片，因此本批明确进入Git。模型权重和大成片仍不入Git；公开/商用素材权利没有自动核验。

- `MODEL_*.png`：3张二维设定板，不是三维模型或LoRA。
- `REFB02_01..10.png`：10张已有生成样图。
- `DAIYU_FACE_CROP`、`WUKONG_FACE_CROP`及两张`COSTUME_CROP`：原4裁片。
- `LOOK_SOURCE_COMP*.png`：9张旧构图来源；另一个花束来源在REFB02_09，但遮脸，不能自动满足当前COMP09。
- `T1_*_COSTUME.png`：6个确定性服装ROI，不是独立定妆。

[草坡源图](source_library/REFB02_02.png) · [石阶源图](source_library/REFB02_06.png) · [山水源图](source_library/REFB02_01.png)

路径/hash见`git_media_manifest.json`。本地 `python scripts/sync_repo_media.py --apply` 即可恢复旧registry要求的local位置；不再下载ZIP或登录OpenArt。

这解决“已有图没到本机”。仍未生成的EP00120镜不在此库中；0/30批准不能因文件收到而提升。

[完整交接](../../docs/preproduction/GIT_MEDIA_HANDOFF.md)
