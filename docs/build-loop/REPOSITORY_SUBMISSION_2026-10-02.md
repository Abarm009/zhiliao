# 知了初赛源码仓库提交记录

- 日期：2026-10-02（Asia/Shanghai）
- 队伍名：知了
- 公开仓库：[Abarm009/zhiliao](https://github.com/Abarm009/zhiliao)
- 提交入口：`https://github.com/gosimfoundation/hackathon-agenticapp26/issues/13`
- 用户已明确授权新建仓库、提交代码并按该 Issue 格式登记队伍与仓库地址。
- 状态：179 个源码与文档文件已提交，赛事仓库地址评论已发布并回读。
- 评论回执：[Issue #13 · 知了提交](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/13#issuecomment-5945671513)

## 提交范围

保留本项目应用源码、旧后端迁移基线、测试、依赖锁文件、设计、审查和迁移记录。保留有来源说明的仿真种子，来源见 `backend/data/simseed/PROVENANCE.md`；这些数据不代表真实模型的学习效果。

忽略本地 `.env` 和密钥、运行数据库、运行日志与附件、虚拟环境、缓存、构建产物及三个官方参考源码克隆。`--app-dir` 经文件类型检查为 SQLite 数据库，显式排除。仅增加忽略规则，不删除本地文件。

`runtime/` 中的历史核验原始日志未公开上传；审查文档中的本地证据路径不能作为远端可下载证据。官方参考版本仍由 `references/README.md` 记录，参考克隆本身不进入本仓库。

## 状态边界

本次工作仅登记源码仓库，不重新判定业务、原生界面、模型或平台验收结果。最近的独立核验为 `REPAIR_VERIFICATION_2026-10-02.md`，其中 V01–V11 不能因发布仓库而自动改判。没有在本次提交工作中重新运行全部业务测试。

本次仅授权赛事仓库地址评论，不代表 Hub 收录或其他平台提交已完成。历史文档中的外部授权状态保留为当时记录。

## 验证方式

推送前检查 Git 暂存文件清单、忽略项、嵌套仓库、数据库文件头和常见凭据格式；推送后回读远端分支提交；评论后回读队伍名、仓库地址和评论链接。实际结果另记于本地 `runtime/repository-submission-20261002/`。

## 实际结果

- 发布前快照：179 文件，4,788,484 字节；常见凭据格式、数据库文件头、嵌套 Git 条目检查无发现。此处为明确范围的检查结果，不是完整安全审计。
- 通过已登录的 GitHub 网页分两批提交（100 + 79 文件）。源码提交：[`24884b03920781597c8b50aa7513d264400fe792`](https://github.com/Abarm009/zhiliao/commit/24884b03920781597c8b50aa7513d264400fe792)。
- 将该远端版本 fetch 回本地后逐一比对：179 文件，无缺失、无多余文件，全部文件内容 Git blob SHA 与发布前快照一致。
- 网页上传将 `backend/scripts/e2e_full_chain.sh` 存为普通文件模式；脚本内容一致，按文档使用 `bash backend/scripts/e2e_full_chain.sh` 调用。本地原始 Git 快照另行保留。
- 本机 HTTPS Git 未配置可用凭据，已有 SSH 无法通过 GitHub 认证；连接器写新仓库返回权限不足。本次成功上传使用浏览器登录会话，未创建或提取访问令牌，未变更账号权限。后续命令行推送仍需配置 GitHub 认证。
- 主办方 Issue 评论已通过 GitHub API 回读，作者 `Abarm009`，评论 ID `5945671513`，正文如下。

```text
队伍名：知了
GitHub 仓库地址：https://github.com/Abarm009/zhiliao
```

本文件和 README 的发布状态说明随后单独补充；上列源码提交固定不变，后续修复继续正常提交，不因登记地址冻结开发。
