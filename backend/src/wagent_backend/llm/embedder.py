"""1024 维文本向量 —— recall/write_memory 的检索基础。

两个实现，按配置选择（WAGENT_EMBEDDING=api|local|auto，默认 auto）：
    api   ：DashScope text-embedding-v3（OpenAI 兼容 /embeddings，默认 1024 维）
            —— 有 LLM_API_KEY 时运行时用它（真实模型）
    local ：确定性哈希词袋（CJK 二元组 + ASCII 词），零依赖零网络
            —— 测试与离线兜底；与 api 的向量空间不互通

⚠️ 同一条洞察的 embedding 必须与检索时的 embedder 一致；
   切换 embedder 后应重置图谱（ops.db 重建会用当前 embedder 重新灌种子）。
维度固定 1024 —— 冻结 DDL 的 vector(1024)。
"""

from __future__ import annotations

import math
import os
import re
from collections.abc import Callable

DIM = 1024
DEFAULT_EMBED_MODEL = "text-embedding-v3"

EmbedFn = Callable[[str], list[float]]

_CJK = re.compile(r"[一-鿿]")
_WORD = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    """CJK 连续段切成二元组（单字保留原字），ASCII 切词。"""
    text = text.lower()
    tokens: list[str] = []

    def flush(buf: str) -> None:
        if not buf:
            return
        if len(buf) == 1:
            tokens.append(buf)
        else:
            tokens.extend(buf[i : i + 2] for i in range(len(buf) - 1))

    buf = ""
    for ch in text:
        if _CJK.match(ch):
            buf += ch
        else:
            flush(buf)
            buf = ""
    flush(buf)
    tokens.extend(_WORD.findall(text))
    return tokens


def local_embed(text: str) -> list[float]:
    """确定性哈希词袋向量（l2 归一化）。同义词不聚拢 —— 它只保证可复现。"""
    vec = [0.0] * DIM
    for tok in _tokenize(text):
        h = int.from_bytes(tok.encode("utf-8"), "little")
        vec[h % DIM] += 1.0
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        vec[0] = 1.0
        return vec
    return [v / norm for v in vec]


def api_embed(text: str) -> list[float]:
    from wagent_backend.llm import client as llm_client

    model = os.environ.get("WAGENT_EMBED_MODEL") or DEFAULT_EMBED_MODEL
    resp = llm_client._client().embeddings.create(model=model, input=[text])
    vec = list(resp.data[0].embedding)
    if len(vec) != DIM:
        raise RuntimeError(f"embedding 维度 {len(vec)} ≠ 冻结契约 {DIM}（模型 {model}）")
    return vec


def get_embedder() -> EmbedFn:
    mode = (os.environ.get("WAGENT_EMBEDDING") or "auto").lower()
    from wagent_backend.llm import client as llm_client

    if mode == "local":
        return local_embed
    if mode == "api":
        return api_embed
    return api_embed if llm_client.is_configured() else local_embed


def embedder_name(fn: EmbedFn) -> str:
    return "local" if fn is local_embed else "api"


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
