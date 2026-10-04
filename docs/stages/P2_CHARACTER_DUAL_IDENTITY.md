# P2 双身份同框关键帧专项

## 为什么 P2 不先从 LoRA 开始

项目真正需要的是：
**林黛玉 + 孙悟空在同一张生活照里同时稳定。**

单人脸一致不等于 CP 短剧可生产。

## Step 1：锁角色 Bible

DAIYU：
- 圆润鹅蛋
- 自然下颌，非尖下巴
- 细长眼型，单/内双视觉
- 细眉
- 古典灵秀，不网红化
- 不固定歪头

WUKONG：
- 暖金棕毛
- 稳定耳形/眉骨/口鼻
- 人形比例
- 非普通人脸加毛

## Step 2：Reference Pack

每人 20–30 张 approved：
- front
- left/right 3/4
- profile
- half/full body
- neutral
- smile
- annoyed
- caring
- tired

数据未稳定前不训练 LoRA。

## Step 3：双身份方案最小矩阵

最多选 3 种：
A. Hero Lane 人工/ChatGPT
B. 人类 identity ref + 悟空 LoRA/ref
C. two-pass regional inpaint/composite

可选 D：
regional conditioning / regional mask

不要一开始叠 6 个 identity node。

## Step 4：10 个固定场景

1. 并排看冰箱
2. 坐桌边
3. 阳台浇花
4. 公交并排
5. 雨伞下
6. 洗碗
7. 开门
8. 买菜
9. 沙发看书
10. 夜灯床边

先不测试复杂包扎手指。

## 评分

每张：
- Daiyu identity
- Wukong identity
- height ratio
- costume stage
- anatomy
- interaction
- composition

## Gate

10 个场景中：
- ≥8 张两边 identity 都 ≥4/5
- 无明显网红化黛玉
- 悟空不人脸化
- 可重复生成相似关系

## 输出

- 角色 approved pack
- 双人 keyframe workflow/方法
- P2 benchmark
- 是否需要 LoRA 的明确结论
