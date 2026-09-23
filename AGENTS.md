# Agent instructions

Tool-agnostic version of `.claude/skills/`. Read before changing anything.

- `make test` must be green before you finish.
- **A new format is a parser in `app/mesh.py` registered in `PARSERS`.** Do not touch the routes for a
  new format; they dispatch through the registry.
- Every parser returns a `Mesh` of vertices and **triangular** faces. Triangulate polygons in the parser.
- Failure is `raise ParseError(message, line=N)`. On failure **nothing is stored**.
- Errors are `{detail, code, line}`. Use the codes already in use.
- Tests use the `client` and `samples` fixtures and are named `test_ac<N>_...`.

## When implementing from a specification
Implement what the specification says. Where it is silent, decide, and **write the decision down**
in your final message. Do not ask clarifying questions during a blind handoff. Do not write the
acceptance tests unless asked — those belong to the specification's author.

## When drafting a specification from a meeting transcript
Read the whole transcript. Record what was decided, including corrections made later in the meeting.
List what was parked as an open question. Do not resolve what the room left open.
