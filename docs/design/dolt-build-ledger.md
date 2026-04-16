# Dolt build ledger for dependency resolution and build cache state

## Purpose
Define a robust, versioned state layer for workspace dependency choices, build inputs, cache hits/misses, and materialized outputs.

`Sociosphere` already owns the workspace manifest + lock and deterministic multi-repo materialization path. The missing persistence seam is a control-plane ledger that records **why** a build used a particular dependency graph and **what** cache/materialization state resulted.

## Decision
Use **Dolt** as the canonical relational ledger for:

- dependency graph snapshots
- dependency resolution decisions
- build-choice decisions
- cache entries and cache provenance
- build materializations and receipts

## Why Dolt
Dolt gives us:

- branch-based isolation for parallel build plans and canary resolution work
- commit history and diffs over relational state
- SQL-queryable history/diff/system tables
- remote-based or standby replication for read replicas / disaster recovery
- backup paths for both committed and uncommitted state

## Core rule
Git remains the source of truth for source code and workspace lockfiles.

Dolt becomes the source of truth for **evaluated build state**:

- which dependency set was chosen
- which upstream revisions were selected
- which cache objects are valid for a given choice set
- which materializations were produced
- which failures or invalidations occurred

## Minimal object family

The first persistent object family is:

- `dependency-resolution.v1`
- `build-choice.v1`
- `build-cache-entry.v1`
- `build-materialization.v1`

## Branch model

Use Dolt branches as isolated build-plan workspaces.

Examples:
- `main` — accepted build ledger state
- `resolve/<workspace>/<ts>` — dependency resolver proposal
- `build/<workspace>/<ts>` — materialization run state
- `cache-repair/<site>/<ts>` — cache invalidation or refill work

No branch writes directly to `main` without merge.

## Dependency semantics

The dependency ledger must be able to answer:

- which upstream repo/revision/input was selected?
- what solver or policy produced that choice?
- what alternatives were rejected?
- what lockfile/manifests did this choice correspond to?
- did this choice produce a reusable cache lineage?

## Cache semantics

Cache entries are not just blobs. They are keyed by:

- dependency-resolution identity
- build-choice identity
- target system / platform
- artifact class
- producer toolchain / executor
- validity state

A cache hit is only valid if the cache entry is still compatible with the current dependency resolution and build choice.

## Recommended tables

- `dependency_nodes`
- `dependency_edges`
- `dependency_resolutions`
- `build_choices`
- `build_choice_inputs`
- `build_cache_entries`
- `build_cache_bindings`
- `build_materializations`
- `build_failures`
- `cache_invalidations`

## Consumption path

1. workspace manifest + lock identify candidate inputs
2. resolver emits a `dependency-resolution` record in Dolt
3. build planner emits a `build-choice` record in Dolt
4. cache lookup binds or rejects `build-cache-entry` rows
5. materialization emits `build-materialization`
6. failures / invalidations emit ledger updates instead of disappearing into CI logs

## Non-goals

This design does not replace:

- Git history
- binary/object storage
- artifact registries
- Nix store semantics

It complements them by making evaluated build state reviewable, mergeable, and queryable.

## Follow-on

- land the starter schemas under `schemas/fabric/`
- land the starter Dolt DDL
- bind runner/orchestrator emissions to the ledger
- add cache validation and invalidation routines
