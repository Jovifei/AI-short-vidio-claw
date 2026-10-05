# 19 当前有效视觉规格

状态：ACTIVE
用途：所有 Production keyframe / video / QA

## 1. Identity Source of Truth

人物是否正确，以用户批准的视觉 reference 为第一依据。

优先级：
1. 用户批准的 reference images
2. 用户批准的 golden keyframes
3. Character Bible 文字特征
4. prompt 风格词

文字描述不能替代视觉 reference。

## 2. 林黛玉

要求：
- 保持用户认可的古典荧幕参考脸感；
- 不现代网红化；
- 不尖 V 下巴；
- 脸偏圆润鹅蛋；
- 下巴自然、小而不锐；
- 眼眉含蓄古典；
- 鼻口小巧；
- 古典发式；
- 表情范围要丰富，不能每张固定低头或歪头。

Hard Reject：
- 尖下巴
- 现代女团妆
- 通用 AI 少女脸
- 夸张现代双眼皮审美
- 现代直发 + 现代服装

## 3. 孙悟空

要求：
- 必须保持用户认可的经典齐天大圣猴脸结构；
- 眉骨、眼窝、鼻口/吻部、耳形和面颊毛区稳定；
- 毛色与批准 reference 保持一致；
- 表情可以温柔，但不能因此变成普通男性脸加毛。

Hard Reject：
- 普通男性五官 + 毛发
- 欧美猿人电影脸
- 狐狸/狮子脸
- 耳形/吻部/眉骨每镜随机变化
- 为恋爱感把猴脸明显人脸化

## 4. 服装

当前 Production 人物不穿现代衣服。

即使场景是公交、厨房、公寓、街道、阳台，人物仍保持批准的古装视觉。

DAIYU：
- 淡雅多层古装；
- 月白/淡蓝/淡紫/浅粉灰；
- 居家时可以简化为古典内衫/罩衣，但不是 T 恤、毛衣、现代睡衣。

WUKONG：
- 齐天大圣经典古装视觉；
- 黄/金棕主色；
- 护腕/腰带/兽纹等批准后固定；
- 居家可减少重装，但不能 hoodie、运动夹克、牛仔裤、运动鞋。

## 5. 场景

场景可以现代，人物衣服不能现代。

这种“经典人物认真过今天的生活”本身就是系列反差。

## 6. CP 感

要覆盖：
并肩、依偎、偷看、互相照顾、打闹、递东西、保护、靠肩、轻触、少量亲密镜头、同框各做各的。

生活感来自“他们已经很熟”，不是每张都接吻。

## 7. Keyframe QA

权重：
- DAIYU identity 25
- WUKONG identity 25
- costume 15
- couple chemistry 15
- anatomy/contact 10
- composition 5
- lighting/style 5

Hard Gate：
- 任一主角 identity < 4/5 → REJECT
- 出现现代服装 → REJECT
- WUKONG 明显人脸化 → REJECT
- DAIYU 明显现代化 → REJECT
- 关键肢体错误 → REJECT

## 8. Reference 存储

大图本机：
local/references/active_visual_target/

Git 只存 manifest/hash：
assets/characters/*/reference_manifest.yaml
assets/style/ACTIVE_VISUAL_TARGET.yaml
