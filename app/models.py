"""Every shape that crosses the API boundary."""

from __future__ import annotations

from pydantic import BaseModel


class BBox(BaseModel):
    min: list[float]
    max: list[float]


class ModelSummary(BaseModel):
    id: str
    name: str
    format: str
    triangle_count: int
    bbox: BBox
    size_bytes: int
    uploaded_at: float


class ModelList(BaseModel):
    items: list[ModelSummary]
    total: int


class MeshPayload(BaseModel):
    """What the viewer draws. Vertices in file units; faces are 0-based triangles."""

    vertices: list[list[float]]
    faces: list[list[int]]
    triangle_count: int
    bbox: BBox


class ErrorBody(BaseModel):
    """The one error shape. ``line`` is set when the parser knows where it stopped."""

    detail: str
    code: str
    line: int | None = None
