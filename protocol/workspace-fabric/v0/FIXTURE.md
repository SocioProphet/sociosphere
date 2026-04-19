# Fixture

## Mount registration request

```yaml
api_version: sourceos.fabric.mount/v0.1
kind: MountRegistrationRequest

workspace:
  cell: cell-alpha
  id: ws-research
  principal: operator.local

mount:
  id: topo-main
  backend: topolvm
  resolved_handle: /var/lib/sourceos/workspaces/ws-research
  authority_mode: local_first
  durability_class: local_persistent
  replay_mode: append_only_evidence
  visibility_default: private

datasets:
  - id: ds-notes
    role: primary
    indexes:
      - id: idx-notes-xapian
        engine: xapian
        mode: authoritative_local
      - id: idx-notes-vec
        engine: tantivy
        mode: derived_cache

adapters:
  - kind: hypercore
    role: topic_distribution
    topics: [notes.events, notes.snapshots]
  - kind: s3
    role: object_snapshot_replica
    bucket: ws-research-snapshots
  - kind: drive
    role: compatibility_mirror
    folder_id: drive-folder-123
  - kind: rsync
    role: bulk_sync
    endpoint: rsync://backup/ws-research

policy:
  bundle: policy/default
  quorum_profile: local-owner-plus-1
  require_signed_tombstones: true
  stale_mirror_policy: metadata_only

lease_request:
  ttl: 24h
  renewable: true
```

## Lease response

```yaml
api_version: sourceos.fabric.mount/v0.1
kind: MountRegistrationLease

status: active

lease:
  id: lease-01JABCXYZ
  issued_at: 2026-04-18T23:00:00Z
  expires_at: 2026-04-19T23:00:00Z
  renewable: true

workspace:
  cell: cell-alpha
  id: ws-research

mount:
  id: topo-main
  authority_mode: local_first
  backend: topolvm
  status: active

approved:
  datasets: [ds-notes]
  indexes: [idx-notes-xapian, idx-notes-vec]
  adapters:
    - hypercore:topic_distribution
    - s3:object_snapshot_replica
    - drive:compatibility_mirror
    - rsync:bulk_sync

evidence:
  stream: /cells/cell-alpha/evidence/mount-registration
  correlation_id: reg-topo-main-20260418-001
```

## Evidence event envelope

```yaml
event_id: ev-01JABCXYZ
event_type: mount.registration.proposed
occurred_at: 2026-04-18T23:00:00Z

actor_ref: operator.local
workspace_ref: ws-research
mount_ref: topo-main
dataset_ref: ds-notes
policy_bundle_ref: policy/default
correlation_id: reg-topo-main-20260418-001

payload:
  authority_mode: local_first
  backend: topolvm
  adapters:
    - hypercore:topic_distribution
    - s3:object_snapshot_replica
  status: proposed
```

## Error registry

```text
E_PATH_ESCAPE
E_BACKEND_UNSUPPORTED
E_AUTHORITY_MODE_INVALID
E_QUORUM_REQUIRED
E_POLICY_DENIED
E_TOMBSTONE_UNSIGNED
E_TOMBSTONE_CONFLICT_LOCAL_DIRTY
E_INDEX_ROLE_CONFLICT
E_STALE_MIRROR_BLOCKED
E_LEASE_EXPIRED
E_ADAPTER_ROLE_INVALID
E_DATASET_BINDING_INVALID
E_REPLAY_STREAM_MISSING
```
