"""OBJ support — one test per acceptance criterion in specs/obj-support.md.

Written from the criteria before the handoff, by the spec's author. A red test points at a
sentence in that document.
"""
from __future__ import annotations
from tests.conftest import upload


def test_ac1_triangle_faces_upload(client, samples):
    r = upload(client, samples / "cube-tris.obj")
    assert r.status_code == 201, r.text
    b = r.json(); assert b["format"] == "obj" and b["triangle_count"] == 12


def test_ac2_polygon_faces_are_triangulated(client, samples):
    b = upload(client, samples / "cube.obj").json()
    assert b["triangle_count"] == 12, "six quads must become twelve triangles"


def test_ac3_negative_indices_resolve(client, samples):
    pos = upload(client, samples / "cube.obj").json()
    neg = upload(client, samples / "cube-negative.obj").json()
    assert neg["triangle_count"] == pos["triangle_count"] == 12
    assert neg["bbox"] == pos["bbox"]


def test_ac4_index_out_of_range_is_422_with_line(client, samples):
    r = upload(client, samples / "index-out-of-range.obj")
    assert r.status_code == 422 and r.json()["code"] == "parse_error"
    assert r.json()["line"] == 4
    assert client.get("/models").json()["total"] == 0, "nothing may be stored"


def test_ac5_bad_line_rejects_whole_file_with_line(client, samples):
    r = upload(client, samples / "broken.obj")
    assert r.status_code == 422 and r.json()["code"] == "parse_error"
    assert r.json()["line"] == 5
    assert client.get("/models").json()["total"] == 0, "partial geometry must not be accepted"


def test_ac6_no_faces_is_422(client, samples):
    r = upload(client, samples / "points-only.obj")
    assert r.status_code == 422 and r.json()["code"] == "parse_error"
    assert client.get("/models").json()["total"] == 0


def test_ac7_material_and_group_lines_are_ignored(client, samples):
    b = upload(client, samples / "cube-with-material.obj")
    assert b.status_code == 201 and b.json()["triangle_count"] == 12


def test_ac8_size_limit_is_shared_with_stl(client, samples, monkeypatch):
    from app.routes import models as routes
    monkeypatch.setattr(routes, "MAX_UPLOAD_BYTES", 100)
    r = upload(client, samples / "torus.stl", as_name="big.obj")
    assert r.status_code == 413 and r.json()["code"] == "too_large"


def test_ac9_extension_case_is_ignored(client, samples):
    assert upload(client, samples / "cube.obj", as_name="CUBE.OBJ").status_code == 201


def test_ac10_mesh_shape_matches_stl_and_formats_lists_obj(client, samples):
    mid = upload(client, samples / "cube.obj").json()["id"]
    m = client.get(f"/models/{mid}/mesh").json()
    assert len(m["vertices"]) == 8 and len(m["faces"]) == 12 and all(len(f) == 3 for f in m["faces"])
    assert "bbox" in m
    assert "obj" in client.get("/formats").json()["formats"]
