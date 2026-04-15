# Tool ABI v1

## Purpose
Define a portable execution contract for tools across local runners, K3s pods, containers, and future execution backends.

## Core rule
A tool does not receive ambient authority.

Every execution must be governed by an explicit `CapabilityGrantSet` tied to:
- mounts
- network profile
- secret scopes
- retention/export policy
- audit/evidence hooks

## Tool descriptor
Each `ToolRef` MUST include:
- `tool_id`
- `tool_version`
- `runtime_type` (`container | pod | wasm | process`)
- `input_schema_ref`
- `output_schema_ref`
- `default_offline_behavior`
- `required_capability_classes[]`
- `emitted_event_types[]`

## Capability classes
### Filesystem
- `mount.read`
- `mount.write`
- `mount.append`
- `mount.index.invalidate`
- `mount.export`

### Network
- `network.none`
- `network.lan`
- `network.tor`
- `network.wan.allowlist`

### Secrets
- `secret.read:<scope>`

### Distribution
- `distribution.publish.manifest`
- `distribution.publish.index`
- `distribution.publish.content`

## Execution request
A `ToolExecutionRequest` MUST include:
- `execution_id`
- `tool_ref`
- `invoker_ref`
- `mount_bindings[]`
- `capability_grants[]`
- `input_payload_ref`
- `network_profile`
- `secret_scope_refs[]`
- `policy_bundle_ref`

## Execution response
A `ToolExecutionResponse` MUST include:
- `execution_id`
- `status`
- `output_payload_ref`
- `artifact_refs[]`
- `emitted_event_refs[]`
- `manifest_delta_refs[]`
- `index_delta_refs[]`
- `warnings[]`

## Offline behavior
Each tool MUST declare one of:
- `must_succeed_offline`
- `degrade_offline`
- `deny_offline`

## Safety defaults
- default network profile is `network.none`
- default secret scope is empty
- tools MAY only publish artifacts covered by policy

## Worked example
A PDF ingest tool may receive:
- read access to canonical mount
- write access to scratch mount
- no network
- no secrets
- permission to emit manifest and index deltas
