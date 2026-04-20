# Adapter role matrix

## TopoLVM / local block-backed workspace

Role: authoritative local persistence plane.

Allowed authority:
- yes, default
- best fit for `local_first`

Best use:
- primary workspace mount
- authoritative local dataset storage
- authoritative local indexes

## Hypercore / Dat-style append-only feed

Role: topic distribution and append-only replay/snapshot dissemination.

Allowed authority:
- not default mutable workspace authority
- acceptable for append-only event and topic surfaces when explicitly scoped

Best use:
- `topic_distribution`
- replay streams
- snapshot advertisements
- evidence/event feeds

## MinIO / S3

Role: object snapshot replica, cold export, archive.

Allowed authority:
- only under explicit `provider_first` or approved hybrid policy

Best use:
- `object_snapshot_replica`
- `cold_archive`
- restore source for snapshots

## rsync

Role: bulk sync and bootstrap transport.

Allowed authority:
- no implicit authority
- transport only

Best use:
- `bulk_sync`
- migration/bootstrap
- cold import/export

## Google Drive API

Role: compatibility mirror and collaboration ingress/egress.

Allowed authority:
- not by default
- only if explicitly promoted and policy/quorum approved

Best use:
- `compatibility_mirror`
- `collaboration_ingress`
- controlled document interchange

## Index engines

### Xapian
Role: lexical search index.
Best fit: authoritative_local or derived_cache.

### Tantivy
Role: fast local search index.
Best fit: derived_cache or authoritative_local under explicit policy.

### SQLite FTS
Role: embedded metadata/control-plane lookup.
Best fit: lightweight local search and metadata indexing.

## Default profile

```yaml
authority_mode: local_first
require_signed_tombstones: true
stale_mirror_policy: metadata_only
remote_authority_promotion: quorum_required
authoritative_remote_indexes: disabled_by_default
preview_visibility_on_conflict: metadata_only
```
