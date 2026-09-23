# The human review — what to find on camera (step 2, ~7:24)

Read `spec-v1.md` against what the room actually decided in the transcript. Three problems, all of
the same kind: **the draft is not wrong, it is silent**, and silence is what the implementer fills in.

| | The draft says | What the meeting decided that the draft dropped | v2 |
|---|---|---|---|
| 1 | AC2: polygon faces "display correctly" | **[10:15]** the triangle count is the count *after* triangulation. "Correctly" has no number in it, so an implementer that keeps one triangle per quad passes it. | AC2: fan-triangulated, `triangle_count` counts the result — six quads → 12 |
| 2 | AC3: invalid files "rejected with an error" | **[10:04–10:05]** reject the *whole* file, and **name the line**. And **[10:06–10:08]** negative indices are *legal* and must load; out-of-range must reject. The draft has no idea negative indices exist. | AC3 (negative loads), AC4 (out-of-range, `line`), AC5 (bad line, `line`, nothing stored) |
| 3 | *(absent)* | **[10:12]** vertices with no faces → reject. The draft never mentions it, so an implementer stores an empty model. | AC6 |

Two smaller things worth pointing at: §8 says **"None."** — the meeting parked *units* explicitly at
[10:17], and an agent draft almost always writes "None." And AC5 says "the size limit" without the
number, when the room corrected it from fifty to twenty-five on the record.

Say the general lesson once all three are found: **the draft was well organised, well written,
complete-looking, and quiet in three places the room had actually decided.**
