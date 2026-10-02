"""FastAPI 依赖注入 —— 存储与 LLM 的获取点（测试用 dependency_overrides 替换）。"""

from __future__ import annotations

from collections.abc import Callable

from fastapi import HTTPException

from wagent_backend.agent.loop import CompleteMsg
from wagent_backend.graphRAG.store import GraphStore, get_store
from wagent_backend.llm import client


def get_store_dep() -> GraphStore:
    return get_store()


def get_complete_msg() -> CompleteMsg:
    """聊天循环用的 LLM 调用（qwen3.7-flash）。"""
    try:
        return client.complete_msg
    except client.LLMConfigError as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e


def get_complete_text() -> Callable:
    """抽取器用的 LLM 调用（纯文本回复）。"""
    try:
        return client.complete_text
    except client.LLMConfigError as e:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(e)) from e
