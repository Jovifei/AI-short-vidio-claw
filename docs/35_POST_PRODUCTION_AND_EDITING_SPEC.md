# 35 后期、剪辑与交付规范

状态：ACTIVE PREPRODUCTION

## 1. 后期顺序

Picture Lock 之前不做重调色。

流程：
Story Cut
→ Picture Cut
→ Sound Cut
→ Subtitle
→ Color/Texture
→ Technical QC
→ Final Approval

## 2. Story Cut

目标：
只回答一件事：
“看得懂故事吗？”

素材允许混用：
- static still
- M1 clip
- M2 clip

不要因为静态多就判失败。

## 3. 节奏

生活段：
2–3 秒/镜

情绪段：
3–4 秒/镜

极短 insert：
0.8–1.5 秒，少用。

EP001 目标：
约 55–70 秒。

## 4. 静态图动画

允许：
- 1–4% slow zoom
- 轻微 pan
- parallax
- rain/light overlay
- grain

禁止：
过大的 Ken Burns 导致脸被裁掉。

## 5. 动态片处理

优先使用原始完整 take。

仅在必要时：
- trim
- speed 95–105%
- slight stabilization

不要通过大幅变速掩盖动作失败。

## 6. FPS

模型 source fps 与 delivery fps 分开记录。

Delivery：
第一版 24fps。

如果 source 本来 24fps：
不需要为了“更顺”自动插帧。

插帧只有在：
- source 明显跳
- 人物脸不会被破坏
时进入 Lab 测试。

## 7. Resolution

第一版关键目标：
竖屏构图正确、脸稳定。

最终交付可考虑：
1080×1920。

是否 upscale：
后续对人物脸/毛发做 A/B 后再冻结，不预先承诺某一模型。

## 8. Color

不要把不同模型输出强行调成完全一样的肤色。

先统一：
- white balance
- contrast
- saturation
- black level
- highlight rolloff

再做轻风格。

## 9. Grain

轻微 film grain 可以：
- 统一静态和视频质感
- 遮盖部分生成纹理差异

但不能用重 grain 掩盖坏脸。

## 10. 字幕

第一版：
- 简洁白字
- 清晰描边/阴影
- 底部安全区
- 不遮手和脸

台词少，避免花哨动态字幕。

## 11. 转场

默认：
hard cut。

少量：
cross dissolve。

禁止默认：
- page turn
- zoom transition
- glitch
- flashy wipe

## 12. 封面

封面选择：
Identity 最稳定的一张双人 Hero Frame。

优先：
- 两张脸都清楚
- 关系一眼可见
- 背景不复杂

## 13. 文件

local/production/<ID>/edit/
- assembly_v001.mp4
- picture_lock_v001.mp4
- sound_v001.mp4
- final_candidate_v001.mp4
- final_approved.mp4

## 14. Export Manifest

记录：
- input accepted assets
- edit version
- ffmpeg version
- resolution
- fps
- codec
- audio codec
- duration
- hash

## 15. Final Technical QC

- 无缺镜
- 无黑帧
- 无冻结异常
- 无音频爆点
- 音画同步
- 字幕不越界
- 封面正确
- manifest 完整

## 16. 最后质量原则

如果：
A. 高清但人物脸错
B. 720p/1080p upscale 后脸正确

永远选 B。
