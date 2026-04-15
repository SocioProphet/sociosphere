# manifest.v1

## Purpose
`manifest.v1` is the canonical, deterministic description of a mounted dataset view. It is the root object that connectors, indexers, Hyper feeds, releases, and conflict resolution bind to.

## Invariants
- every manifest has exactly one `manifest_id`
- `manifest_id` is the hash of the canonical serialized manifest body
- ordering is deterministic
- path entries may be plaintext or encrypted depending on policy profile
- every entry points to a canonical `object_id`
- manifests are immutable once committed; changes produce a new manifest

## Required fields
- `schema_version`: `manifest.v1`
- `manifest_id`
- `created_at`
- `created_by`
- `dataset_ref`
- `mount_ref`
- `policy_bundle_ref`
- `entries[]`
- `root_hash`

## Entry fields
Each entry contains:
- `logical_path`
- `path_mode`: `plaintext | encrypted`
- `object_id`
- `object_version`
- `size_bytes`
- `mtime`
- `mime_type`
- `connector_source_refs[]`
- `classification_tags[]`
- `acl_snapshot_ref`
- `tombstone`: boolean

## Canonical ordering
Entries sort by:
1. normalized logical path bytes
2. object_id
3. object_version

## Hashing
- hash algorithm: `sha256`
- `root_hash` is the Merkle-like aggregate over ordered entry hashes
- each entry hash is over the canonical serialized form of that entry

## Encryption mode
When `path_mode=encrypted`:
- `logical_path` stores ciphertext or opaque token
- cleartext path mapping remains local to the authoritative cell unless policy allows export

## Connector source references
`connector_source_refs[]` may include:
- Drive: `drive:file_id:revision_id`
- S3: `s3:bucket:key:version_or_etag`
- rsync: `rsync:path:fingerprint`
- Hyperdrive: `hyperdrive:key:path`
- local fs: `localfs:device:path:fingerprint`

## Authority rules
- local-first mode: local manifest authority wins unless explicit failover/quorum says otherwise
- release snapshots are immutable manifests
- mutable heads always point to the latest accepted manifest

## Export profiles
- `full`: plaintext paths + connector refs + object refs
- `redacted`: reduced metadata, plaintext optional
- `high_threat`: encrypted paths, minimized connector refs

## Signing
A detached signature SHOULD cover:
- `manifest_id`
- `dataset_ref`
- `root_hash`
- `policy_bundle_ref`
- `created_at`

## Relationship to other objects
- `indexpack.v1` binds to one `manifest_id`
- `ManifestDelta` events transition one manifest to the next
- releases point at immutable manifest roots
