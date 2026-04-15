# Connector contracts

## Purpose
Define a uniform adapter contract for external and inter-site data movement.

Connectors covered in v1:
- Google Drive
- rsync
- S3 / MinIO
- Hyper manifest/index distribution

## Core rule
Connectors do not own canonical identity.

Canonical identity is always:
- `object_id`
- `object_version`
- `manifest_id`

Connectors only provide:
- source references
- transport
- incremental change signals
- optional ACL metadata

## Common connector interface
Each connector SHOULD implement:
- `scan(cursor) -> changes[]`
- `fetch(source_ref) -> object bytes or stream`
- `push(local_ref) -> source_ref` when enabled
- `ack(cursor)`
- `checkpoint() -> connector state`
- `restore(checkpoint)`
- optional `map_acl(remote_acl)`

## Change record shape
Each `change` includes:
- `change_id`
- `source_ref`
- `operation` (`create | update | delete | move | permission_change`)
- `remote_version_hint`
- `observed_at`
- optional `metadata`

## Drive connector
### Source refs
`drive:file_id:revision_id`

### Expected behavior
- baseline import via listing scoped roots
- incremental sync via change cursor
- downloads resolve to canonical objects locally
- remote permissions may be captured as advisory metadata and mapped into local policy where allowed

### Default policy
- `local_first`: pull or staged-sync default
- remote deletes become tombstones only after policy check
- local edits after last synced revision trigger manual reconcile queue

## rsync connector
### Source refs
`rsync:path:fingerprint`

### Expected behavior
- treated primarily as filesystem transport
- by default used for one-way mirror or controlled sync jobs
- quick-check mode uses mtime + size semantics unless stronger verification policy is enabled

### Default policy
- do not use bidirectional mutable sync by default
- destructive delete propagation must be explicit

## S3 / MinIO connector
### Source refs
` s3:bucket:key:version_or_etag `

### Expected behavior
- may act as canonical object store or replica depending on deployment mode
- when used as replica, local manifest authority remains primary in `local_first`
- object version ids or etags inform remote version hints

### Default policy
- signed tombstones for deletes
- budget + lifecycle rules apply to replica storage independently of local hot storage

## Hyper distribution connector
### Source refs
- `hypercore:feed_key:seq`
- `hyperdrive:key:path`

### Expected behavior
- manifest/index delta export by default
- optional raw object distribution only when policy allows
- topic exposure controlled by threat profile

### Default policy
- `high_threat` disables public discovery
- out-of-band sharing of topic refs preferred

## Connector checkpoints
Every connector checkpoint SHOULD include:
- connector id
- dataset scope
- last committed cursor/marker
- last successful scan time
- integrity summary

## Error classes
- `TRANSIENT_UNAVAILABLE`
- `AUTH_EXPIRED`
- `PERMISSION_DENIED`
- `SOURCE_CONFLICT`
- `CHECKPOINT_CORRUPT`
- `POLICY_BLOCKED`

## Worked examples
### Example 1 — Drive pull into local-first corpus
1. `scan(cursor)` returns changed file ids
2. `fetch()` downloads bytes
3. bytes become canonical `object_id`
4. manifest advances
5. index warms on new manifest

### Example 2 — rsync export outbox
1. local release snapshot selected
2. export tree materialized
3. rsync transport copies tree to peer
4. peer ingests into its own canonical store

### Example 3 — Hyper mesh index sharing
1. local manifest/index deltas emitted
2. Hyper connector publishes feeds
3. peer replicates feeds and reconstructs import-side manifest/index state

## Follow-on implementation work
- exact checkpoint serialization
- ACL mapping schemas
- per-connector metrics and lag reporting
