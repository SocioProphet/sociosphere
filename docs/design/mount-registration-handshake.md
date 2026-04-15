# Mount registration handshake

## Purpose
Define the runtime contract for turning a requested mount into a usable, queryable workspace surface.

This contract applies uniformly across:
- TopoLVM-backed PVC mounts
- host/bind mounts
- named engine volumes
- network filesystems
- Hyperdrive-backed materializations
- object-backed import/export surfaces

## Goal
A mount is not considered ready until the system can return:
- `MountRef`
- `ManifestRef`
- `IndexRef`
- `CapabilityGrantSet`
- optional `DistributionRefs`

## Core rule
`mounted != ready`

Ready means:
1. the storage surface resolved successfully
2. fingerprint and policy checks passed
3. an initial manifest exists
4. an index handle exists, even if state is `WARMING`
5. retrieval graph registration succeeded

## Request object
`MountSpec` MUST include:
- `mount_name`
- `intent_class`
- `backend_type`
- `access_mode` (`ro` or `rw`)
- `authority_mode` (`local_first | hybrid | provider_first`)
- `index_policy_ref`
- `retention_class_ref`
- `capability_policy_ref`
- optional `distribution_policy_ref`

## Response object
`MountRegistrationResponse` MUST include:
- `mount_ref`
- `manifest_ref`
- `index_ref`
- `readiness_state`
- `policy_bundle_ref`
- `capability_grants[]`
- optional `distribution_refs[]`
- optional `warnings[]`

## MountRef
`MountRef` fields:
- `mount_id`
- `backend_type`
- `resolved_path_or_handle`
- `node_ref`
- `rw_mode`
- `fingerprint`
- `capacity_bytes`
- `created_at`

## ManifestRef
`ManifestRef` fields:
- `manifest_id`
- `root_hash`
- `entry_count`
- `generation`
- `created_at`

## IndexRef
`IndexRef` fields:
- `index_id`
- `manifest_id`
- `pipeline_version`
- `state` (`WARMING | READY | DEGRADED`)
- `chunk_set_ref`
- `embedding_set_ref`
- `keyword_index_ref`

## CapabilityGrantSet
Each grant includes:
- `principal`
- `mount_id`
- `rights` (`r l i d w k a` plus execution scopes as needed)
- `network_profile`
- `secret_scope_refs[]`
- `expires_at`

## DistributionRefs
May include:
- `manifest_feed_ref`
- `index_feed_ref`
- `hyperdrive_ref`
- `topic_refs[]`

## Handshake phases
### Phase 1 — resolve
Resolve the requested backend into a concrete mount handle.

### Phase 2 — verify
Run:
- fingerprint check
- ACL/policy check
- capacity sanity
- backend-specific readiness probe

### Phase 3 — manifest
Produce `manifest.v1` root for the current visible dataset view.

### Phase 4 — index attach
Attach an existing index if one matches `(manifest_id, pipeline_version)`; otherwise create a new `IndexRef` in `WARMING` state.

### Phase 5 — retrieval registration
Register `IndexRef` in retrieval graph immediately.

### Phase 6 — distribution publish (optional)
Publish manifest/index deltas according to distribution policy.

## Failure classes
### Hard fail
Return `FAILED` and do not expose mount to retrieval when:
- fingerprint mismatch under strict mode
- policy denies access
- backend cannot be mounted
- manifest generation fails

### Soft fail
Return `DEGRADED` but keep mount usable when:
- index build warming exceeds threshold
- optional distribution publish fails
- remote connector dependency is unavailable but local cache is valid

## Backend notes
### TopoLVM
- authoritative cluster-local mount path is the mounted PVC in the workspace/runtime pod
- `mount_id` should bind to PVC UID + pod-local mount path + volume fingerprint

### Bind/host mounts
- fingerprint SHOULD include device/inode or equivalent host identity markers

### Network filesystems
- readiness should record staleness and lease/callback status where available

### Hyperdrive materializations
- treat imported materialization as a mount view, not as local authority unless policy promotes it

## Worked example
### Request
- backend: `topolvm`
- pvc: `ws-alpha-data`
- access: `rw`
- index policy: `rag-default-v1`
- authority: `local_first`

### Response
- `mount_ref.mount_id = mnt_ws_alpha_data_001`
- `manifest_ref.manifest_id = sha256:...`
- `index_ref.index_id = idx_ws_alpha_data_001`
- `index_ref.state = WARMING`
- retrieval graph accepts the mount immediately

## Follow-on implementation work
- canonical serialization for request/response envelopes
- signature format for manifest/index refs
- concrete health probe rules per backend
