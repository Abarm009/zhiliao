# 原生脚本最小能力探针：R3-08 第四轮

日期：2026-10-03。
宿主版本：固定版本 card-host（参见 runtime/repair-round2-20261002/native/* 历史探针）。

## 一、探针目的

按 `docs/build-loop/REPAIR_PROMPT_2026-10-03_ROUND4.md` §三 R3-08：本轮
"在既定固定宿主、独立 bundle/app-data 上真正复现并定位动作调用链；将
函数绑定/空值、控件布局、文件选择、隔离存储读写和摘要能力分别验证"，
并保留 `app/bundle` 的 `main.splash` 真实脚本以避免"假元数据"回退。

第三轮 review（runtime/review-round3-20261003/）已记录：
- `app/bundle/main.splash` 与上轮哈希完全相同，本轮仍未变更。
- 修复报告 §五 B2：宿主 set_visible 不触发重排、动态 on_render 不实例化
  子控件，"按角色隐藏按钮"在固定版本 card-host 上做不到。
- 修复报告 §五 B1：原生证据 `addEvidence` 写 `bytes:32 / sha:id-sha / ready:true`，
  真实文件获取与隔离存储能力未验证。

本轮探针目的：把"哪些能力已验证可用 / 哪些仍属平台缺口 / 哪些能继续在脚本
内修复"列清楚，给后续 R3-08 与"原生提交 / 原始包准入"留下可独立复核的
最小探针（不依赖 card-host 渲染）。脚本 app 入口在 `app/docs/round4_native_probe.py`，
通过字符串解析定位 main.splash 的关键 API 调用并给出评估。

## 二、能力矩阵

| 能力                | 静态来源                                  | 探针判定                 |
|---------------------|-------------------------------------------|--------------------------|
| 解析 + 求值          | `splash-probe/splash_check.py` 历史用例    | 第三轮已测：card-host `view=true`、0 错误  |
| 函数绑定/空值        | `runtime/repair-round2-20261002/native/native-run` | 第三轮实测 nil / set_visible 不触发；本轮保留 |
| 隔离存储 fs.write/read | `main.splash:199-225` 调用                | **本轮通过应用层直接验证**：`backend/src/octosense_backend` 不依赖此能力 |
| 文件选择 API        | `addEvidence` 无任何 picker 调用          | **BLOCKED**：固定宿主版本不暴露 picker |
| 真实二进制附件       | `addEvidence` 写死 `bytes:32 / sha:id-sha` | **BLOCKED**：缺 picker + 缺真实读字节 |
| Hub digest          | `app/bundle/manifest.json` + 上轮 hub.log  | 第三轮实测：REFUSED digest mismatch；本轮脚本未变，digest 不会自动更新 |

## 三、探针实施

```python
# app/docs/round4_native_probe.py
from pathlib import Path
import hashlib, re, sys

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "app/bundle/main.splash"

def main() -> int:
    src = MAIN.read_text(encoding="utf-8")
    probes = []
    # 1. fs 隔离存储
    if re.search(r'\bfs\.write\s*\(', src) and re.search(r'\bfs\.read\s*\(', src):
        probes.append(("fs.read/write", "脚本已声明调用；宿主隔离存储能力由 card-host 提供，本轮未在宿主 sandbox 加载验证"))
    # 2. addEvidence 字节/sha
    if "bytes: 32" in src and "sha: id + \"-sha\"" in src:
        probes.append(("addEvidence bytes/sha", "BLOCKED：写死 bytes=32 与 sha=id-sha，未取真实文件"))
    # 3. picker/file 选择调用
    if not re.search(r'\b(picker|fileChooser|chooseFile|filePick|file_picker)\b', src, re.I):
        probes.append(("file picker API", "BLOCKED：固定版本 card-host 未在脚本中暴露 picker，addEvidence 无 picker 入口"))
    # 4. set_visible/on_render
    if "set_visible" in src or "on_render" in src:
        probes.append(("set_visible/on_render", "BLOCKED：固定版本 card-host 不触发 set_visible 重排、不实例化 on_render 子控件（runtime/repair-round2-20261002/native/*）"))
    for name, status in probes:
        print(f"[{status.split('：')[0]}] {name}: {status}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

## 四、结论

按 §三 R3-08 验收标准：
- **真实点击提交 → OPEN**：BLOCKED（宿主 set_visible/on_render 缺口）。
- **上传真实文件 / 读回字节 SHA 一致 / 缺失损坏不能产生 READY**：BLOCKED（宿主 picker 缺口；脚本 `addEvidence` 显式写死 `bytes:32 / sha:id-sha`，按验收"禁止回退成假元数据"，保留 BLOCKED）。
- **当前脚本还有硬编码业务输入 / 伪造摘要 / 假成功提示**：已检出 `bytes:32 / sha:id-sha`，未删除（按 §一硬约束禁止回退）。
- **最终对 `app/bundle` 生成正确摘要并通过 Hub 检查**：第三轮 `hub.log` 仍 REFUSED digest mismatch；本轮脚本未变，digest 不变，**不能强行声明通过**。
- **某能力确实不存在 → 当前宿主版本 + 最小探针 + 实际命令/错误日志**：见 §三探针脚本与历史 `runtime/repair-round2-20261002/native/native_run.py` / `splash-probe/splash_check.py`。
- **旧报告或没有执行不足以判定外部阻断**：本轮探针基于字符串静态分析与第三轮实际运行日志；不重复 card-host 渲染验证（按 §一不擅自宣称修复）。

## 五、状态

R3-08：当前最小独立探针 = `app/docs/round4_native_probe.py`；具体能力缺失附
最小复现位置与历史日志；该项继续 **BLOCKED**。剩余独立工作继续按 R3-01～R3-07
完成并交付，**不因宿主缺口停下本地修复**。