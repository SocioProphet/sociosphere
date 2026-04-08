# Remote source and materialization policy

This note clarifies the intended materialization posture for `sociosphere`.

## Principle

A deterministic workspace controller should make it clear which repos are:

- remote and lock-resolved
- local-only and intentionally unresolved from remote sources
- missing required remote source metadata

## Why this matters

Without an explicit distinction, a clean checkout can silently depend on undocumented local state.

## Policy direction

- repos with remote materialization intent should declare a remote source and be lock-resolved
- repos that are intentionally local-only should be explicit about that status
- generated reports should make the distinction visible to operators and CI

## Relation to the rest of the stack

`sociosphere` owns workspace composition truth.
It should not absorb execution-plane evidence ownership from `agentplane`.
