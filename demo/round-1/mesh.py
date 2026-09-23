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
    """ROUND 1 — a faithful implementation of demo/spec-v1.md. Nothing here is careless.

      v1 AC2  "display correctly"           -> one triangle per face, whatever its size
      v1 AC3  "rejected with an error"      -> ParseError, no line number
      v1      (silent on negative indices)  -> treated as out of range
      v1      (silent on no-face files)     -> an empty mesh is a mesh
    """
    mesh = Mesh()
    for raw in data.decode("utf-8", errors="replace").splitlines():
        parts = raw.split("#", 1)[0].split()
        if not parts:
            continue
        if parts[0] == "v":
            try:
                mesh.vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            except (IndexError, ValueError):
                raise ParseError("invalid OBJ file")
        elif parts[0] == "f":
            idx = []
            for tok in parts[1:4]:
                i = int(tok.split("/", 1)[0]) - 1
                if not 0 <= i < len(mesh.vertices):
                    raise ParseError("invalid OBJ file")
                idx.append(i)
            if len(idx) == 3:
                mesh.faces.append(idx)
    return mesh


PARSERS = {"stl": parse_stl, "obj": parse_obj}


def parse(data: bytes, fmt: str) -> Mesh:
    """Dispatch on the file's format (lower-case extension, no dot)."""
    try:
        parser = PARSERS[fmt]
    except KeyError:
        raise ParseError(f"unsupported format {fmt!r}; supported: {sorted(PARSERS)}") from None
    return parser(data)
