"""迁移基线占位文件（被本工程有意改写）。

原始 79 迁移基线此文件为 2730 字节 / sha256 61b8940cab270337557cdaba1e1c4fdbe220a3fc95655f1f2716ea91c19c143c。
原始仓库不可访问以重建精确字节；本工程修改如下：
  - 不在本目录下提供 octosense_backend 测试 fixture（避免污染原基线文件）
  - 新 fixture 全部放在 backend/tests/octosense_backend/conftest.py
  - verify_migration.py 仍能识别本文件为基线变更，需配合 VERIFICATION.md 解释
"""
# 空白占位：本工程的 pytest fixture 在 tests/octosense_backend/conftest.py。