# Protocol

The workspace controller is the canonical home for shared protocol schemas, fixture vectors, and adapter/workbench contract tests.

## Active protocol roots

- `protocol/agentic-workbench/v0/` — legacy governed artifact lifecycle surface
- `protocol/agentic-workbench/v1/` — active workflow-kernel, trust-profile, and policy-pack surface

## Ownership boundaries

- `sociosphere/protocol/agentic-workbench/v1/*` owns workflow orchestration objects and workspace-level trust profiles/policy packs.
- `mcp-a2a-zero-trust` owns canonical trust objects and the transport-facing capability registry.
- `agentplane` owns static bundle execution contracts, runtime dispatch, receipts, and replay.

## Compatibility and fixtures

Fixture vectors under `protocol/agentic-workbench/v1/fixtures/` are the canonical inputs for workflow-kernel contract tests and controller preflight validation.

## Runner integration

The workspace controller exposes preflight gates:

- `runner validate-policy`
- `runner validate-trust`
- `runner trust-report`

These commands are the workspace-level policy and trust integrity checks.
