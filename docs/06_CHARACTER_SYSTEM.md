# 06 角色一致性与人物系统

## 1. 目标

“同一个角色”不是只锁脸，而是锁定一组可见事实：

- 头脸比例
- 眼型/眉形
- 鼻口比例
- 下颌
- 年龄观感
- 体型
- 发型
- 发饰
- 肤色/毛发
- 身高差
- 服装 stage
- 标志道具
- 表演习惯

## 2. 林黛玉：原创原著型视觉方向

项目使用的是“古典文学人物林黛玉的原创视觉设计”，而不是对任何一位现代演员的复制。

目标观感：
- 清秀、灵动、敏锐；
- 面部偏圆润鹅蛋，不做网红 V 脸和过尖下巴；
- 下颌线自然收窄，但有真实颏部体积；
- 眼睛偏细长、含蓄，单眼皮/内双视觉均可，但不做夸张欧式双眼皮；
- 眉细而有轻蹙感，不能画成强势现代平眉；
- 鼻梁与鼻头小巧、自然；
- 唇形小而薄厚适中；
- 表情不应长期“歪头忧郁”，她应有冷眼、含笑、专注、讥诮、好奇、倔强、放松等丰富状态；
- 体态纤细，但不是病弱摆拍；
- 发式可保留古典气质，进入现代生活场景时服装可做“古典元素 × 现实生活”混搭。

禁止漂移：
- 尖下巴；
- 明显网红妆；
- 大开扇双眼皮；
- 高饱和韩式妆感；
- 过度幼态娃娃脸；
- 每镜都低头/歪头；
- 直接复刻特定影视演员五官和服饰。

## 3. 孙悟空：原创人形猿猴视觉方向

固定：
- 暖金/棕金毛发；
- 人形体态；
- 清晰猿猴面部结构；
- 鼻口不是普通人类脸加毛；
- 耳朵、眉骨、毛发方向稳定；
- 四肢毛发和手掌比例稳定；
- 日常服装偏旧、实用、易活动；
- 性格外放、顽皮、警觉，但在黛玉面前常有克制的温柔。

禁止漂移：
- 下一镜突然普通人脸；
- 毛色大幅改变；
- 耳朵形状随机；
- 身高和体格显著变化；
- 直接复制特定影视版孙悟空妆造。

## 4. 角色 Reference Pack

每个主角至少准备：
- 正脸
- 左 3/4
- 右 3/4
- 侧脸
- 半身
- 全身
- 中性表情
- 笑
- 生气/不耐烦
- 当前主 stage 服装

建议形成 20–30 张“已确认且彼此一致”的图，再考虑训练角色 LoRA。

## 5. 技术路线

### 人类角色
阶段 A：
approved reference + PuLID / IPAdapter。

阶段 B：
角色视觉稳定后训练 LoRA。

阶段 C：
LoRA + reference conditioning + pose/depth 控制。

### 孙悟空
阶段 A：
reference conditioning + 统一提示词模板。

阶段 B：
优先训练角色 LoRA。

阶段 C：
LoRA + reference + mask/pose 组合。

不建议把 InsightFace 相似度当孙悟空唯一判据，因为其脸不是标准人脸分布。

## 6. Stage 机制

角色外观随剧情变化时不覆盖 base，而是新增 stage。

例：
DAIYU_BASE
DAIYU_HOME
DAIYU_RAIN
DAIYU_SLEEP
DAIYU_OUTDOOR

WUKONG_BASE
WUKONG_HOME
WUKONG_RAIN
WUKONG_INJURED
WUKONG_OUTDOOR

stage 只记录发生变化的可见项。未写的仍继承 base。

## 7. 连续性锁

每个镜头复制最小必要锁面，不把整份人物简介塞进提示词。

例：
DAIYU_LOCK_FACE：
rounded oval face, natural soft jawline, non-pointed chin, narrow almond eyes, subtle single/inner eyelid, fine slightly arched brows

WUKONG_LOCK_FACE：
warm golden-brown fur, pronounced simian brow and muzzle, human-like expressive eyes, pointed external ears, consistent cheek fur pattern

锁面要短、具体、可复制。

## 8. 表演连续性

人物一致不等于静态复制。

黛玉的行为库：
- 认真做事
- 轻微嫌弃
- 侧眼观察
- 克制笑
- 轻声讽刺
- 专注照顾
- 安静阅读
- 疲倦靠肩

悟空行为库：
- 偷看
- 抢食物
- 护着伞
- 帮忙但笨手笨脚
- 假装不疼
- 做错后看反应
- 对外警惕、对内放松

短剧的 CP 感来自动作关系，不来自每镜拥抱。
