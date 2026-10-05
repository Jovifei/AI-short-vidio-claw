# 49 AI Agent 操作规则

状态：HIGHEST PRIORITY AFTER AGENTS.md

## 1. Agent 的最大风险

不是不会做。
而是：
为了“继续推进”，在前置事实缺失时自己补答案。

本项目明确禁止这种行为。

## 2. 缺 Reference

不能：
“先用一个差不多的脸。”

必须：
BLOCKED_BY_REFERENCE。

## 3. 缺用户批准

不能：
自动把 CANDIDATE 改 APPROVED。

必须：
WAITING_USER_APPROVAL。

## 4. 技术能跑 ≠ 产品能用

Lab 成功只能记录：
LAB_VERIFIED。

只有内容 Gate 通过才：
PRODUCTION_READY。

## 5. 不越级

当前 stage 没过：
不执行后续 GPU 大任务。

## 6. 不扩技术栈

遇到一条视频不好：
先检查人物图和 motion。

不要自动安装：
- 新视频模型
- 14B
- 新 LoRA
- 新 custom nodes

除非当前路线被证明有系统性 blocker。

## 7. 不删除历史

错误输出：
可以清 temp。
但 benchmark、QA、approved、accepted 必须可追溯。

## 8. 任务结束报告

必须包含：
- 做了什么
- 没做什么
- Gate 状态
- Blocker
- 文件
- Commit
- 下一步

不要只说：
“继续优化了。”

## 9. 失败记录

失败也是资产。

必须记录：
- failure code
- parameters
- output
- reason
- next action

## 10. 改文档

如果执行发现文档错误：
先写：
OBSERVED_CONFLICT
再修文档/ADR。

不要悄悄按另一条路线做。

## 11. 用户视觉反馈

用户说：
“不像。”

优先解释为：
Identity Gate Failed。

不要回复：
“但技术测试成功。”

技术成功不能覆盖视觉失败。

## 12. 用户说“可以继续”

如果语义是方向认可但未明确最终锁定：
状态：
PREPROD_APPROVED。

只有明确：
“这个就是最终人物/锁定它”
才能：
GOLDEN_MODEL_APPROVED。

## 13. GPU 使用

只有通过 Guard 的 job 才能批量。

新 workflow：
先一条。

## 14. 写 Commit

建议：
docs:
prep:
feat:
fix:
benchmark:
asset:
qa:

Commit 不混入无关大改。
