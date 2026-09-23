"""Upload, list, inspect, and fetch the mesh for a model.

Read this file before adding a format or an endpoint: the upload path is the pattern.
"""

from __future__ import annotations

import sqlite3
from pathlib import PurePosixPath

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from app import mesh as meshlib
from app import store
from app.models import MeshPayload, ModelList, ModelSummary

router = APIRouter(prefix="/models", tags=["models"])

MAX_UPLOAD_BYTES = 25 * 1024 * 1024   # the number decided in the 2026-09-18 meeting


def _error(status: int, code: str, detail: str, line: int | None = None) -> JSONResponse:
    return JSONResponse(status_code=status, content={"detail": detail, "code": code, "line": line})


@router.post("", response_model=ModelSummary, status_code=201)
async def upload_model(request: Request, name: str = Query(..., min_length=1),
                       db: sqlite3.Connection = Depends(store.get_db)):
    """Accept a mesh file as the raw request body (``?name=`` carries the filename).

    Parse it, keep it. **Nothing is stored if parsing fails.** The format is the file's
    extension, lower-cased; there is no format picker.
    """
    name = PurePosixPath(name).name
    fmt = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if fmt not in meshlib.PARSERS:
        return _error(415, "unsupported_format",
                      f"{fmt or 'no extension'} is not supported; supported: {sorted(meshlib.PARSERS)}")
    data = await request.body()
    if not data:
        return _error(422, "empty_file", "the uploaded file is empty")
    if len(data) > MAX_UPLOAD_BYTES:
        return _error(413, "too_large", f"file is {len(data)} bytes; the limit is {MAX_UPLOAD_BYTES}")
    try:
        m = meshlib.parse(data, fmt)
    except meshlib.ParseError as exc:
        return _error(422, "parse_error", str(exc), exc.line)
    row = store.insert(db, name=name, fmt=fmt, triangle_count=m.triangle_count,
                       bbox=m.bbox(), size_bytes=len(data))
    store.save_file(row["id"], fmt, data)
    return ModelSummary(**row)


@router.get("", response_model=ModelList)
def list_models(db: sqlite3.Connection = Depends(store.get_db)) -> ModelList:
    rows = db.execute("SELECT * FROM models ORDER BY uploaded_at DESC").fetchall()
    items = [ModelSummary(**store.to_dict(r)) for r in rows]
    return ModelList(items=items, total=len(items))


@router.get("/{model_id}", response_model=ModelSummary)
def get_model(model_id: str, db: sqlite3.Connection = Depends(store.get_db)) -> ModelSummary:
    row = db.execute("SELECT * FROM models WHERE id = ?", (model_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"no model with id {model_id}")
    return ModelSummary(**store.to_dict(row))


@router.get("/{model_id}/mesh", response_model=MeshPayload)
def get_mesh(model_id: str, db: sqlite3.Connection = Depends(store.get_db)) -> MeshPayload:
    """Re-parse the stored file and hand the viewer triangles. Same shape for every format."""
    row = db.execute("SELECT * FROM models WHERE id = ?", (model_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"no model with id {model_id}")
    path = store.file_path(row["id"], row["format"])
    m = meshlib.parse(path.read_bytes(), row["format"])
    return MeshPayload(**m.as_dict())
