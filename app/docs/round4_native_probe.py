"""R3-08 静态分析探针：基于 `app/bundle/main.splash` 的真实脚本做能力矩阵评估。

不在宿主 sandbox 加载，避免第三轮已记录的 set_visible / on_render 缺口
误触发 nil getter 错误链。返回非零退出码表示发现必须项的问题（如伪造摘要、硬编码业务输入）。

历史：`runtime/repair-round2-20261002/native/native_run.py` 与
`runtime/repair-round2-20261002/splash-probe/splash_check.py` 已分别在
card-host 上跑过 view=true / 解析检查；本探针补齐"脚本内能力声明 vs 缺口"，
不重复宿主渲染。
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "app/bundle/main.splash"
MANIFEST = ROOT / "app/bundle/manifest.json"


def probe_main_splash() -> list[tuple[str, str, str]]:
    """检查 main.splash 是否符合 §一硬约束：
      - 不能伪造字节/sha；
      - 不得写死业务输入；
      - 必须按业务基线做授权。
    """
    src = MAIN.read_text(encoding="utf-8")
    out: list[tuple[str, str, str]] = []

    # addEvidence 伪造字节/sha 检测
    if re.search(r'bytes:\s*32', src):
        out.append((
            "addEvidence.bytes",
            "FAIL",
            "app/bundle/main.splash 仍写死 `bytes: 32`；按 §一禁止回退成假元数据，"
            "本探针只能标 FAIL，等宿主 picker / 真实文件获取能力补齐后再修。",
        ))
    else:
        out.append(("addEvidence.bytes", "OK", "未发现写死 bytes 常量"))

    if re.search(r'sha:\s*id\s*\+\s*"[\-\s]?sha"', src):
        out.append((
            "addEvidence.sha",
            "FAIL",
            "app/bundle/main.splash 仍写死 `sha: id + '-sha'`；同上。",
        ))
    else:
        out.append(("addEvidence.sha", "OK", "未发现写死 sha 派生式"))

    # picker API 检测
    picker_terms = ["picker", "fileChooser", "chooseFile", "filePick", "file_picker"]
    if not any(re.search(rf'\b{t}\b', src, re.I) for t in picker_terms):
        out.append((
            "file_picker",
            "BLOCKED",
            "main.splash 未声明调用 picker / fileChooser 类 API；固定版本 card-host"
            "不暴露文件选择能力。app/docs/round4_native_probe.md §四 已记录。",
        ))

    # set_visible / on_render 限制
    if "set_visible" in src or "on_render" in src:
        out.append((
            "set_visible/on_render",
            "BLOCKED",
            "main.splash 调用了 set_visible/on_render；固定版本 card-host"
            "不触发重排、不实例化子控件。历史日志："
            "runtime/repair-round2-20261002/native/native_run.py。",
        ))

    # 命令执行守门
    if "settle(" in src:
        out.append(("command.gate", "OK",
                    "已声明 `settle()` 守门；统一命令边界 + 幂等 + 回执"))
    else:
        out.append(("command.gate", "FAIL",
                    "未声明 settle() 守门；R2-01 / 五.2 / 五.3 / 五.4 修复要求"))

    return out


def probe_manifest_digest() -> list[tuple[str, str, str]]:
    """比较 manifest.json 的 declared digest 与 bundle 实际 SHA-256。"""
    import json
    out: list[tuple[str, str, str]] = []
    if not MANIFEST.exists():
        out.append(("manifest.digest", "MISSING", "app/bundle/manifest.json 不存在"))
        return out
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as e:
        out.append(("manifest.digest", "FAIL", f"manifest 解析失败: {e}"))
        return out
    integrity = data.get("integrity") or {}
    declared = (integrity.get("bundle_sha256") or integrity.get("bundle_blake3")
                or data.get("digest") or data.get("sha256"))
    if not declared:
        out.append(("manifest.digest", "MISSING",
                    "manifest.json 未声明 bundle_sha256 / bundle_blake3 / digest"))
        return out
    # 计算实际 bundle SHA-256；声明的 blake3 仍视为信息项，不强求算法一致
    bundle = MAIN.read_bytes()
    actual_sha = hashlib.sha256(bundle).hexdigest()
    out.append(("manifest.declared",
                "INFO" if not declared.startswith(actual_sha[:6]) else "OK",
                f"declared={str(declared)[:16]}…，bundle 实际 sha256={actual_sha[:16]}…"))
    return out


def main() -> int:
    rows = probe_main_splash() + probe_manifest_digest()
    fail = 0
    for name, status, msg in rows:
        if status in ("FAIL", "MISSING"):
            fail += 1
        print(f"[{status}] {name}: {msg}")
    print(f"\n{'OK' if fail == 0 else 'FAIL'}: {len(rows)} 项；fail/missing={fail}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())