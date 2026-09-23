# MeshView — the live-demo repository

A small 3D model viewer: upload a mesh, look at it. Built for the Week 5 guest session's live build,
where a recorded product meeting becomes a specification becomes a working feature.

```bash
make setup && make test      # 23 tests
make run                     # http://127.0.0.1:8000 — the viewer;  /docs — the API
```

## What is here
```
app/mesh.py            the Mesh shape and the parsers — a new format is a function registered in PARSERS
app/routes/models.py   upload (raw body, ?name=), list, one model, its mesh
app/static/index.html  the viewer (Three.js); draws whatever /models/{id}/mesh returns
data/samples/          generated STL and OBJ files, including the awkward ones — see tests skill
docs/meetings/         the recorded feature-review meeting the demo starts from
specs/                 one specification per feature
demo/                  the live-demo kit: first draft, review notes, approved spec, failure exhibit
.claude/skills/        how-to-write-a-spec · api-conventions · testing  (AGENTS.md carries the same rules)
```

## Branches
- `main` — OBJ support implemented from `specs/obj-support.md`, 23 tests green.
- `demo/start` — the repository as it is *before* the live build: STL only, the ten OBJ criterion
  tests present and red. The live session runs here. `git checkout main` is the fallback.

The starter repository students use for the assignment is a different repo:
<https://github.com/jmrthms/sdd-starter-repo>.
