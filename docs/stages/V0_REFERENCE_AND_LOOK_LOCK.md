# V0 — 人物 Reference 与视觉目标锁定

## 目标
任何 Production 视频之前，先锁定两位角色的外观。V0 完成前，不生成故事视频。

## 输入
用户批准：
- 林黛玉脸部参考 3–8 张
- 林黛玉服装参考 2–5 张
- 孙悟空脸部参考 3–8 张
- 孙悟空服装参考 2–5 张
- 10 张情侣构图参考

如果本地 Codex 无法访问聊天图片，请用户把文件放到 local/references/inbox/。

## Step 1：本地归档
local/references/active_visual_target/
- daiyu/face/
- daiyu/costume/
- wukong/face/
- wukong/costume/
- composition/lookreel01/

这些原图不提交 Git。

## Step 2：建立 manifest
创建：
- assets/characters/daiyu/reference_manifest.yaml
- assets/characters/wukong/reference_manifest.yaml

每张记录：
ref_id、local_relative_path、sha256、type、angle、notes、approved_by_user、approved_at。

## Step 3：Golden Face Set
DAIYU 至少：正面、左右 3/4、自然笑、中性。
WUKONG 至少：正面、左右 3/4、中性、温和表情。

## Step 4：Golden Costume Set
至少锁：
- DAIYU_CLASSIC_OUTDOOR
- DAIYU_CLASSIC_HOME
- WUKONG_CLASSIC_OUTDOOR
- WUKONG_CLASSIC_HOME

HOME 只能古装轻量化，不能现代化。

## Step 5：Contact Sheet
把批准参考排成联系表给用户确认：
- 人物是否正确
- 服装方向是否正确
- 哪些图应淘汰

没有明确批准，状态保持 DRAFT。

## PASS
- 两个角色均有 Golden Face Set
- 两个角色均有 Golden Costume Set
- 10 张 composition refs 编号完成
- 用户明确批准
- manifest 有 hash

状态：VISUAL_TARGET_LOCKED

通过后才进入 K1。
