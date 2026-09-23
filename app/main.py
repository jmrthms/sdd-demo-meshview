"""MeshView — a small 3D model viewer.

    make run      # http://127.0.0.1:8000  (the viewer)   /docs (the API)
    make test
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routes import models

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="MeshView", version="1.0.0",
              description="Upload a 3D model, look at it. The starting point for the live specification demo.")
app.include_router(models.router)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
    code = {404: "not_found", 413: "too_large", 415: "unsupported_format", 422: "invalid"}.get(exc.status_code, "error")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail, "code": code, "line": None})


@app.get("/", include_in_schema=False)
def viewer() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/formats", tags=["meta"])
def formats() -> dict[str, list[str]]:
    """The formats the upload accepts. The viewer's format tag reads this."""
    from app.mesh import PARSERS
    return {"formats": sorted(PARSERS)}


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
