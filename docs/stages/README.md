# 阶段执行文档

本目录不是“参考建议”，而是给本地 Agent/Codex 逐阶段执行的工作单。

执行顺序：

1. P0R_REBASE_EXECUTION.md
2. P1A_WAN22_5B_BASELINE.md
3. P1AQ_VISUAL_QUALITY.md
4. P1B_OPTIONAL_ALTERNATIVES.md（条件触发）
5. P2_CHARACTER_DUAL_IDENTITY.md
6. P3_EP001_FIRST_CUT.md
7. P4_CONTROL_PLANE.md
8. P5_AUDIO_LIPSYNC_POST.md
9. P6_AUTOMATED_EPISODE.md
10. P7_SERIES_SCALE.md

规则：
- 不越级；
- Gate 未过不自动进入下一阶段；
- P1B 是可选，不是必做；
- 每阶段只解决一个主要风险；
- 实测结果写入 docs/benchmarks；
- 关键结论同步 PROJECT_STATE / ROADMAP / ADR。
