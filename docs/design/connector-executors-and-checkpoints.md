# Connector executors and checkpoint persistence

## Purpose
Define how connector contracts are executed at runtime and how they persist progress safely across restarts, partitions, and replay.

This document covers executor behavior for:
- Google Drive
- rsync
- S3 / MinIO
- Hyper distribution

## Core rule
Connector execution is idempotent relative to canonical identity and checkpoints.

Executors do not invent authority. They materialize changes into the local-first canonical fabric according to connector policy.

## Executor model
Each connector executor runs as a bounded worker with:
- `connector_id`
- `dataset_ref`
- `policy_bundle_ref`
- `checkpoint_ref`
- `health_state`
- `lag_metrics`

## Common executor phases
1. restore checkpoint
2. scan for remote/local changes
3. stage candidate changes
4. policy check candidates
5. fetch/push as allowed
6. emit manifest/index deltas
7. persist checkpoint atomically
8. emit evidence/audit events

## Checkpoint object
`ConnectorCheckpoint` MUST include:
- `checkpoint_id`
- `connector_id`
- `dataset_ref`
- `cursor_or_marker`
- `last_successful_scan_at`
- `last_applied_change_id`
- `integrity_digest`
- `executor_version`
- `created_at`
- `updated_at`

## Atomicity rules
- a checkpoint is only advanced after all associated local state mutations are committed
- partial fetches may be tracked in executor-private scratch state but MUST NOT advance the shared checkpoint until complete
- corrupted checkpoints force replay from the last known-good checkpoint or a connector-specific recovery baseline

## Health states
- `IDLE`
- `RUNNING`
- `DEGRADED`
- `FAILED`
- `BLOCKED_BY_POLICY`

## Lag metrics
Executors SHOULD report:
- scan lag
- apply lag
- queued change count
- bytes pending
- last success timestamp

## Google Drive executor
### Scan source
- change cursor / page token

### Runtime behavior
- baseline listing establishes initial cursor state
- changes are processed in cursor order
- local objects are created from downloaded bytes and attached to new manifests
- local edits that conflict with newer remote revisions go to manual reconcile queue under `local_first`

### Checkpoint fields
Additional optional fields:
- `start_page_token`
- `last_page_token`
- `last_processed_file_ids[]` (bounded/debug only)

## rsync executor
### Scan source
- explicit scheduled sync job or manual invocation

### Runtime behavior
- rsync is treated as filesystem transport, not canonical metadata authority
- default mode is one-way mirror unless policy explicitly enables bidirectional flows
- deletes only propagate when configured

### Checkpoint fields
Additional optional fields:
- `source_tree_fingerprint`
- `last_sync_mode`
- `last_remote_snapshot_hint`

## S3 / MinIO executor
### Scan source
- object listing, version markers, or event stream if configured

### Runtime behavior
- when S3 is canonical, executor may materialize local caches/indexes
- when S3 is replica, local manifest authority remains primary in `local_first`
- delete markers become signed tombstones before local application when needed

### Checkpoint fields
Additional optional fields:
- `continuation_token`
- `last_seen_version_marker`
- `bucket_generation_hint`

## Hyper executor
### Scan source
- replicated feed sequence positions

### Runtime behavior
- manifest and index delta feeds are primary; raw content replication is policy-gated
- executor tracks feed seq positions independently for manifest feed, index feed, and optional hyperdrive content
- public topic exposure is forbidden in `high_threat` unless explicitly allowed

### Checkpoint fields
Additional optional fields:
- `manifest_feed_seq`
- `index_feed_seq`
- `content_feed_seq`
- `peer_set_digest`

## Recovery rules
- executors MUST tolerate restarts without duplicating destructive operations
- replay from checkpoint MUST be safe and idempotent
- policy changes MAY force executor pause until reauthorized

## Follow-on implementation work
- exact persistent store layout for checkpoints
- backoff and retry tuning
- manual reconcile queue schema
