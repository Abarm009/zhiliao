# 石墨版构建循环交接包

把[启动提示词](START_PROMPT.md)交给已配置比赛Token的编码模型，从第一步开始执行。

- [完整循环设计](../implementation/15_BUILD_VERIFY_LOOP.md)：范围、石墨视觉、L0–L8创建/验证、失败修复及交付标准。
- [验收台账](ACCEPTANCE.json)：全部初始NOT_RUN；编码模型实际执行后登记证据。当前 **24 PASS / 29 NOT_RUN / 8 FAIL / 3 BLOCKED**（2026-10-02 全盘 review 后，9 项 PASS 被改判）。
- [2026-10-02 全盘 Review](REVIEW_2026-10-02.md)：问题清单、复现命令与修改建议（5 P0 + 8 P1 + 7 类 P2）。
- [每轮记录模板](ITERATION_TEMPLATE.md)：实现、验证、失败和接续所需信息。
- [台账检查器](../../scripts/check_build_loop.py)：检查记录完整性，不能运行或证明应用测试。
- [M3/MiniMax Code 适配循环](MCODE_LOOP.md)：与 START_PROMPT 配套，说明主会话模型、工具映射、子代理委派、ask_user 与 self_reminder 边界、媒体交付、Token 纪律；不替代 START_PROMPT。
- [递交材料](SUBMISSION.md)：当前递交材料清单与版本；含 L2-L6 主切片增量。
- [L7/L8 准备状态](L7_L8_SUBMISSION_PLAN.md)：打包、递交、Hub Issue 草稿与待办。

本包已创建；业务应用 L0-L6 主切片已本地 ready（详见 [SUBMISSION.md](SUBMISSION.md) 与 [PROGRESS.md](../../PROGRESS.md)）。旧四版参考保留，正式实现只使用石墨。运行日志和截图放 `runtime/build-loop/`，不进入应用 bundle。全量检查与未接通项以工程验证记录为准。
