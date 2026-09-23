"""The baseline: STL upload, listing, and the mesh the viewer draws."""
from __future__ import annotations
from tests.conftest import upload

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}

def test_viewer_page_serves(client):
    r = client.get("/"); assert r.status_code == 200 and "MeshView" in r.text

def test_upload_binary_stl(client, samples):
    r = upload(client, samples / "cube.stl")
    assert r.status_code == 201, r.text
    b = r.json(); assert b["format"] == "stl" and b["triangle_count"] == 12
    assert b["bbox"] == {"min": [0, 0, 0], "max": [1, 1, 1]}

def test_upload_ascii_stl(client, samples):
    b = upload(client, samples / "cube-ascii.stl").json(); assert b["triangle_count"] == 12

def test_large_stl(client, samples):
    b = upload(client, samples / "torus.stl").json(); assert b["triangle_count"] == 2304

def test_list_after_uploads(client, samples):
    upload(client, samples / "cube.stl"); upload(client, samples / "torus.stl")
    b = client.get("/models").json(); assert b["total"] == 2 and len(b["items"]) == 2

def test_mesh_endpoint_returns_triangles(client, samples):
    mid = upload(client, samples / "cube.stl").json()["id"]
    m = client.get(f"/models/{mid}/mesh").json()
    assert len(m["vertices"]) == 8 and len(m["faces"]) == 12 and all(len(f) == 3 for f in m["faces"])

def test_unknown_id_is_404(client):
    assert client.get("/models/nope").status_code == 404

def test_unsupported_extension_is_415(client, samples):
    r = upload(client, samples / "cube.stl", as_name="cube.step")
    assert r.status_code == 415 and r.json()["code"] == "unsupported_format"

def test_empty_file_is_422_and_nothing_stored(client, samples):
    r = upload(client, samples / "empty.stl")
    assert r.status_code == 422 and r.json()["code"] == "parse_error"
    assert client.get("/models").json()["total"] == 0

def test_garbage_is_422(client, samples):
    r = upload(client, samples / "not-a-mesh.stl"); assert r.status_code == 422

def test_over_limit_is_413(client, samples, monkeypatch):
    from app.routes import models as routes
    monkeypatch.setattr(routes, "MAX_UPLOAD_BYTES", 100)
    r = upload(client, samples / "torus.stl"); assert r.status_code == 413 and r.json()["code"] == "too_large"


def test_formats_lists_what_the_registry_has(client):
    assert "stl" in client.get("/formats").json()["formats"]
