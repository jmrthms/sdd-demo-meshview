"""The one shape every format is parsed into, and the STL parser.

A mesh is vertices (floats, in file units) and triangular faces (0-based vertex
indices). Anything a format carries beyond that — normals, colours, materials —
is ignored on purpose: this is a viewer, not a CAD kernel.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field


class ParseError(ValueError):
    """The file could not be read as a mesh. ``line`` is 1-based when known."""

    def __init__(self, message: str, line: int | None = None) -> None:
        super().__init__(message)
        self.line = line


@dataclass
class Mesh:
    vertices: list[list[float]] = field(default_factory=list)
    faces: list[list[int]] = field(default_factory=list)

    @property
    def triangle_count(self) -> int:
        return len(self.faces)

    def bbox(self) -> dict[str, list[float]]:
        if not self.vertices:
            return {"min": [0.0, 0.0, 0.0], "max": [0.0, 0.0, 0.0]}
        xs, ys, zs = zip(*self.vertices)
        return {"min": [min(xs), min(ys), min(zs)], "max": [max(xs), max(ys), max(zs)]}

    def as_dict(self) -> dict:
        return {"vertices": self.vertices, "faces": self.faces,
                "triangle_count": self.triangle_count, "bbox": self.bbox()}


# ------------------------------------------------------------------ STL

def _is_binary_stl(data: bytes) -> bool:
    if len(data) < 84:
        return False
    (count,) = struct.unpack_from("<I", data, 80)
    return len(data) == 84 + 50 * count


def parse_stl(data: bytes) -> Mesh:
    """Binary or ASCII STL. Vertices are de-duplicated so the viewer gets a real index."""
    if _is_binary_stl(data):
        return _parse_binary_stl(data)
    if data.lstrip().lower().startswith(b"solid"):
        return _parse_ascii_stl(data)
    raise ParseError("not an STL file: neither a valid binary header nor an ASCII 'solid'")


def _parse_binary_stl(data: bytes) -> Mesh:
    (count,) = struct.unpack_from("<I", data, 80)
    if count == 0:
        raise ParseError("STL file contains no triangles")
    index: dict[tuple[float, float, float], int] = {}
    mesh = Mesh()
    off = 84
    for _ in range(count):
        vals = struct.unpack_from("<12f", data, off)
        off += 50
        tri = []
        for i in (3, 6, 9):
            v = (vals[i], vals[i + 1], vals[i + 2])
            if v not in index:
                index[v] = len(mesh.vertices)
                mesh.vertices.append(list(v))
            tri.append(index[v])
        mesh.faces.append(tri)
    return mesh


def _parse_ascii_stl(data: bytes) -> Mesh:
    index: dict[tuple[float, float, float], int] = {}
    mesh = Mesh()
    tri: list[int] = []
    for n, raw in enumerate(data.decode("utf-8", errors="replace").splitlines(), start=1):
        parts = raw.split()
        if not parts or parts[0] != "vertex":
            continue
        try:
            v = (float(parts[1]), float(parts[2]), float(parts[3]))
        except (IndexError, ValueError) as exc:
            raise ParseError(f"bad vertex: {raw.strip()!r}", line=n) from exc
        if v not in index:
            index[v] = len(mesh.vertices)
            mesh.vertices.append(list(v))
        tri.append(index[v])
        if len(tri) == 3:
            mesh.faces.append(tri)
            tri = []
    if tri:
        raise ParseError("facet with fewer than three vertices at end of file")
    if not mesh.faces:
        raise ParseError("STL file contains no triangles")
    return mesh


# ------------------------------------------------------------------ OBJ

def parse_obj(data: bytes) -> Mesh:
    """Wavefront OBJ, geometry only — see specs/obj-support.md.

    Reads ``v`` and ``f``. Everything else (materials, groups, normals, texture coordinates)
    is skipped without error. Polygon faces are fan-triangulated. Indices are 1-based;
    negative indices are relative to the vertices defined so far. Any malformed line
    rejects the whole file with its line number.
    """
    mesh = Mesh()
    for n, raw in enumerate(data.decode("utf-8", errors="replace").splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        kw, args = parts[0], parts[1:]
        if kw == "v":
            try:
                mesh.vertices.append([float(args[0]), float(args[1]), float(args[2])])
            except (IndexError, ValueError) as exc:
                raise ParseError(f"bad vertex: {raw.strip()!r}", line=n) from exc
        elif kw == "f":
            if len(args) < 3:
                raise ParseError(f"face with fewer than three vertices: {raw.strip()!r}", line=n)
            idx = []
            for tok in args:
                try:
                    i = int(tok.split("/", 1)[0])
                except ValueError as exc:
                    raise ParseError(f"bad face index {tok!r}", line=n) from exc
                if i == 0:
                    raise ParseError("face index 0 is not allowed (indices are 1-based)", line=n)
                j = len(mesh.vertices) + i if i < 0 else i - 1
                if not 0 <= j < len(mesh.vertices):
                    raise ParseError(f"face references vertex {i} but only {len(mesh.vertices)} are defined", line=n)
                idx.append(j)
            for k in range(1, len(idx) - 1):          # fan triangulation
                mesh.faces.append([idx[0], idx[k], idx[k + 1]])
        # vt, vn, vp, mtllib, usemtl, o, g, s, l, p and anything unknown: ignored on purpose
    if not mesh.faces:
        raise ParseError("OBJ file contains no faces")
    return mesh


PARSERS = {"stl": parse_stl, "obj": parse_obj}


def parse(data: bytes, fmt: str) -> Mesh:
    """Dispatch on the file's format (lower-case extension, no dot)."""
    try:
        parser = PARSERS[fmt]
    except KeyError:
        raise ParseError(f"unsupported format {fmt!r}; supported: {sorted(PARSERS)}") from None
    return parser(data)
