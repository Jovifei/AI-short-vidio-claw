# 29 人物模型审核状态

日期：2026-10-05
状态：PREPROD_MODEL_DIRECTION_APPROVED / FINAL_GOLDEN_PENDING

## 用户最新反馈

用户表示：
“感觉可以，继续用建模的人物制作短剧所需的所有不在本地执行的工作。”

项目解释：

这已经足够允许：
- 继续剧本
- 继续分镜
- 继续角色/服装 Stage
- 继续 Prompt
- 继续场景/声音/后期规划
- 继续 LOOKREEL/EP001 Preproduction

但还不自动等于：
FINAL_GOLDEN_MODEL_APPROVED。

原因：
最终本地生产需要可验证的：
- 文件
- Hash
- Reference Manifest
- Contact Sheet
- 最终锁定状态

## 当前建模方向

### 林黛玉
采用当前建模图方向：
- 柔和圆润鹅蛋脸
- 非尖 V 下巴
- 含蓄眼眉
- 古典发髻
- 花/玉/珠类轻饰
- 月白/淡紫/淡青服装

Canonical：
assets/characters/daiyu/canonical_visual.yaml

### 孙悟空
采用当前建模图方向：
- 金棕猴脸
- 明确眉骨/吻部/耳形
- 斗战胜佛佛冠/冠饰
- 佛珠
- 红金正式造型 + 黄灰金日常造型

Canonical：
assets/characters/wukong/canonical_visual.yaml

## 服装

孙悟空：
- DZS_FORMAL
- DZS_DAILY
- DZS_HOME

林黛玉：
- CANONICAL_LAVENDER
- CANONICAL_HOME
- RAIN

## Final Golden Gate

只有用户明确说：
“锁定这个人物/就用这版作为最终人物”

并且本地有 Hash 后：

golden_model_status: APPROVED

## 当前允许的下一步

继续 Preproduction：
已完成 docs/30–50。

本地下一步：
把人物 reference 落盘并做 Final Golden Review。
