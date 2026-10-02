"""聊天路由 —— LLM + kg_* 工具的 function-calling 问答。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from wagent_backend.agent import loop as agent_loop
from wagent_backend.web.deps import get_complete_msg

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[dict[str, str]] = Field(
        default_factory=list,
        description="最近的对话记录 [{role: user|assistant, content}]，只保留几轮即可",
    )


@router.post("")
def chat(req: ChatRequest, complete=Depends(get_complete_msg)) -> dict:
    result = agent_loop.run(complete, req.message, req.history)
    return result.model_dump()
