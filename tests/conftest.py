"""``client`` = a TestClient on a throwaway database and upload directory."""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from app import store
from app.main import app
from pathlib import Path

SAMPLES = Path(__file__).resolve().parent.parent / "data" / "samples"

@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(store, "UPLOAD_DIR", tmp_path / "uploads")
    store.reset()
    with TestClient(app) as c:
        yield c
    store.reset()

@pytest.fixture()
def samples():
    return SAMPLES

def upload(client, path: Path, as_name: str | None = None):
    """POST one sample file the way the viewer does: raw body, filename in the query string."""
    return client.post("/models", params={"name": as_name or path.name}, content=path.read_bytes())
