# EMVI Proof Slice Fixture (v0)

This fixture defines the canonical demonstration sequence for the proof slice.

## Fixture sequence

1. Operator opens a page through `ui_runtime`.
2. Operator captures the page into `collection:research`.
3. Operator selects a snippet in an editor and captures it into `collection:research`.
4. Operator proposes a shell command via the shell surface.
5. Policy evaluates the proposed command.
6. If allowed, the command executes and output is captured.
7. Operator issues a graph query through the graph façade.
8. At least one graph result is captured into `collection:research`.
9. Operator freezes `collection:research` into a snapshot.
10. Operator exports the snapshot.
11. Operator inspects the ledger/provenance trail for the full run.

## Expected artifacts

- one page capture object
- one snippet capture object
- one shell command object
- one shell output object
- one graph result object
- one collection containing all captured members
- one immutable snapshot
- one portable export artifact
- one provenance/ledger trail covering the sequence

## Notes

This fixture is intentionally small. It exists to pressure the shell, adapter,
policy, and provenance boundaries before broader surface coverage is attempted.
