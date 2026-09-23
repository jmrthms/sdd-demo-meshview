# Live demo — runbook (7:15–7:45)

One feature from a recorded meeting to passing tests. **The capture loop from slide 13, for real:**
a transcript → an agent-drafted spec → the human review → the approved spec → a fresh session
implements → the spec author's tests → the first draft's version fails.

| | |
|---|---|
| `docs/meetings/2026-09-18-feature-review.md` | The recorded meeting. Product, engineering, design, QE decide OBJ support |
| `spec-v1.md` | The agent's first draft, **problems left in** |
| `REVIEW-NOTES.md` | The three things to find on camera, with the transcript timestamps that decided them |
| `spec-v2.md` = `specs/obj-support.md` | Approved |
| `tests/test_obj_support.py` | Ten criterion tests — **yours, written before the handoff** |
| `round-1/mesh.py` + `run-round-1.sh` | The failure exhibit: v1's parser against v2's criteria |

## Verified
```
demo/start before the build     13 passed, 10 red (the criterion tests)
round 2 (from spec-v2)          23 passed
round 1 (from spec-v1)          5 of 10 criteria FAIL
```

## Before class
- [ ] `git checkout demo/start` · `make test` → 13 passed, 10 failed. **Correct.**
- [ ] `make run` → http://127.0.0.1:8000 — upload `data/samples/cube.stl`, see it; upload `cube.obj`,
      see `unsupported_format`. That is the "before."
- [ ] Second, cold agent session open in this directory. Transcript and `REVIEW-NOTES.md` in tabs.
- [ ] Share the editor + browser windows only.

## The run
**7:15** `sec-3`, then `demo-request` — read the three-line excerpt, say the full transcript is in the
repo. Ask the room for two undecided things. `demo-loop`, then switch.

**7:19 · Step 1 — draft from the recording (4 min).** Type, aloud:
> Draft a feature specification for OBJ support from `docs/meetings/2026-09-18-feature-review.md`,
> using the spec-authoring skill. Write it to `specs/obj-support.md`.

Narrate: it is reading a 24-minute meeting; section 6 is coming from the api-conventions skill.

**7:23 · Step 2 — read it as a human (6 min).** Open `demo/spec-v1.md` beside what it produced. Find
the three silences in `REVIEW-NOTES.md`, each with the timestamp where the room decided it. Point at
§8 "None." — the room parked units at [10:17]. Land the line: *well organised, well written,
complete-looking, and quiet in three places the room had decided.*

**7:29 · Step 3 — fix and approve (2 min).** `cp demo/spec-v2.md specs/obj-support.md`. Commit.

**7:31 · Step 4 — blind handoff (5 min).** Cold session, scroll up to show it is empty:
> Implement the feature specified in `specs/obj-support.md`. Follow the conventions already in the repository.

Do **not** ask it to write tests. If it asks a question, write the question on screen and tell it to
proceed on its best judgement.

**7:36 · Step 5 — your tests (3 min).** `make test`. Say who wrote `tests/test_obj_support.py` and when.
Then the browser: upload `cube.obj`, watch it render, the format tag now reads `stl obj`.

**7:40 · Step 6 — the exhibit (4 min).** `bash demo/run-round-1.sh` — *this is what version one's
criteria produced: five of ten.* Somebody will say "just fix the parser." The fix was the document.

**7:44** back to `blind-handoff`, `what-you-saw`.

## Fallbacks
- **Slow:** narrate the transcript → spec story.
- **Generated code does not run:** say so — *the failure mode I warned you about* — then
  `git stash -u && git checkout main && make test`. The finished parser is on `main`.
- **Tooling gone:** `what-you-saw` from `spec-v1.md` vs `spec-v2.md` on screen. Eight minutes.
- **Never debug live past 90 seconds.**
