# Conflict matrix

## Purpose
Define authoritative side, version source, tombstone semantics, and manual intervention triggers for each connector and topology.

## Default strategy hierarchy
1. explicit release snapshot beats mutable head
2. authoritative local cell beats remote replica in `local_first`
3. explicit quorum failover can temporarily change authority
4. manual reconcile queue beats silent destructive merge

## Topology matrix

### Local mount ↔ local canonical object store
- authority: local mount ingest path
- version source: manifest generation order
- tombstones: explicit and immediate
- manual intervention: no

### Google Drive ↔ local-first workspace
- authority: local in `local_first`, drive in `provider_first`
- version source: Drive revision / modified time + local manifest generation
- tombstones: remote delete becomes local tombstone only after policy check
- manual intervention: yes when local edits exist after last synced revision

### rsync peer ↔ local-first workspace
- authority: configured per connector; default local
- version source: checksum if enabled, otherwise mtime+size
- tombstones: delete propagation only when explicitly enabled
- manual intervention: yes for bidirectional mutable trees unless one side is declared source-of-truth

### S3/MinIO replica ↔ local-first workspace
- authority: local unless replica is promoted
- version source: object version id or etag + manifest generation
- tombstones: propagate as signed delete markers
- manual intervention: only when split-brain promotion occurs

### Hyper mesh peer ↔ local-first workspace
- authority: release snapshot or signed feed ordering
- version source: feed sequence + signed manifest/index refs
- tombstones: feed deltas carry tombstones explicitly
- manual intervention: yes if peer presents conflicting mutable head without accepted quorum event

### Cloud twin ↔ edge authoritative site
- authority: edge by default
- version source: snapshot generation + manifest generation
- tombstones: mirrored after replication checkpoint
- manual intervention: required for failover/failback transitions

## Safe defaults
- Drive connectors default to pull or local-authoritative sync
- rsync defaults to one-way mirror unless explicitly promoted
- Hyper distribution defaults to manifest/index export only
- vendor file stores are never authoritative

## Open decisions
- exact tie-breakers when local edits and remote tombstones race
- branch/merge semantics for collaborative mutable datasets
- failback rules after cloud twin promotion
