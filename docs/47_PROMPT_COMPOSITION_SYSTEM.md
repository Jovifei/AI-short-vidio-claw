# 47 Prompt 组合系统

状态：ACTIVE

## 1. Prompt 不是事实源

事实源来自：
- identity reference
- costume stage
- shot card
- continuity
- visual bible

Prompt 只是把这些事实传给模型。

## 2. Image Prompt 结构

顺序固定：

### A. Identity Contract
“Use supplied approved identity references as source of truth.”

### B. Costume Contract
明确 stage ID。

### C. Composition
- shot size
- camera angle
- body positions
- eye line

### D. Frozen Moment
这一帧正在发生什么。

### E. Environment
场景和道具。

### F. Lighting
光线方向、时间。

### G. Texture
live-action / natural / restrained。

### H. Hard Reject
身份/服装/解剖错误。

## 3. 不要写的东西

避免堆：
- masterpiece
- best quality
- ultra beautiful
- goddess
- handsome man
- fashion editorial

这些会把人物拉向通用审美。

## 4. Character Token

文字可辅助：

DAIYU：
soft rounded oval face, restrained classical eyes, delicate brows, classical updo, pale layered robe

WUKONG：
golden-brown simian face, stable brow ridge, clear muzzle, stable ears, Buddhist victory ornaments

但最终仍以 reference 为准。

## 5. Video Prompt 结构

### A. Preservation
Preserve exact identity, costume, props.

### B. Primary Motion
只能一个。

### C. Secondary Motion
最多一个。

### D. Camera
简单。

### E. Environment
轻微。

### F. Negative Motion
No new people / no costume change / no identity redesign.

## 6. Prompt Revision

命名：
IMG_<SHOT>_r001
VID_<SHOT>_r001

任何核心词改变：
revision +1。

## 7. Prompt Delta

每次失败只改一个方向。

例如 identity drift：
不要同时：
- 改 prompt
- 改 frames
- 改 sampler
- 改 reference

否则不知道哪个有效。

## 8. 镜头例子 SH006

事实：
悟空偷看黛玉。

Image：
两人已经是正确人物，黛玉收药箱，悟空侧眼看她。

Video：
Daiyu continues tidying the medkit. Wukong gives one brief side glance. Subtle breathing. Very slow push-in.

不再描述：
黛玉脸型、悟空毛发，避免模型重新解释。

## 9. Negative Prompt

Negative 主要防：
- identity drift
- modern clothing
- species drift
- extra limbs
- duplicated people
- distorted hands
- text/watermark

不要堆几十个互相矛盾风格词。

## 10. Prompt Library

Git：
prompts/image/
prompts/video/
prompts/qa/

Episode-specific：
episodes/<ID>/image_prompts.md
episodes/<ID>/video_prompts.md

模板与内容分开。
