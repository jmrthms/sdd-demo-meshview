# What a blind handoff actually reports

**Dry run, Wed Sep 23, the morning of the session.** A fresh agent session — no conversation
history, nothing but the repository and `specs/obj-support.md` (= `demo/spec-v2.md`) — was told:

> Implement the feature specified in `specs/obj-support.md`. Follow the conventions already in
> the repository.

The ten criterion tests in `tests/test_obj_support.py` were **withheld** from that repository, so
the code was built from the specification alone. (On `demo/start` they are present and red, which
is the easier case.) They were run against its code afterwards.

**Result: 10 of 10 of the spec author's acceptance tests passed, 23 of 23 overall.** The
specification was implementable blind. That is the claim the whole exercise rests on.

What follows is the implementer's own report, verbatim except for shortening the sandbox path.
Read sections 3 and 4: **this is what a good gap analysis looks like.** Every assumption named,
every complaint pointing at a section number. Four of its five complaints were simply correct —
the specification has since been fixed for each (the `obj stl` order, `size_bytes`, a binding
default for the forward-reference question, the renamed-STL case under AC6). The fifth, "the test
file promised in §7 is absent", was true only because this dry run withheld it on purpose.

---

## 1. FILES CHANGED

- `app/mesh.py` — added `parse_obj` and `_obj_index`, registered `"obj"` in `PARSERS`, added
  `import math`, updated the module docstring. No route, model, viewer, or test changes.

## 2. TEST RESULT

`13 passed in 0.07s`

(Separately, a throwaway script outside the repo drove all ten criteria through the API against a
temp database — all passed, nothing stored on rejection. Script deleted.)

## 3. ASSUMPTIONS

- "a malformed line anywhere in the file" vs AC7 "any other non-geometry line … ignored": only `v`
  and `f` lines are validated; everything else (including unknown keywords, a bad `vn`) is skipped.
- "the `v` and `f` records": `v` needs three finite floats; a 4th `w` or trailing colour values are
  ignored, not validated. `nan`/`inf` count as "non-numeric" (they would 500 in JSON otherwise).
- "only `i` is used": the `t`/`n` slots are not inspected; more than three `/`-fields, a
  non-integer, or index `0` is `bad face` with the line.
- Fewer than three indices on an `f` line: rejected with the line.
- §8 "such a file is rejected": implemented as stated — positive indices resolve against vertices
  defined so far, so forward references fail with "face references vertex 1 but only 0 are defined".
- Line numbering: physical lines (LF/CRLF/CR), comments and blanks counted; UTF-8 BOM stripped;
  `#` starts a comment anywhere on a line. Line continuation (`\`) not supported.
- Not an OBJ at all (no `v`, no `f`): distinct message `not an OBJ file: no vertex or face records
  found`, still 422 `parse_error`.
- No vertex de-duplication or pruning; bbox covers every `v`, matching what the viewer computes.
- Viewer untouched: the tag already reads `/formats`.

## 4. SPEC PROBLEMS

- §4 says the tag shows `stl obj`, but §5 fixes `/formats` as `["obj","stl"]` and §6 forbids route
  changes — the tag will read `obj stl`. Pick one.
- §7 promises `tests/test_obj_support.py` "before the handoff"; it is absent, so nothing verifies
  the author's reading. README's "23 tests" likewise does not match the 13 present.
- §8 lists forward references as open while §6/AC3 already decide it. Say which is binding.
- §5 example `size_bytes: 231` — `cube.obj` is 194 bytes.
- "The file is not what its extension says" is never specified; it only falls out of AC6.
