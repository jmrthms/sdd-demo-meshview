"""Generate data/samples/*. Deterministic; run `make seed` to rebuild."""
from __future__ import annotations
import math, struct
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "data" / "samples"

def binary_stl(tris, path):
    buf = bytearray(b"MeshView sample".ljust(80, b"\0")) + struct.pack("<I", len(tris))
    for a, b, c in tris:
        buf += struct.pack("<12f", 0, 0, 0, *a, *b, *c) + b"\0\0"
    path.write_bytes(buf)

def ascii_stl(tris, path, name="sample"):
    lines = [f"solid {name}"]
    for a, b, c in tris:
        lines += ["  facet normal 0 0 0", "    outer loop"] + [f"      vertex {v[0]} {v[1]} {v[2]}" for v in (a, b, c)] + ["    endloop", "  endfacet"]
    lines.append(f"endsolid {name}"); path.write_text("\n".join(lines) + "\n")

def cube(s=1.0):
    p = [(0,0,0),(s,0,0),(s,s,0),(0,s,0),(0,0,s),(s,0,s),(s,s,s),(0,s,s)]
    quads = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    tris = []
    for a,b,c,d in quads: tris += [(p[a],p[b],p[c]),(p[a],p[c],p[d])]
    return p, quads, tris

def torus(R=2.0, r=0.6, nu=48, nv=24):
    pts = [[( (R + r*math.cos(2*math.pi*j/nv)) * math.cos(2*math.pi*i/nu),
              (R + r*math.cos(2*math.pi*j/nv)) * math.sin(2*math.pi*i/nu),
               r*math.sin(2*math.pi*j/nv)) for j in range(nv)] for i in range(nu)]
    tris = []
    for i in range(nu):
        for j in range(nv):
            a,b,c,d = pts[i][j], pts[(i+1)%nu][j], pts[(i+1)%nu][(j+1)%nv], pts[i][(j+1)%nv]
            tris += [(a,b,c),(a,c,d)]
    return tris

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    p, quads, tris = cube()
    binary_stl(tris, OUT / "cube.stl")                 # 12 triangles
    ascii_stl(tris, OUT / "cube-ascii.stl", "cube")
    binary_stl(torus(), OUT / "torus.stl")             # 2304 triangles
    (OUT / "empty.stl").write_bytes(b"MeshView empty".ljust(80, b"\0") + struct.pack("<I", 0))
    (OUT / "not-a-mesh.stl").write_bytes(b"hello, this is a text file pretending to be geometry\n")
    # --- OBJ fixtures, for the feature built live. The awkward ones are deliberate. ---
    v = "\n".join(f"v {x} {y} {z}" for x,y,z in p)
    (OUT / "cube.obj").write_text("# a cube, quad faces — must be triangulated\n" + v + "\n" +
        "\n".join(f"f {a+1} {b+1} {c+1} {d+1}" for a,b,c,d in quads) + "\n")
    (OUT / "cube-tris.obj").write_text("# same cube, already triangles, with texture/normal slots in the index\n" + v +
        "\nvn 0 0 1\n" + "\n".join(f"f {a[0]+1}//1 {a[1]+1}//1 {a[2]+1}//1" for a in
        [(0,3,2),(0,2,1),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]) + "\n")
    (OUT / "cube-negative.obj").write_text("# relative (negative) indices — legal OBJ, easy to get wrong\n" + v + "\n" +
        "\n".join(f"f {a-8} {b-8} {c-8} {d-8}" for a,b,c,d in quads) + "\n")
    (OUT / "cube-with-material.obj").write_text("mtllib cube.mtl\no cube\nusemtl steel\ns off\n" + v + "\n" +
        "\n".join(f"f {a+1} {b+1} {c+1} {d+1}" for a,b,c,d in quads) + "\n")
    (OUT / "points-only.obj").write_text("# vertices but no faces\n" + v + "\n")
    (OUT / "broken.obj").write_text("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\nv 0 0 oops\nf 1 2 4\n")   # bad vertex on line 5
    (OUT / "index-out-of-range.obj").write_text("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 9\n")            # face refs vertex 9 of 3
    print("wrote", sorted(x.name for x in OUT.iterdir()))

if __name__ == "__main__":
    main()
