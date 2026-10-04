# prompts

Prompt 只是一层执行资产，不是人物事实本身。

目录建议：
- system：Agent/Codex 系统级约束
- image：关键帧模板
- video：动作模板
- qa：VLM 检查模板

规则：
- 人物固定事实来自 assets；
- 剧情事实来自 episode；
- prompt 通过模板组合它们；
- 不把真实演员名字当主要身份提示；
- 每次 prompt revision 可追溯。
