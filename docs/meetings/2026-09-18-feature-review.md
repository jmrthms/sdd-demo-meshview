# MeshView — feature review

**Recorded:** Thursday, September 18, 2026, 10:00–10:24 · **Present:** Priya (product), Dan (engineering),
Marta (design), Tomasz (QE) · Transcript auto-generated, lightly cleaned. Speaker labels are role, not name,
after the first line.

---

**[10:00] Priya (product):** Okay, so the ask for this cycle. Three things came out of the customer calls. One, people
keep trying to upload OBJ files and the viewer just says unsupported. Two, they want to be able to see the wireframe,
not just the shaded thing. Three, some kind of info panel — triangle count, size, that sort of thing. And there's a
fourth one I'll mention at the end that I don't think we do this cycle.

**[10:01] Engineering:** OBJ is the big one. That's a real parser. STL is trivial by comparison — it's just a list of
triangles. OBJ has vertices in one list, faces referencing them by index, and the faces aren't necessarily triangles.

**[10:01] Product:** What do you mean not triangles.

**[10:02] Engineering:** Quads, mostly. Or bigger polygons. Half the OBJ files out of a modelling tool are quads. We'd
have to split them into triangles ourselves, because the viewer only draws triangles.

**[10:02] Product:** Fine, so we split them. From the user's point of view it should just work like STL does. Upload
it, it shows up in the list, click it, see it.

**[10:03] QE:** Can I get a definition of "work like STL" that I can test? Because right now for STL, if the file's
garbage we send back a 422 with a reason. If it's empty, 422. If it's too big, 413. Is OBJ getting all of those?

**[10:03] Product:** Yes. Same behaviour. Same error shapes.

**[10:04] Engineering:** Same error shape is easy. The interesting part is what counts as garbage for OBJ. An STL is
either a valid list of triangles or it isn't. An OBJ can be *partly* valid — a hundred good faces and then one line
that says `v 0 0 oops`. Do we take the hundred good faces, or reject the file?

**[10:04] QE:** Reject the file. If we take partial geometry the user sees a model with a hole in it and thinks the
software is broken. Reject it and tell them the line.

**[10:05] Product:** Tell them the line number?

**[10:05] QE:** We already have a `line` field in the error response. STL's ASCII parser fills it in. OBJ should too.
Otherwise a user with a two-hundred-thousand-line file has no idea where to look.

**[10:05] Product:** Okay. Reject the whole file, name the line. Written down.

**[10:06] Engineering:** Next one. OBJ files can reference vertices with negative numbers — minus one means "the last
vertex I defined." It's in the spec, tools use it, and if we don't handle it the model comes out scrambled with no
error at all.

**[10:06] QE:** That's worse than an error. Silent wrong geometry.

**[10:07] Engineering:** Agreed. And the flip side: a face that references vertex nine when there are only three. Also
silent unless we check.

**[10:07] Product:** Both of those are "reject and name the line," yes?

**[10:07] Engineering:** Negative indices we should *support*, they're legal. Out-of-range we reject.

**[10:08] Product:** Right. Support negative, reject out-of-range. Okay.

**[10:08] Design:** Can I do the viewer side before we go further down the parser? Whatever we add, it goes in the
existing left panel. The upload button stays where it is and stays the primary button. The format tag next to it
should update to say "stl obj" instead of just "stl." No new controls for this. I don't want a format picker — the
extension tells us the format.

**[10:09] Engineering:** Agreed on the extension. What about a `.OBJ` in capitals, or `.Obj`?

**[10:09] Design:** Case-insensitive, obviously.

**[10:09] QE:** "Obviously" is how things don't get tested. I'm writing it down.

**[10:10] Product:** What about the material stuff. OBJ files come with that separate `.mtl` file, right? Colours,
textures.

**[10:10] Engineering:** They can. And `usemtl` lines inside the OBJ that reference it. And groups, `o` and `g` lines,
and smoothing groups, `s`. My strong preference is we ignore all of it this cycle. Geometry only. We read `v` and
`f`, we skip everything else, and we don't fail on lines we skip.

**[10:11] Product:** So a file with materials still loads, it just loads grey.

**[10:11] Engineering:** Blue, but yes.

**[10:11] Design:** Blue. It's the accent colour.

**[10:11] Product:** Fine. Geometry only. Materials are explicitly not this cycle — put that in the spec as a non-goal
so nobody files it as a bug.

**[10:12] QE:** What about a file with vertices and no faces at all. Point cloud, basically. Some scanners export
those.

**[10:12] Engineering:** We can't draw it. There's nothing to draw.

**[10:12] Product:** Then reject it. Same as an empty STL.

**[10:13] QE:** And size. STL's cap is — what is it now, Dan?

**[10:13] Engineering:** Fifty meg.

**[10:13] QE:** It's twenty-five. I checked this morning.

**[10:13] Engineering:** Is it? Okay, twenty-five then. OBJ is text so it's less dense than binary STL — twenty-five
meg of OBJ is a lot of triangles. Same cap is fine.

**[10:14] Product:** Twenty-five for both. Same number, same error.

**[10:14] QE:** One more. Triangle count in the list. For a quad file, is the count the number of quads in the file or
the number of triangles after we split them?

**[10:15] Engineering:** Triangles. It's what we draw and it's what the STL count means.

**[10:15] Product:** Triangles after splitting. Good.

**[10:15] Design:** Units. STL has no units. Does OBJ?

**[10:16] Engineering:** Not really. Some exporters put a comment at the top. There's no standard. Whatever number is
in the file is what we show — same as STL, we don't say millimetres or metres anywhere.

**[10:16] Design:** So the info panel can't say "12 mm." It says "12." Hmm. I'd like to come back to that. Park it.

**[10:17] Product:** Parked. Units is an open question, not this cycle.

**[10:17] Product:** Wireframe toggle and the info panel — Marta, you had sketches?

**[10:18] Design:** Wireframe is a single toggle in the bottom-left readout, where the triangle count shows now. Info
panel is the same readout, just with the bounding box dimensions added. Both small. Honestly both could be one
ticket.

**[10:18] Engineering:** They're viewer-only changes, no backend. I'd do OBJ first — it's the one with actual risk —
and the viewer pair after, as a separate spec.

**[10:19] Product:** Agreed. OBJ this cycle, viewer pair next. And the fourth thing, for the record: a customer asked
for side-by-side comparison of two models. We are not doing that. It's a different product.

**[10:19] QE:** For OBJ, what do I need from the spec to write the tests? The happy path, quads, negative indices,
out-of-range, the bad-line case with the line number, points-only, the size cap, and materials-ignored. That's eight.

**[10:20] Engineering:** And the list showing `obj` as the format, and the mesh endpoint giving the viewer the same
shape it gets for STL. Ten.

**[10:20] QE:** Ten. I'll write them from the criteria once the spec's reviewed.

**[10:21] Product:** Dan, can you have the spec drafted by tomorrow so we can review it Monday?

**[10:21] Engineering:** I'll have the agent draft it from this recording tonight and I'll read it in the morning.
Monday review is fine.

**[10:22] Product:** Good. Anything else? … No? Okay, thanks all.

*[recording ends 10:24]*
