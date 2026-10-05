# 22 本地 Codex / ComfyUI 最终交接单

## 本文件用途

仓库中能由远端规划、写作、结构化完成的工作应先完成。
只有以下工作真正依赖用户本机、ComfyUI、显卡或本地素材。

## 本地必须做的工作

### 1. 把用户认可的人物/服装 reference 放入 local/
位置：
local/references/active_visual_target/

需要：
- daiyu/face
- daiyu/costume
- wukong/face
- wukong/costume
- composition/lookreel01

然后运行 reference index/hash 工具。

### 2. 视觉批准
本地不能自己批准。
必须把 contact sheet / candidate 给用户看。
用户批准后更新 approval manifest。

### 3. Production I2V
只有 approved keyframe 才能进入：
workflows/video/production/

### 4. GPU 渲染
Wan2.2-TI2V-5B 使用已安装模型：
F:/ComfyUI/models/...

现有 ComfyUI：
http://127.0.0.1:8188

实际环境仍以本机当前状态为准。

### 5. FFmpeg 合成
使用 episodes/*/edit_plan 和 accepted assets。

## 本地 Agent 不能做的决定

- 不能自己批准人物脸；
- 不能把 candidate 自动改 APPROVED；
- 不能因为某模型方便就改变人物服装；
- 不能跳过 approved keyframe 用 T2V；
- 不能为了提高动态比例自动升级 M0/M3；
- 不能未经用户批准替换主视频模型。

## 当前本地执行顺序

1. git pull
2. 阅读 AGENTS / PROJECT_STATE / docs/18 / docs/19
3. V0 reference import
4. 生成 contact sheet 与 manifest
5. 等用户批准
6. K1 十张 keyframe
7. 等用户批准
8. T1 approved I2V
9. E0 Look Reel
10. 等用户批准
11. E1 EP001

## 交付给远端审核的最小材料

每阶段提交 Git：
- manifest
- QA
- prompts
- workflow metadata
- benchmark
- textual status

大媒体不进 Git，除非明确放到 review 目录用于审核。
