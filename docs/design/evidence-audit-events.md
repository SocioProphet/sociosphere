# Evidence and audit event schema

## Purpose
Define the minimum event surface needed to audit mount, index, connector, tool, and governance behavior.

## Event envelope
Every event MUST include:
- `event_id`
- `event_type`
- `occurred_at`
- `actor_ref`
- `workspace_ref`
- `dataset_ref` (when applicable)
- `policy_bundle_ref`
- `correlation_id`
- `payload_ref` or inline canonical payload
- optional `signature_ref`

## Core event families
### Mount events
- `mount.ready`
- `mount.degraded`
- `mount.failed`

### Manifest events
- `manifest.created`
- `manifest.advanced`
- `manifest.tombstone_applied`

### Index events
- `index.warming`
- `index.ready`
- `index.degraded`

### Connector events
- `connector.scan.started`
- `connector.scan.completed`
- `connector.fetch.completed`
- `connector.push.completed`
- `connector.conflict.detected`

### Tool events
- `tool.execution.started`
- `tool.execution.completed`
- `tool.execution.denied`

### Governance events
- `quorum.proposal.created`
- `quorum.approval.recorded`
- `quorum.commit.applied`

## Evidence requirements
For state-changing events, the payload SHOULD include refs to:
- prior manifest/index state
- resulting manifest/index state
- artifacts created
- policy decision records

## Retention guidance
- governance and destructive actions: keep-until-deleted-by-policy or legal hold
- operational transient events: policy-driven TTL

## Follow-on work
- canonical wire encoding
- signing profile
- event correlation rules across connectors and tools
