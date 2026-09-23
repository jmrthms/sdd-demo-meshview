---
name: api-conventions
description: >
  Use whenever adding a file format, an endpoint, or a response shape to this repository.
  Names the parser registry, the upload path, the error contract, and the file layout.
---

# API conventions

## Layout
- Parsers live in `app/mesh.py`. **A new format is a parser function registered in `PARSERS`** —
  `parse(data, fmt)` dispatches on the lower-case extension. Nothing else in the app needs to know
  the format exists: the upload route, the list, and the mesh endpoint all go through the registry.
- Every parser returns a `Mesh`: `vertices` (floats, file units) and `faces` (0-based triangles).
  Non-triangular faces are triangulated by the parser, never by the viewer.
- Routes live in `app/routes/`. Shapes live in `app/models.py`. Nothing crosses the boundary as a bare dict.
- The viewer is `app/static/index.html`. It draws whatever `/models/{id}/mesh` returns; it does not parse.

## The error contract
Every 4xx is `ErrorBody` — `{detail, code, line}`:
- `415 unsupported_format` — extension not in `PARSERS`
- `422 empty_file` — zero bytes
- `413 too_large` — over `MAX_UPLOAD_BYTES`
- `422 parse_error` — the parser raised `ParseError`; `line` is set when it knows the line
- `404 not_found`

A parser signals failure by raising `ParseError(message, line=...)`. **On any failure nothing is stored** —
no row, no file.

## Things not to do
- Do not parse in the viewer. Do not add a format picker; the extension decides.
- Do not return partial geometry from a file that failed part-way. Reject it.
- Do not add a new error shape.
