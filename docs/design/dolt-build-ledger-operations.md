# Dolt build ledger operational rules

## Purpose
This note defines the operational rules for the Dolt-backed build ledger so dependency resolution, build choices, cache state, and materializations are preserved in a robust and reviewable way.

## Branch strategy
Use Dolt branches as isolated workspaces for build state.

Recommended branch families:
- `main` — accepted build ledger state
- `resolve/<workspace>/<ts>` — dependency resolution work
- `build/<workspace>/<ts>` — build/materialization run state
- `cache-repair/<site>/<ts>` — cache repair and invalidation work

No direct write to `main` without merge.

## Remote / replication strategy
Use Dolt remotes for committed state replication.

Recommended posture:
- writer pushes committed branch state to remote
- readers / mirrors pull from remote on demand
- remote mirrors are used for read and disaster recovery of committed state

## Backup strategy
Use Dolt backups for states that must preserve uncommitted working sets.

Operational rule:
- remotes protect committed history
- backups protect both committed and uncommitted branch state

## Conflict handling
Conflicts are treated as a signal that competing build or cache state needs explicit resolution.

Operational rule:
- do not auto-commit unresolved conflicts
- resolve conflicts before accepting branch state into `main`
- treat cache invalidation or dependency-choice disagreement as reviewable ledger events, not silent overwrite behavior

## Queryability expectations
The ledger should support answering:
- which dependency resolution produced this build choice?
- which cache state was active for that choice?
- which materialization consumed or produced a given artifact?
- what branch introduced a cache invalidation or changed a dependency edge?

## Minimal persisted families
Even before full schema coverage lands, the ledger must preserve these concepts:
- dependency resolution
- build choice
- cache state
- materialization state
- failure / invalidation notes

## Integration rule
Git remains canonical for source code and lockfiles.
Dolt remains canonical for evaluated build state derived from those inputs.
