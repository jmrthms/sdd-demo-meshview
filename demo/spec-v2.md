# Feature Specification — OBJ file support

**Status:** approved · **Source:** `docs/meetings/2026-09-18-feature-review.md`
**Author:** drafted by the agent from the recording, revised in review · **Reviewers:** the room, 7:24

## 1. Intent

People keep uploading OBJ files and the viewer says unsupported. OBJ is the second most common
mesh format after STL, and most modelling tools export it. Accept it, so that from the user's point
of view an OBJ file works exactly like an STL file does: upload it, it appears in the list, click it,
see it.

## 2. User stories

- As a user with an OBJ file, I want to upload it and see it, so that I do not have to convert it.
- As a user with a broken OBJ file, I want to be told which line is wrong, so that I can fix it.

## 3. Acceptance criteria

1. Given a well-formed `.obj` whose faces are triangles, when it is uploaded, then the response is
   HTTP 201 with `format` `"obj"` and `triangle_count` equal to the number of faces.
2. Given faces with more than three vertices (quads or larger polygons), when the file is uploaded,
   then each face is fan-triangulated and `triangle_count` is the count **after** triangulation.
3. Given faces that use relative (negative) indices, when the file is uploaded, then each index is
   resolved against the vertices defined so far, and the result is identical to the same geometry
   written with positive indices.
4. Given a face that references a vertex index outside the range defined, when the file is uploaded,
   then the whole file is rejected with HTTP 422, `code` `"parse_error"`, and `line` set to the
   offending line; nothing is stored.
5. Given a malformed line anywhere in the file (for example a vertex with a non-numeric coordinate),
   when the file is uploaded, then the whole file is rejected with HTTP 422, `code` `"parse_error"`,
   and `line` set; nothing is stored. Partial geometry is never accepted.
6. Given a file with vertices but no faces, when it is uploaded, then it is rejected with HTTP 422
   and `code` `"parse_error"`; nothing is stored. A file with no `v` or `f` records at all (an STL
   renamed `.obj`, say) is the same case.
7. Given `mtllib`, `usemtl`, `o`, `g`, `s`, `vn`, `vt` or any other non-geometry line, when the
   file is uploaded, then those lines are ignored and the file loads normally.
8. Given a file larger than 25 MB, when it is uploaded, then it is rejected with HTTP 413 and
   `code` `"too_large"` — the same limit and the same error as STL.
9. Given an extension in any letter case (`.obj`, `.OBJ`, `.Obj`), when the file is uploaded, then
   it is accepted as OBJ.
10. Given an uploaded OBJ, when `GET /models/{id}/mesh` is called, then the payload has exactly the
    shape it has for STL — `vertices`, triangular `faces`, `bbox` — and `GET /formats` lists `"obj"`.

## 4. Scope and non-goals

**In scope:** the `v` and `f` records of the OBJ format; polygon faces; relative indices; the error
behaviour above; the format tag in the viewer updating from `stl` to `obj stl`, the order
`GET /formats` returns.

**Explicitly out of scope this cycle:** materials and textures (`mtllib`, `usemtl`, `.mtl` files);
groups and objects (`o`, `g`); smoothing groups (`s`); normals and texture coordinates as data
(`vn`, `vt` are skipped, not used); free-form curves and surfaces; a format picker in the UI;
units (see §8); the wireframe toggle and info panel (separate spec); side-by-side comparison
(not this product).

## 5. Interfaces and contracts

No new endpoints. `POST /models?name=<file>.obj` with the file as the body, exactly as for STL.

```
201 { "id": "…", "name": "cube.obj", "format": "obj", "triangle_count": 12,
      "bbox": {"min":[0,0,0], "max":[1,1,1]}, "size_bytes": 194, "uploaded_at": … }

422 { "detail": "bad vertex: 'v 0 0 oops'", "code": "parse_error", "line": 5 }
422 { "detail": "face references vertex 9 but only 3 are defined", "code": "parse_error", "line": 4 }
422 { "detail": "OBJ file contains no faces", "code": "parse_error", "line": null }
413 { "detail": "file is … bytes; the limit is 26214400", "code": "too_large", "line": null }
```

`GET /formats` → `{"formats": ["obj", "stl"]}`. `GET /models/{id}/mesh` → unchanged shape.

## 6. Constraints

- **Registry, not routes.** OBJ is a parser function in `app/mesh.py` registered in `PARSERS`.
  The upload route, the list, the mesh endpoint and the viewer's format tag pick it up from there.
  No route changes.
- **Triangulation happens in the parser.** The viewer only ever receives triangles. A polygon with
  n vertices becomes n − 2 triangles by fan: (v0, v1, v2), (v0, v2, v3), …
- **Face index tokens** may be `i`, `i/t`, `i/t/n` or `i//n`; only `i` is used. Indices are 1-based;
  negative means relative to the vertices defined so far at that line.
- **Failure means nothing stored.** A `ParseError` at any line rejects the whole file; no row, no file.
- **Size limit** is `MAX_UPLOAD_BYTES` (25 MB), shared with STL. Not a new constant.
- **Error body** is `{detail, code, line}`; `line` is 1-based and set whenever the parser knows it.
- **Viewer:** no new controls. The format tag reads `GET /formats`. The upload button stays primary.
- **Units:** shown as file units, unlabelled, as for STL.

## 7. Test plan

One test per criterion in `tests/test_obj_support.py`, named `test_ac<N>_…`, using the fixtures in
`data/samples/`. Written by the spec's author from the criteria, before the handoff.

| | sample | asserts |
|---|---|---|
| AC1 | `cube-tris.obj` | 201, format obj, 12 triangles |
| AC2 | `cube.obj` (six quads) | 12 triangles |
| AC3 | `cube-negative.obj` | same count and bbox as `cube.obj` |
| AC4 | `index-out-of-range.obj` | 422, parse_error, line 4, list stays empty |
| AC5 | `broken.obj` | 422, parse_error, line 5, list stays empty |
| AC6 | `points-only.obj` | 422, parse_error, list stays empty |
| AC7 | `cube-with-material.obj` | 201, 12 triangles |
| AC8 | `torus.stl` bytes renamed `.obj` with the limit patched to 100 | 413 |
| AC9 | `cube.obj` as `CUBE.OBJ` | 201 |
| AC10 | `cube.obj` then `/mesh`; `/formats` | 8 vertices, 12 triangular faces; `"obj"` listed |

## 8. Open questions

- **Units.** The file has none and the viewer labels none. Design wants a unit in the info panel;
  parked in the meeting. Owner: Marta, for the viewer-pair spec.
- Some exporters write `f` lines before all `v` lines are defined. **Binding for this cycle:** the
  parser resolves indices at the face's line (§6), so such a file is rejected under AC4. Open only
  whether a later cycle should accept it. Nobody in the meeting raised it; ask Dan.
