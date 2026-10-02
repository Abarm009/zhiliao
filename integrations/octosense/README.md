# OctoSense 集成边界（尚未实现）

**2026-09-27优先依据：[13 Hub实证修订](../../docs/implementation/13_APP_HUB_SUBMISSION_REVIEW.md)**。目标先验证Hub脚本应用`main.splash`；下面9/22–26的Rust broker与本机配对路线已停止作为默认。此目录仍为空实现边界，尚无bundle。身份/事务/模型/附件先过G0，不自行增加宿主服务绕开封闭能力表。

此目录只预留集成职责，不含官方 SDK、宿主应用或可运行任务卡。

2026-09-26更新：见[07架构修订](../../docs/implementation/07_REVISION_20260926.md)和[09运行Harness](../../docs/implementation/09_AGENT_HARNESS.md)。G0须取得实际课程包/宿主版本并验证本地业务服务接入；日期已过不能当作发布包已验证。固定app身份/digest保持，P0只组合已注册界面片段，不动态执行任意生成脚本。Matrix用于分享入口，不替代后端项目授权；本文后续9/22方案按该修订理解。

2026-09-22确定的比赛主路线：扩展robrix2原生维修应用，Rust/Makepad/Octoscript L0沿用所选宿主版本，受控Rust broker访问Python后端。完整[技术栈与本地配对](../../docs/implementation/03_TECH_STACK.md)、[接口](../../docs/implementation/04_DATA_API.md)、[官方来源与G0边界](../../docs/implementation/06_OFFICIAL_COMPLIANCE.md)已提供。

本地配对是本项目自有设计，不是官方身份API。具体控件与桥接方法必须通过固定宿主构建验证；本目录后续保存app.card、适配代码、宿主分支/补丁、版本及复现说明，不保存密钥。原生界面、实际模型和业务闭环分别验收。以下通用接入说明应结合当前原生路线执行。

先核对赛方发布包和官方样例，记录仓库、版本、支持系统与能力。最小验证为：宿主卡片读取本地测试任务 → 用户确认 → 后端状态变化 → 卡片读取回执。根据实际接口选择 HTTP、MCP 或宿主要求的桥接，不能事先宣称任意一种已经支持。

平台特有的卡片组件、脚本、能力声明、事件转换与打包配置放这里；任务状态、授权检查、偏好和业务判断留在后端。适配器失败时旧 Web 基线仍可用于排障，但旧页面不算完成平台接入。
