# 48 Reference Bundle 规范

状态：ACTIVE

## 1. 一个 Production Keyframe 的 Reference Bundle

必须最多包含：

### Identity
DAIYU：
1–3 张。

WUKONG：
1–3 张。

### Costume
每角色 1 张主参考。

### Composition
1 张。

总量尽量 5–7 张以内。

## 2. 为什么不能塞二十张 Reference

太多 reference 会带来：
- 人脸冲突
- 服装冲突
- 不同光线/年龄感冲突
- 模型不知道该跟谁

所以先从 Golden Reference 中选最匹配当前角度的少量图片。

## 3. 角度匹配

如果 shot 是：
左 3/4。

Identity bundle 优先：
- left 3/4
- front
而不是右 profile。

## 4. 全身镜头

增加：
- full-body costume ref

但脸仍保留：
- front/3Q identity ref。

## 5. 同框

人物顺序固定：
DAIYU refs
WUKONG refs
Costume refs
Composition ref

不要交叉随机排列。

## 6. Composition Ref

只学习：
- 人物位置
- 摄影机角度
- 景别
- 动态关系

不学习：
- 参考图人物的脸
- 参考图人物服装
- 品牌/文字

Prompt 明确：
composition only.

## 7. Reference Bundle Manifest

每个 shot 建议记录：

bundle_id
shot_id
daiyu_refs[]
wukong_refs[]
daiyu_costume_ref
wukong_costume_ref
composition_ref
bundle_hash
created_at

## 8. Bundle Hash

把 ref IDs + 各 sha256 排序后拼接再 Hash。

这样同一 shot 以后可以知道 reference bundle 是否改过。

## 9. Bundle Freeze

Keyframe USER_APPROVED 后：
bundle freeze。

若换 reference：
必须生成新 keyframe version。

## 10. Local Path

local/production/<PROJECT>/<SHOT>/records/reference_bundle.json

Git 可以提交不含原图的 bundle manifest。
