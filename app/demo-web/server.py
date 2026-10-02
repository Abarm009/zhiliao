"""HTML 演示站点（本地开发用，不进 Hub bundle）。

修复 N14 / R-P1-4：
  - 修复 httpx.ConnectError / TimeoutException 区分
  - /task/{id} 路由重定向到 /workbench?task=
  - binary 透传：保留 Content-Type / status_code / body bytes
  - 非 JSON 不再统一包装为 {_raw: text}
"""
from __future__ import annotations

import os
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

# 配置：演示端口 + 后端端口
DEMO_PORT = int(os.environ.get("OCTOSENSE_DEMO_PORT", "8090"))
BACKEND_BASE = os.environ.get("OCTOSENSE_BACKEND_BASE", "http://127.0.0.1:8713")

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

app = FastAPI(title="OctoSense Repair · Demo Web (local)", version="0.2.0")


# ─── 反向代理到后端（透传 X-Actor-Id 等头）───
@app.api_route(
    "/api/octosense/v1/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def proxy_octosense(request: Request, path: str):
    body = await request.body()
    target_url = f"{BACKEND_BASE}/api/octosense/v1/{path}"
    if request.url.query:
        target_url += "?" + request.url.query
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in {"host", "content-length"}}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
            )
            ct = r.headers.get("content-type", "")
            # binary 透传：image/*、application/octet-stream 等
            if not ct.startswith("application/json"):
                return Response(
                    content=r.content,
                    status_code=r.status_code,
                    media_type=ct.split(";")[0].strip() or "application/octet-stream",
                    headers={"x-octosense-proxied-from": BACKEND_BASE},
                )
            return JSONResponse(
                content=r.json(),
                status_code=r.status_code,
                headers={"x-octosense-proxied-from": BACKEND_BASE},
            )
    except httpx.ConnectError as e:
        return JSONResponse(
            {"code": "BACKEND_DOWN", "detail": f"无法连接后端 {BACKEND_BASE}: {e!s}"},
            status_code=503,
        )
    except httpx.TimeoutException as e:
        return JSONResponse(
            {"code": "BACKEND_TIMEOUT", "detail": f"后端 {BACKEND_BASE} 超时: {e!s}"},
            status_code=504,
        )
    except httpx.HTTPError as e:
        return JSONResponse(
            {"code": "BACKEND_ERROR", "detail": f"后端 {BACKEND_BASE} 错误: {e!s}"},
            status_code=502,
        )


@app.get("/api/demo/health")
async def demo_health():
    """演示层 + 后端层健康检查。"""
    backend_ok = False
    backend_version = None
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{BACKEND_BASE}/api/octosense/v1/health")
            if r.status_code == 200:
                backend_ok = True
                backend_version = r.json().get("version")
    except Exception:
        pass
    return {
        "demo": {"ok": True, "port": DEMO_PORT},
        "backend": {"ok": backend_ok, "base": BACKEND_BASE, "version": backend_version},
        "demo_users": [
            {"actor": "u-reporter-1", "name": "报修人一", "role": "REPORTER", "projects": ["prj-A"]},
            {"actor": "u-reporter-2", "name": "报修人二", "role": "REPORTER", "projects": ["prj-B"]},
            {"actor": "u-tech-1",     "name": "技工甲（HVAC）", "role": "TECHNICIAN", "projects": ["prj-A"], "skills": "HVAC"},
            {"actor": "u-tech-2",     "name": "技工乙（电气）", "role": "TECHNICIAN", "projects": ["prj-A", "prj-B"], "skills": "ELECTRICAL"},
            {"actor": "u-manager",    "name": "经理丙", "role": "MANAGER", "projects": ["prj-A"]},
        ],
    }


# ─── 静态文件 ──────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(STATIC / "login.html")


@app.get("/workbench", include_in_schema=False)
async def workbench():
    return FileResponse(STATIC / "workbench.html")


@app.get("/task", include_in_schema=False)
async def task_index():
    return RedirectResponse(url="/workbench")


@app.get("/task/{task_id}", include_in_schema=False)
async def task_detail(task_id: str):
    """R-P1-4：原 /task/{id} 不再返 500；重定向到工作台并预选任务。"""
    return RedirectResponse(url=f"/workbench?task={task_id}")


# 挂载 /static 目录（含 css/js）
if (STATIC).is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=DEMO_PORT, log_level="info")
