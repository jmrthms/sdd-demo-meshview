# Feature Specification — OBJ file support

**Status:** draft · **Author:** drafted by the agent from `docs/meetings/2026-09-18-feature-review.md`, 7:22

> **This is the FIRST DRAFT, with its problems left in.** Well organised, complete-looking, and quiet
> about three things the meeting actually decided. The approved version is `spec-v2.md`.

## 1. Intent
Users keep uploading OBJ files and the viewer rejects them as unsupported. Accept OBJ so that it
works like STL: upload, list, view.

## 2. User stories
- As a user, I want to upload an OBJ file and see it, so that I do not have to convert it.

## 3. Acceptance criteria
1. Given a valid `.obj` file, when uploaded, then it is accepted and appears in the model list with
   format `obj`.
2. Given an OBJ with polygon faces, when uploaded, then it displays correctly in the viewer.
3. Given an invalid OBJ file, when uploaded, then it is rejected with an error.
4. Given material and group lines, when uploaded, then they are ignored.
5. Given a file over the size limit, when uploaded, then it is rejected.
6. Given an uploaded OBJ, when the mesh is fetched, then the viewer can draw it.

## 4. Scope and non-goals
**In:** OBJ geometry. **Out:** materials, textures, the wireframe toggle, the info panel, comparison.

## 5. Interfaces and contracts
`POST /models?name=file.obj`, as for STL. Same response shape. Same error shape.

## 6. Constraints
Follow the repository's conventions for parsers and errors. Same size limit as STL.

## 7. Test plan
Tests for the criteria above, using the sample files.

## 8. Open questions
None.
