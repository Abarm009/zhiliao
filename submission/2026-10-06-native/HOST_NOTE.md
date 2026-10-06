# 主办方进展说明草稿

> 任务书：「准备一段可发给主办方的简短进展说明，附 A/B 两版、视频及官方 Issue 链接。没有明确的主办方接收渠道时，只准备文案，不擅自发送。」
>
> 推荐发送时机：用户明确授权后；推荐渠道：比赛报名系统站内信 / Agentic App 2026 比赛官方邮件 / 微信群（如已建立）。

---

## 中文版（~280 字）

> 老师好，知了团队 2026-10-06 双版交付进展同步：
>
> A 版（Web/后端演示与比赛材料，commit `6d81d57b`，bundle blake3 `eff13f55...`）：82 秒正式普通话配音视频、7 张截图、`octosense-repair-0.1.0.zip` 应用包、提交说明已就位，材料在 `submission/2026-10-06/`。
>
> B 版（OctoSense 原生候选，commit 待冻结 tag `octosense-repair-b-v0.1.0`，bundle blake3 `5503136c...`）：A 版残留的 N1/N2 已实质修复——取消 ScrollYView、引入 tick() 1Hz 重算、把与 OctoScript 内置函数 `pick`/`me` 同名的用户函数改名 `pickUser`/`getMe`；并按独立 review 反馈修了 B-R01（addEvidence 写 demo 占位，submitCompletion 不再被伪 ready 蒙混）、B-R02（runCommand 恢复 hit/conflict 路径，消除字段访问错误）、B-R03（events.jsonl 改整体数组格式，重启后 9→9 events 完全恢复）、B-R05（身份切换按 visible 过滤）。DRAFT→OPEN→ACCEPTED→SCHEDULED 由真实 card-host（Hub@6741dea / Shell@a5d847a / Octoscript@68f6a9df）实测点击跑通；IN_PROGRESS 经合成 tasks.json 真实宿主验证。**不声称完整闭环到 COMPLETED**——review 已知的开工 scheduler 时序 + App picker 缺失让 IN_PROGRESS→AWAITING_ACCEPTANCE 卡住，已显式记录。B 版材料在 `submission/2026-10-06-native/`。
>
> 真实宿主兼容性仅在固定旧版本（Hub@6741dea lockfile）上验证；上游 main 与本机 lockfile 存在 commit 差异，未独立重编测试。
>
> 后端 190 项单测与 17 步 HTTP E2E 独立验证（与原生 bundle 解耦）。
>
> 已知限制（已显式标记，未冒充通过）：App 文件选择器、隔离存储读字节 API、grant 生命周期、真实模型接入、开工 scheduler timing、最新宿主兼容性。等 OctoSense 宿主补齐后再次递交更新版本。
>
> App Hub Issue 待发草稿在 `submission/2026-10-06-native/HUB_ISSUE.md`；GitHub 仓库：`https://github.com/Abarm009/zhiliao`。

---

## 英文版（~250 words）

> Team Zhiliao — 2026-10-06 dual-release progress update (post-review):
>
> **Version A** (Web/backend demo + contest materials, fixed commit `6d81d57b`, bundle blake3 `eff13f55...`): 82-second Mandarin video, 7 screenshots, `octosense-repair-0.1.0.zip` bundle, full VERIFICATION. Materials in `submission/2026-10-06/`.
>
> **Version B** (OctoSense native candidate, commit pending freeze under tag `octosense-repair-b-v0.1.0`, bundle blake3 `5503136c...`): A's outstanding N1/N2 fixed — drop ScrollYView, add `fn tick()` 1Hz refresh, rename user `pick`/`me` to `pickUser`/`getMe`. **Post-review additional fixes**: B-R01 (addEvidence writes `demo:true, ready:false`; submitCompletion is now correctly blocked when `readyCount<1`, no fake closure), B-R02 (runCommand recovers hit/conflict branches; field-access bug fixed), B-R03 (events.jsonl is now a JSON array; restart recovers 9→9 events exactly), B-R05 (setActor/prevTask/nextTask filter by `visible()`; switching to a non-owner shows "无可见任务" instead of someone else's draft). DRAFT→OPEN→ACCEPTED→SCHEDULED driven by real clicks on a real card-host (Hub@6741dea / Shell@a5d847a / Octoscript@68f6a9df); IN_PROGRESS verified via synthesized tasks.json. **We do NOT claim a complete closure to COMPLETED** — the review-known scheduler timing at startProgress + missing App picker halts the flow at IN_PROGRESS→submitCompletion, and that is honestly logged.
>
> "Latest OctoSense compatibility" is **not** independently re-verified: local binary corresponds to Hub@6741dea's lockfile; upstream main has diverged.
>
> Backend 190 unit tests + 17-step HTTP E2E remain as independent business evidence, decoupled from the bundle.
>
> Known limits (explicitly flagged, not faked): app file picker, isolated-storage read-bytes API, grant lifecycle, real model integration, startProgress scheduler timing, latest-host compatibility. We will re-stamp + re-check + re-scan once the host fills these in.
>
> App Hub Issue draft: `submission/2026-10-06-native/HUB_ISSUE.md`. Repo: `https://github.com/Abarm009/zhiliao`.

---

## 发送前确认

- [ ] 用户已明确主办方接收渠道（站内信 / 邮件 / 微信）
- [ ] 用户已批准发出内容（不擅自发送）
- [ ] 已附 A 版视频链接 / B 版 6 张截图 / App Hub Issue 链接 / GitHub 仓库链接
- [ ] 已附 stamp blake3 与 hash 校验（防止文件在传输中被改）
- [ ] 中文版 / 英文版根据主办方语言习惯选择
