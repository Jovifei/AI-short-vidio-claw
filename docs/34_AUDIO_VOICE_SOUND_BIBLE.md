# 34 声音、配音与环境声圣经

状态：PREPRODUCTION COMPLETE / LOCAL AUDIO EXECUTION DEFERRED

## 1. 核心原则

声音不是最后随便加一条 BGM。

这套生活短剧的真实感有一半来自：
- 房间底噪
- 水
- 碗筷
- 风
- 公交
- 雨
- 布料
- 小动作

## 2. 声音层级

1. Dialogue / VO
2. Ambience
3. Foley / SFX
4. Music

混音时 Music 优先级最低。

## 3. 林黛玉声音方向

不是模仿具体演员。

特征：
- 音量偏小但清楚
- 语速不快
- 句尾不做现代撒娇语气
- 讽刺时更轻，不更响
- 情绪变化靠停顿与气息

关键词：
restrained / intelligent / soft / dry wit / clear diction

## 4. 孙悟空声音方向

不是夸张卡通猴声。

特征：
- 反应快
- 日常时自然
- 有一点粗粝或明亮的颗粒感
- 认真时突然稳定下来
- 对黛玉语气会降低攻击性

关键词：
agile / warm / direct / playful / protective

## 5. 对白节奏

短句优先。

每句建议：
1–3 秒。

对话间保留：
0.2–0.8 秒真实停顿。

不要每个镜头都有台词。

## 6. EP001 台词

WUKONG：
“皮外伤。”

DAIYU：
“下次再逞能，我便不管你了。”

WUKONG：
“你每回都这么说。”

第一版可画外音。

## 7. 环境声库

### HOME_ENTRY
- 走廊空调/楼道底噪
- 门锁/门轴
- 轻脚步

### LIVING_ROOM
- 室内 room tone
- 药箱塑料/金属小声
- 布料

### KITCHEN
- 冰箱低频
- 包装轻响
- 水龙头
- 碗碟

### BALCONY
- 城市远声
- 风
- 叶片
- 衣物

### MARKET
- 多人低声但不能抢对白
- 塑料袋/篮子
- 摊位环境

### BUS
- 低频发动机
- 车身轻震
- 报站可模糊化避免具体品牌/线路

### RAIN
- 伞面雨点
- 地面水
- 远车
- 衣料湿声

## 8. Foley

优先真实 Foley，不要所有小动作都用夸张音效。

必须可听但轻：
- 放药箱
- 碗放桌
- 相机快门
- 雨伞打开
- 书页
- 衣袖

## 9. BGM

风格：
- 极简
- 少乐器
- 旋律不过度煽情
- 适合让环境声穿透

第一季可建立两个 motif：
A. Daily motif
B. Fate motif

宿命 motif 只在 EP008–EP010 明显出现。

## 10. 响度目标

后续本地混音参考：
- Dialogue 清晰优先
- 最终平台音量避免过度压缩
- 使用统一 loudness pipeline

具体 LUFS 以发布平台和实际素材测试后冻结，不在当前文档伪造已验证值。

## 11. Voice Asset

本地：
local/audio/voices/
local/audio/ambience/
local/audio/sfx/
local/audio/music/

Git：
assets/audio/voice_bible.yaml
assets/audio/soundscape.yaml

## 12. LipSync

LipSync 不是第一版核心。

先让：
角色正确 + 剪辑成立 + 声音成立。

只有正面/半侧稳定脸对白镜头才做。

悟空属于专项测试，不假设 MuseTalk 对猴脸稳定。
