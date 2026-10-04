"""backend/tests 顶层 conftest：继承基线测试的公共 helper + 数据隔离。

修复 V11 / 交接指令 §6.2：
  - `backend/tests/octosense_backend/conftest.py` 与 `backend/tests/conftest.py`
    同名，pytest 收集时 `from conftest import stream_of` 会解析到最近的那个，
    继承的 test_ops_agent / test_ops_api 因此收集失败。这里在 tests 顶层重新
    提供同一份 helper，让 `from conftest import ...` 稳定解析到本文件。
  - helper 从旧 WAgent 工作区**复制**而非依赖它（不引用旧目录，也不改旧代码）。
  - 数据文件指向临时目录，不污染 runtime/ops.db。
"""
from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def _isolated_data_file(tmp_path_factory: pytest.TempPathFactory):
    path = tmp_path_factory.mktemp("kg") / "kg.json"
    os.environ["WAGENT_KG_DATA"] = str(path)
    os.environ.setdefault("WAGENT_OPS_SIMSEED", "0")
    os.environ.setdefault("OCTOSENSE_DB", str(path.parent / "octosense.db"))
    os.environ.setdefault("OCTOSENSE_EVIDENCE_ROOT", str(path.parent / "evidence"))
    yield
    os.environ.pop("WAGENT_KG_DATA", None)


from _baseline_helpers import chunks_of, stream_of  # noqa: E402,F401
