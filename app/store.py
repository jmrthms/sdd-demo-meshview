"""Where uploaded models live: a SQLite index plus the original file on disk."""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "meshview.db"
UPLOAD_DIR = ROOT / "data" / "uploads"

SCHEMA = """
CREATE TABLE IF NOT EXISTS models (
    id             TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    format         TEXT NOT NULL,
    triangle_count INTEGER NOT NULL,
    bbox           TEXT NOT NULL,
    size_bytes     INTEGER NOT NULL,
    uploaded_at    REAL NOT NULL
);
"""

_conn: sqlite3.Connection | None = None


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    """Resolved at call time so tests can point DB_PATH somewhere temporary."""
    conn = sqlite3.connect(path or DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def get_db() -> Iterator[sqlite3.Connection]:
    global _conn
    if _conn is None:
        _conn = connect(DB_PATH)
    yield _conn


def reset() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None
    p = Path(DB_PATH)
    if p.exists():
        p.unlink()


def save_file(model_id: str, fmt: str, data: bytes) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    path = UPLOAD_DIR / f"{model_id}.{fmt}"
    path.write_bytes(data)
    return path


def file_path(model_id: str, fmt: str) -> Path:
    return UPLOAD_DIR / f"{model_id}.{fmt}"


def insert(db: sqlite3.Connection, *, name: str, fmt: str, triangle_count: int,
           bbox: dict[str, Any], size_bytes: int) -> dict[str, Any]:
    model_id = uuid.uuid4().hex[:12]
    row = {"id": model_id, "name": name, "format": fmt, "triangle_count": triangle_count,
           "bbox": bbox, "size_bytes": size_bytes, "uploaded_at": time.time()}
    db.execute("INSERT INTO models VALUES (?,?,?,?,?,?,?)",
               (model_id, name, fmt, triangle_count, json.dumps(bbox), size_bytes, row["uploaded_at"]))
    db.commit()
    return row


def to_dict(r: sqlite3.Row) -> dict[str, Any]:
    d = dict(r)
    d["bbox"] = json.loads(d["bbox"])
    return d
