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

The workspace controller relies on runner-supported workflows for workspace operations.

Policy and trust integrity checks remain workspace-level concerns, but they are not currently exposed here as dedicated `runner validate-policy`, `runner validate-trust`, or `runner trust-report` subcommands.

Keep this document aligned with the commands actually implemented by `tools/runner/runner.py`.
