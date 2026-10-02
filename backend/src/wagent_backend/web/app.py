"""FastAPI 应用入口。

    kg-web                     # 默认 http://127.0.0.1:8700
    kg-web --host 0.0.0.0 --port 9000
"""

from __future__ import annotations

import argparse
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from wagent_backend.web import routes_chat, routes_extract, routes_graph, routes_ops

STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(title="wagent-kg", version="0.4.0", description="设备台账知识图谱 + 设施运维 Agent")
    app.include_router(routes_graph.router)
    app.include_router(routes_chat.router)
    app.include_router(routes_extract.router)
    app.include_router(routes_ops.router)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def ops_page() -> FileResponse:
        # 默认首页 = 设施运维 Agent 三栏回放台
        # no-cache = 每次向服务器重校验（带 ETag/Last-Modified），改版后刷新即生效，
        # 避免浏览器拿旧 JS 打新后端（流式接口 404 / 行为不一致）
        return FileResponse(STATIC_DIR / "ops.html",
                            headers={"Cache-Control": "no-cache"})

    @app.get("/ops", include_in_schema=False)
    def ops_alias() -> FileResponse:
        return FileResponse(STATIC_DIR / "ops.html",
                            headers={"Cache-Control": "no-cache"})

    @app.get("/graph", include_in_schema=False)
    def graph_page() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html",
                            headers={"Cache-Control": "no-cache"})

    @app.get("/asset/{asset_id}", include_in_schema=False)
    def asset_page(asset_id: str) -> FileResponse:
        # 设备 360 视图（台账 + 运行参数 + 工单流水）；asset_id 由页面 JS 从路径取
        return FileResponse(STATIC_DIR / "asset.html",
                            headers={"Cache-Control": "no-cache"})

    @app.get("/api/health")
    def health() -> dict:
        return {"ok": True}

    return app


app = create_app()


def main() -> None:
    import uvicorn

    from wagent_backend.llm import client

    parser = argparse.ArgumentParser(prog="kg-web", description="wagent-kg Web 服务")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8700)
    args = parser.parse_args()

    if client.is_configured():
        print(f"✓ 模型已配置：{client.model_name()}")
    else:
        print(
            "⚠ 未配置 LLM_API_KEY —— 图谱浏览可用；AI 聊天/工单抽取请先编辑 "
            "agent/.env 填入 key 后重启"
        )
    # 路由：/ 与 /ops 都是运维 Agent 回放台；/graph 是图谱可视化
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
