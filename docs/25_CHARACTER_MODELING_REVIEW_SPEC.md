# 25 人物建模与审核规格（Character Modeling Review Spec）

日期：2026-10-05
状态：ACTIVE
目的：把“像不像”从主观争论变成可重复的审核流程。

## 1. 为什么先做人物建模板

本项目不是普通短剧。孙悟空与林黛玉都属于观众已有强视觉记忆的人物。
只要脸不对，即使构图、灯光、动作全部漂亮，用户仍会认为“不是那个人”。

因此人物审核必须早于：
- 视频运动；
- 场景复杂化；
- LoRA 训练；
- 批量生产。

## 2. 第一批必须产出的建模图

每个角色至少建立 2 张正式建模图：

### A. Face Identity Sheet
用于锁脸。
必须包含：
- 正面
- 左 3/4
- 右 3/4
- 左侧面
- 右侧面
- 中性表情
- 轻笑
- 轻微不悦/认真
- 不同光照下仍保持相同五官

### B. Full Character Sheet
用于锁体型与服装。
必须包含：
- 正面全身
- 3/4 全身
- 侧面全身
- 半身
- HOME stage
- OUTDOOR stage
- 关键服装细节放大
- 发饰/头箍/腰带/护腕等细节

### C. Couple Scale Sheet
两个角色同框：
- 正面并肩
- 侧面并肩
- 坐姿并排
- 身高差
- 肩宽/头身比
- 靠近但不接触
- 轻微接触

这一张主要用来防止每个镜头身高比例漂移。

## 3. 林黛玉建模审核点

### 3.1 Face Geometry

必须检查：
- 脸不是现代 V 脸；
- 下颌自然向下收；
- 下巴小但不尖；
- 颧区自然，不做欧美骨相；
- 面中比例柔和；
- 脸宽不能在不同角度忽大忽小。

### 3.2 Eyes / Brows

- 眼神偏含蓄；
- 眼裂自然，不放大成通用 AI 大眼；
- 眉线细，眉峰柔；
- 不能所有表情都忧郁；
- 正常、轻笑、嫌弃、专注都要成立。

### 3.3 Nose / Mouth

- 鼻部体量自然小巧；
- 唇部不过分丰厚；
- 不出现现代整形感；
- 不使用明显欧美唇妆。

### 3.4 Hair

需要固定：
- 刘海轮廓
- 发髻高度
- 两侧鬓发
- 发饰位置
- HOME/OUTDOOR 可轻量变化，但不能下一镜完全换发型。

### 3.5 Body

- 纤细；
- 肩线自然；
- 不是儿童比例；
- 不是现代时尚模特夸张长腿；
- 坐姿和站姿都保持相同体态。

## 4. 孙悟空建模审核点

### 4.1 Species Read

最重要问题：
第一眼是否是“经典猴王”，而不是：
- 普通男性脸加金毛；
- 西方猿人；
- 狮子/狐狸；
- 大猩猩；
- 兽人。

### 4.2 Face Landmarks

需要固定：
- 眉骨形状
- 眼窝
- 鼻梁到吻部过渡
- 上下唇/吻部轮廓
- 面颊毛区
- 额头毛线
- 耳形
- 耳位
- 下颌毛
- 头箍位置

### 4.3 Fur Map

必须建立“毛发地图”：
- 额头毛方向
- 面颊毛方向
- 下颌毛
- 颈部毛
- 前臂毛
- 手背毛
- 尾巴颜色/长度

同一角色不同镜头不能随机改变毛发分区。

### 4.4 Expression

必须测试：
- 中性
- 轻笑
- 认真
- 疼痛但忍着
- 偷看
- 保护
- 轻微生气

原则：
表情变化不能把猴脸拉回人类脸。

## 5. Costume Modeling

### DAIYU
OUTDOOR：
- 多层轻薄古装
- 淡色
- 发饰稳定

HOME：
- 层数减少
- 面料更轻
- 仍然古典

RAIN：
- 与 OUTDOOR 同一套或明确的雨天 stage
- 湿度变化可控

### WUKONG
OUTDOOR：
- 经典猴王视觉语言
- 固定腰带、护腕、主色

HOME：
- 去除重装
- 保留古装结构

INJURED：
- 继承 HOME/OUTDOOR 之一
- 额外加入伤口/绷带 continuity

## 6. 建模图审核顺序

每次不要同时看所有东西。

### Pass 1：Face
只问：
“是不是我们要的这个人？”

### Pass 2：Species / Face Stability
悟空：
猴脸结构对不对？

### Pass 3：Hair/Fur
固定结构是否稳定？

### Pass 4：Costume
服装是否属于批准 stage？

### Pass 5：Body Ratio
身高、肩宽、头身比。

### Pass 6：Expression
不同表情是否仍像同一个角色。

## 7. 打分

每张建模图：

DAIYU：
- Face identity /5
- Face geometry /5
- Eyes+brows /5
- Hair /5
- Costume /5
- Body /5

WUKONG：
- Face identity /5
- Species read /5
- Brow+muzzle+ear /5
- Fur map /5
- Costume /5
- Body /5

Hard Gate：
任意 identity < 4 → REJECT。

## 8. Golden Model 状态

只有用户明确批准后，才允许：

status: GOLDEN_MODEL_APPROVED

批准后：
- 不再通过 prompt 自由改脸；
- 后续任何新 reference 都必须与 Golden Model 比较；
- LoRA 训练数据也必须来自 approved set。

## 9. 文件位置

本地：
local/references/active_visual_target/
local/production/MODEL_REVIEW/

Git：
assets/characters/daiyu/modeling_review.yaml
assets/characters/wukong/modeling_review.yaml
docs/25_CHARACTER_MODELING_REVIEW_SPEC.md

## 10. 当前建议

先出：
1. 一张 DAIYU Face/Full Model Sheet
2. 一张 WUKONG Face/Full Model Sheet
3. 一张 Couple Scale Sheet

用户批准以后再进入 K1 十构图。
