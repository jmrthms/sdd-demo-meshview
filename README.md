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

## Replay the live build yourself

Everything shown in class runs from `demo/start`:

```bash
git clone https://github.com/jmrthms/sdd-demo-meshview && cd sdd-demo-meshview
git checkout demo/start && make setup && make test     # 13 pass; the ten OBJ criterion tests are red
```

1. In an agent session, ask for the draft: *Draft a feature specification for OBJ support from
   `docs/meetings/2026-09-18-feature-review.md`, using the `how-to-write-a-spec` skill. Write it to
   `specs/obj-support.md`.* Read it beside `demo/spec-v1.md` and `demo/REVIEW-NOTES.md` — find what
   the room decided that the draft is silent about.
2. Approve the corrected version: `cp demo/spec-v2.md specs/obj-support.md`.
3. In a **fresh** session with no history: *Implement the feature specified in `specs/obj-support.md`.
   Follow the conventions already in the repository.* Do not answer questions or correct it.
4. `make test` — the ten criterion tests were written from the specification before step 3, not by
   the session that built the code.
5. `bash demo/run-round-1.sh` — what version one's criteria produced against the same tests.

`demo/README.md` is the timed runbook for the session; `demo/BLIND-HANDOFF-REPORT.md` is what step 3
reported when it was run blind on Sep 23.
