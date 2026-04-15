# FabricFS command surface

## Goals
Provide an AFS-inspired operator interface for mounts, quotas, ACLs, replication status, and governance.

## Core commands
- `fs examine <path>`
  - prints mount type, MountRef, manifest root, index generation, quota, replication status
- `fs listquota <path>`
  - prints data bytes, index bytes, cache bytes, limits
- `fs setquota <path> <limit>`
  - updates quota envelope (policy-gated)
- `fs listacl <path>` / `fs setacl <path> <principal> <rights>`
  - directory-scoped ACLs using `rlidwka`
- `fs whereis <path>`
  - shows backing endpoints / replica locations
- `fs whichcell <path>`
  - shows trust/admin domain

## Required semantics
- `lookup`/traversal requirements must be linted; no effective read/write without traversable parents
- command output must be scriptable (`--json`)
- governance objects under `.quorum/` must be visible and inspectable
