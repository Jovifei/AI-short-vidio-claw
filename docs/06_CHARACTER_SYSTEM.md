# 06 角色一致性与双身份系统

## 1. 目标

“同一个角色”不只是锁脸，而是锁：
- 头脸比例
- 眼眉鼻口
- 下颌
- 年龄感
- 体型
- 发型/毛发
- 身高差
- 服装 stage
- 道具状态
- 表演习惯

**项目真正的 P2 Gate 是两位主角在同一关键帧中同时稳定。**

## 2. 林黛玉原创视觉方向

不是复制任何具体现代演员。

固定方向：
- 圆润偏鹅蛋脸
- 自然收窄的下颌，非 V 脸/尖下巴
- 细长眼型
- 单眼皮/内双视觉均可
- 眉细、略带轻蹙
- 鼻口小巧自然
- 纤细但不是“病弱摆拍”
- 古典气质进入现实生活场景

表情库：
- 专注
- 轻微嫌弃
- 侧眼
- 克制笑
- 讥诮
- 好奇
- 倔强
- 照顾
- 疲倦

禁止：
- 网红尖下巴
- 夸张大双
- 韩式高饱和妆
- 每镜歪头
- 复制具体演员五官/服饰

## 3. 孙悟空原创视觉方向

固定：
- 暖金棕毛
- 清晰猿猴眉骨/口鼻
- 稳定耳形
- 人形体态
- 毛发方向一致
- 日常服装实用、旧、易活动

禁止：
- 普通人脸加毛
- 毛色乱变
- 耳形随机
- 身高体型漂移
- 复制特定影视版猴妆

## 4. Reference Pack

每人 20–30 张 approved：
- front
- 3/4 left/right
- profile
- half body
- full body
- neutral
- smile
- annoyed
- caring
- tired
- 主 stage

Reference 未稳定前不训练 LoRA。

## 5. 单人 identity 候选

DAIYU：
- PuLID
- IPAdapter FaceID
- Character LoRA

WUKONG：
- Character LoRA
- reference conditioning

P1 不测试这些。
P2 本机 benchmark 后才能选。

## 6. 双身份同框专项

原路线最大缺口不是“PuLID 能不能锁黛玉”，而是：
**同一张图里能不能同时守住黛玉和悟空。**

候选：
A. Hero Lane：ChatGPT/人工关键帧
B. DAIYU identity ref + WUKONG LoRA/ref
C. two-pass regional inpaint/composite
D. regional mask/conditioning

选择原则：
- 少节点
- 可重复
- 人物关系自然
- 不为自动化牺牲最终图

## 7. 双身份 10 场景回归集

固定：
1. 冰箱
2. 同桌
3. 阳台
4. 公交
5. 雨伞
6. 洗碗
7. 开门
8. 买菜
9. 沙发/看书
10. 夜灯床边

Gate：
至少 8/10 同时满足两边 identity ≥4/5。

## 8. Stage

不覆盖 base：
DAIYU_BASE / HOME / RAIN / SLEEP / OUTDOOR
WUKONG_BASE / HOME / RAIN / INJURED / OUTDOOR

只记录变化项。

## 9. 连续性锁示例

DAIYU_LOCK_FACE：
rounded oval face, natural soft jawline, non-pointed chin, narrow almond eyes, subtle single/inner eyelid impression, fine slightly arched brows

WUKONG_LOCK_FACE：
warm golden-brown fur, pronounced simian brow and muzzle, expressive human-readable eyes, stable pointed ears, consistent cheek fur

锁面要短、具体、可复制。

## 10. 表演一致性

CP 感来自生活动作，不来自每镜拥抱。

DAIYU：
专注、嫌弃、轻讽、照顾、安静、疲倦。

WUKONG：
偷看、护伞、抢食、笨拙帮忙、装不疼、看她反应、对外警惕对内放松。
