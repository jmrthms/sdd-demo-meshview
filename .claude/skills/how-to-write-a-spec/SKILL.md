---
name: how-to-write-a-spec
description: >
  Use whenever the task is to write, review or revise a feature specification for this
  repository — including drafting one from a meeting transcript in docs/meetings/. Produces
  specs/<feature>.md following the eight-section template and pulls in this repository's API
  and testing conventions so implementation reads only the spec.
---

# Writing a feature specification here

One feature, one file, in `specs/`. Two to four pages. Name it after the feature: `specs/obj-support.md`.

## Before writing, read
- `.claude/skills/api-conventions/SKILL.md` — the upload path, the error shape, where formats plug in.
  **Sections 5 and 6 of the spec must reflect it.**
- `.claude/skills/testing/SKILL.md` — fixtures, sample files, how tests are named. **Section 7 must reflect it.**
- The meeting transcript you were pointed at, **all of it**. Decisions are stated in passing, corrected
  later, and sometimes parked. The spec records what was *decided*, names what was *parked* as an
  open question, and does not resolve what the room left open.

Pull the specific rules in as concrete sentences. Not "follow the conventions" — "the error body is
`{detail, code, line}` and `line` is set when the parser knows where it stopped."

## The eight sections
1. **Intent** — what problem, for whom, in three or four sentences. No implementation.
2. **User stories** — small. Two "ands" is two stories.
3. **Acceptance criteria** — numbered, given / when / then, each one an assertion you could write.
   **Include the unhappy paths.**
4. **Scope and non-goals** — name the adjacent things deliberately not being built.
5. **Interfaces and contracts** — endpoint, request, response, error bodies, with worked examples.
6. **Constraints** — from the two skills above, plus limits *with numbers*.
7. **Test plan** — which criterion is covered by which test, by number.
8. **Open questions** — what the room did not decide, and who can.

## The unhappy paths this repository actually has
A spec here is not finished until it answers these for the format or feature it describes:
- The file is **empty**. The file is **not what its extension says**. The file is **over the size limit**.
- The file is **partly valid** — good geometry, then a bad line. Take the good part, or reject the file?
- The parser hits something **legal but easy to get wrong** (for OBJ: relative indices, polygon faces).
- A reference is **out of range**. Silent wrong geometry is worse than an error.
- There is **nothing to draw** (vertices, no faces).
- The file carries things this viewer **ignores** (materials, groups, normals). Ignoring is a decision — say so.
- **Case** of the extension. **Units** — this viewer shows file units and names none.

## Where to stop
Specify observable behaviour, contracts, and limits. Do not specify how the parser is structured,
what the helpers are called, or the order of steps nobody can observe. If you are writing pseudocode,
you have gone too far.
