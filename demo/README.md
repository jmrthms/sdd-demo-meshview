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
| `BLIND-HANDOFF-REPORT.md` | What a fresh session reported when handed `spec-v2.md` blind on Sep 23: **10 of 10** |

## Verified
```
demo/start before the build     13 passed, 10 red (the criterion tests)
round 2 (from spec-v2)          23 passed
round 1 (from spec-v1)          7 of 10 criteria FAIL
blind handoff, Sep 23, tests withheld   10 of 10 author tests pass (BLIND-HANDOFF-REPORT.md)
step 1 cold, Sep 23             9 min to a 268-line draft; found the skill by name; did not open demo/ or the red tests
step 4 cold, Sep 23             6 min, including its own check of all ten criteria against the API
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

**7:19 · Step 1 — draft from the recording (2 min — do not wait for it).** Type, aloud:
> Draft a feature specification for OBJ support from `docs/meetings/2026-09-18-feature-review.md`,
> using the `how-to-write-a-spec` skill. Write it to `specs/obj-support.md`.

Narrate for a minute: it is reading a 24-minute meeting; it found the skill by name; section 6 is
coming from the api-conventions skill. Then: *"This takes it several minutes — nine, this morning.
Here is what the same prompt produced then."* Open `demo/spec-v1.md` and go to step 2. When the live
draft lands, give it ten seconds on screen: the same eight sections, a different length. Drafts vary
run to run; the one being reviewed is the one that has been read.

**7:21 · Step 2 — read it as a human (6 min).** Open `demo/spec-v1.md` beside what it produced. Find
the three silences in `REVIEW-NOTES.md`, each with the timestamp where the room decided it. Point at
§8 "None." — the room parked units at [10:17]. Land the line: *well organised, well written,
complete-looking, and quiet in three places the room had decided.*

**7:27 · Step 3 — fix and approve (2 min).** If the step-1 session is still running, stop it first
(Ctrl-C twice) — its draft is not the one being shipped. `cp demo/spec-v2.md specs/obj-support.md`.
Commit.

**7:29 · Step 4 — blind handoff (up to 7 min).** Cold session, scroll up to show it is empty:
> Implement the feature specified in `specs/obj-support.md`. Follow the conventions already in the repository.

Do **not** ask it to write tests. If it asks a question, write the question on screen and tell it to
proceed on its best judgement. While it works (six minutes this morning, including its own check
against the API): put `specs/obj-support.md` §3 on screen and walk through criteria 2, 3 and 7 — the
ones slide 16 did not show — and §8, the parked question. **If it is still running at 7:37**, stop it
(Ctrl-C twice), show `demo/BLIND-HANDOFF-REPORT.md` — this morning's run of the same prompt, ten of
ten — and take the fallback: `git stash -u && git checkout main && make test`.

**7:36 · Step 5 — your tests (3 min).** `make test`. Say who wrote `tests/test_obj_support.py` and when.
Then the browser: upload `cube.obj`, watch it render, the format tag now reads `obj stl`.

**7:39 · Step 6 — the exhibit (4 min).** `bash demo/run-round-1.sh` — *this is what version one's
criteria produced: seven of ten.* Somebody will say "just fix the parser." The fix was the document.

**7:43** back to `blind-handoff`, `what-you-saw`.

## Fallbacks
- **Slow:** narrate the transcript → spec story.
- **Generated code does not run:** say so — *the failure mode I warned you about* — then
  `git stash -u && git checkout main && make test`. The finished parser is on `main`, and
  `demo/BLIND-HANDOFF-REPORT.md` is what the same prompt produced this morning: show that instead.
- **Tooling gone:** `what-you-saw` from `spec-v1.md` vs `spec-v2.md` on screen. Eight minutes.
- **Never debug live past 90 seconds.**
