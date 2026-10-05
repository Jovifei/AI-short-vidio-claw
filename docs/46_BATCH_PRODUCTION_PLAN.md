# 46 批量生产与复用计划

状态：PREPRODUCTION COMPLETE

## 1. 为什么要批量“同类资产”，不是批量“整集”

最容易产生漂移的是：
- 同一人物在不同时间重复建模
- 同一场景每集重新生成
- 同一服装每次 prompt 重写

所以批次按资产类型组织，而不是“把一整季一口气生成完”。

## 2. 推荐批次

### Batch A — Character
先完成：
- DAIYU Golden Model
- WUKONG Golden Model
- Couple Scale

### Batch B — Home Environment
一次性准备：
- entry
- living room
- kitchen/fridge
- sink
- balcony
- bedroom

用于 EP001/002/003/005/006/009/010。

### Batch C — Daily Props
- medkit
- bandage
- umbrella
- basket
- bowls
- camera
- bouquet
- comb
- writing set

### Batch D — LOOKREEL
10 keyframes 先全做静态。
通过后再选 4 个 I2V。

### Batch E — EP001
20 stills 先完成。
通过后选 4–6 motion。

### Batch F — Rain
一次固定：
- rain intensity
- umbrella
- cold/warm light
- wetness
供 EP001/005/007。

## 3. 同批生成规则

同一批次固定：
- character reference
- costume stage
- color style
- camera grammar

只变化：
- pose
- composition
- expression
- environment

不要同时变所有条件。

## 4. Reference Freeze

批次开始前保存：
- identity refs hash
- costume refs hash
- prompt template hash
- style config hash

批次中不随意替换 Golden Face。

## 5. Candidate 数量

低风险：
每镜 1–2 candidate。

中风险：
2–3。

高风险：
优先 Hero/manual edit，不无限抽。

## 6. 审核节奏

每完成 3–5 张：
停下来审核一次。

不要等 20 张全做完才发现人物已经漂移。

## 7. 资产复用

场景 reference 只要不被剧情改变：
跨集复用。

服装：
同 stage 跨集复用。

声音：
同 voice id 跨集复用。

道具：
同 prop id 跨集复用。

## 8. 变更冻结

第一集进入 Picture Lock 后：
不要因为第二集有更好新模型，就回头重做第一集全部资产。

新模型先进入 Lab。

## 9. Wave

Wave 1：
LOOKREEL01 + EP001

Wave 2：
EP002 + EP007

Wave 3：
EP003/004/006

Wave 4：
EP005/008/009/010

## 10. 批次 KPI

记录：
- candidate count
- approved count
- reroll count
- GPU minutes
- review time
- failure reason

三批以后才能决定哪个环节值得自动化。
