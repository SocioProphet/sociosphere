# EMVI Cross-Surface Proof Slice

Status: Draft v0.1

## Purpose

This proof slice is the first end-to-end demonstration that EMVI is more than a
command bar. It must prove that one operator shell can safely coordinate browser,
editor, terminal, graph, collection, and provenance flows while remaining aligned
to the local-first agent stack.

## Scope

The proof slice covers these service families:
- `ui_runtime`
- `network`
- `policy`
- `collection`
- `graph`
- `knowledge`
- `shell`
- `ledger`
- `placement`
- `user`

## Required demonstration path

1. Open a page through the local digital-twin UI runtime.
2. Capture that page into a named collection.
3. Capture an editor selection into the same collection.
4. Execute a guarded shell command and capture its output.
5. Query the graph façade for a related structured result.
6. Append the graph result to the same collection.
7. Freeze the collection into an immutable snapshot.
8. Export the snapshot.
9. Inspect provenance and ledger records for every step.

## Required shell behaviors

### 1. Focus correctness
- Grammar only runs in grammar-owning states.
- Editor insert and terminal pass-through remain locally owned.
- Escape unwinds the innermost transient state first.
- Up/Down history escape from multiline surfaces only at allowed boundaries.

### 2. Parse correctness
- Free text remains search by default.
- Explicit command mode with `>` must work.
- Scoped search with slash must work in shell-owned states.
- Deictics such as `current` and `selection` must resolve against the active context.

### 3. Trust correctness
- Every side effect must generate an ActionSpec before execution.
- The ActionSpec must include trust class, target objects, service-family routing,
  confirmation policy, and provenance sink.
- Guarded shell execution must pass through policy before execution.

### 4. Capture correctness
- Page capture must preserve locator and anchor material.
- Snippet capture must preserve file path, line/symbol anchors, and context.
- Shell capture must preserve command identity, output span, and execution metadata.
- Graph capture must preserve query context and row identity.

## Minimal acceptance criteria

### Browse and page capture
- A page can be opened through `ui_runtime` without trusting remote JS/CSS by default.
- The current page can be captured into a collection.
- The resulting item can be previewed and reopened.

### Editor snippet capture
- A selected file range can be captured into the current collection.
- The resulting item can re-resolve its source location.
- The collection records snippet provenance separately from page provenance.

### Guarded shell execution
- A shell command can be proposed and reviewed as an ActionSpec.
- Policy evaluation can deny, require confirmation, or allow execution.
- Output capture becomes a typed collection member.

### Graph result capture
- A graph query can be issued through the graph façade.
- At least one result row can be captured into the collection.
- The result retains query and row provenance.

### Snapshot and export
- The collection can be frozen into a snapshot.
- The snapshot can be exported to at least one portable representation.
- The exported artifact can be inspected without requiring the live shell.

### Provenance and ledger
- Every action in the path must emit provenance or ledger-visible records.
- The operator must be able to inspect what was captured, what executed, and why.

## Explicit non-goals for the first slice

- Full global shell coverage across every host surface
- Arbitrary destructive host actions
- Broad multi-user collaboration flows
- Remote web trust relaxation
- All adapters or all scopes

## Suggested first command set

- `>open current`
- `>capture current into collection:research`
- `>capture selection into collection:research`
- `>run current`
- `>query graph:commonsense "MATCH (...) RETURN ..."`
- `>snapshot collection:research`
- `>export snapshot:current`
- `>inspect ledger current`

## Failure modes that must be surfaced, not hidden

- ambiguous parse
- denied policy evaluation
- missing anchor re-resolution
- unavailable adapter capability
- export failure
- provenance sink failure
- host-boundary ownership conflict

## Exit condition

The proof slice is complete when one operator can traverse the full path above,
without the shell stealing local input ownership, while producing stable captured
objects, explicit execution plans, and inspectable provenance.
