# Mount agent responsibilities

## Purpose
Define the local/runtime component that turns mounted storage into manifest/index state and keeps that state current.

## Core role
The mount agent is the authoritative observer for a resolved mount within a workspace/runtime boundary.

## Responsibilities
1. verify mount readiness
2. fingerprint backend identity
3. scan filesystem/object view into `manifest.v1`
4. trigger index attach or rebuild according to policy
5. emit manifest/index deltas to the local journal
6. optionally hand deltas to distribution connectors

## Inputs
- `MountRef`
- `PolicyBundleRef`
- `IndexPolicyRef`
- `CapabilityGrantSet`

## Outputs
- `ManifestRef`
- `IndexRef`
- `ManifestDelta` events
- `IndexDelta` events
- `MountHealth` state

## Required checks
### Identity
- backend fingerprint matches strict/relaxed policy

### Capacity
- mount free space above minimum operational watermark

### Policy
- mount intent class allowed in current workspace/profile

### Readability
- required subtree walk succeeds

## Change detection
Supported strategies:
- periodic scan
- filesystem watch when available
- connector-driven updates
- release-based immutable refresh

## Health states
- `READY`
- `WARMING`
- `DEGRADED`
- `FAILED`

## Event emission
The mount agent MUST emit:
- `mount.ready`
- `mount.degraded`
- `manifest.created`
- `manifest.advanced`
- `index.warming`
- `index.ready`
- `distribution.publish.requested` when enabled

## Recovery behavior
- on restart, restore last checkpoint
- rebuild manifest/index state if checkpoint missing or corrupt
- never silently downgrade strict fingerprint failures
