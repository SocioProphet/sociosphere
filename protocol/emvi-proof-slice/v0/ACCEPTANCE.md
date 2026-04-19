# EMVI Proof Slice Acceptance (v0)

## Acceptance target

The proof slice passes when one operator can coordinate browser, editor,
terminal, graph, collection, and provenance flows under one shell without
breaking focus ownership, host-boundary rules, or trust boundaries.

## Gates

### A. Focus ownership
- [ ] Shell grammar does not activate in editor insert mode.
- [ ] Shell grammar does not activate in terminal pass-through.
- [ ] Completion surface owns Tab when active.
- [ ] Escape unwinds the innermost transient state first.

### B. Page capture
- [ ] A page can be opened through the local UI runtime.
- [ ] The current page can be captured into a collection.
- [ ] The resulting item can be previewed or reopened later.

### C. Snippet capture
- [ ] A selected file range can be captured into the active collection.
- [ ] Captured snippet retains locator and anchor data.

### D. Guarded shell execution
- [ ] Shell execution first becomes an ActionSpec.
- [ ] Policy can deny, allow, or require confirmation.
- [ ] Captured output is stored as a typed object with provenance.

### E. Graph result capture
- [ ] A graph query can be executed through the graph façade.
- [ ] At least one graph result can be appended to the collection.

### F. Snapshot and export
- [ ] The working collection can be frozen into a snapshot.
- [ ] The snapshot can be exported to a portable form.

### G. Provenance
- [ ] Every nontrivial step emits inspectable provenance or ledger records.
- [ ] The operator can inspect what executed and what was captured.

## Failure conditions

The proof slice fails if any of the following occur:
- grammar steals local input ownership
- execution bypasses policy/confirmation requirements
- capture loses locator/anchor data
- export is not portable outside the live shell
- provenance is missing for a nontrivial step
