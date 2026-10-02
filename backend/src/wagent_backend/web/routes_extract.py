"""抽取路由 —— 工单文本/截图 → LLM 三元组 → 实时入图（图谱自己长大）。"""

from __future__ import annotations

import base64

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from wagent_backend.graphRAG.extractor import TripleExtractor
from wagent_backend.web.deps import get_complete_text

router = APIRouter(prefix="/api/extract", tags=["extract"])


@router.post("")
async def extract(
    text: str | None = Form(default=None),
    image: UploadFile | None = File(default=None),
    complete=Depends(get_complete_text),
) -> dict:
    """粘贴工单文本和/或上传截图，LLM 抽取三元组合并进图谱，返回生长报告。"""
    if not (text and text.strip()) and image is None:
        raise HTTPException(status_code=400, detail="text 与 image 至少提供一个")

    image_b64: str | None = None
    image_mime = "image/png"
    if image is not None:
        raw = await image.read()
        if raw:
            image_b64 = base64.b64encode(raw).decode("ascii")
            image_mime = image.content_type or "image/png"

    extractor = TripleExtractor(complete)
    try:
        triples = extractor.extract(
            text=(text or "").strip() or None,
            image_b64=image_b64,
            image_mime=image_mime,
        )
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"LLM 返回无法解析：{e}") from e

    from wagent_backend.graphRAG.store import get_store

    report = extractor.apply(get_store(), triples)
    return report.model_dump()
