# Agentic Workbench Protocol (v1)

This module defines the workflow kernel and governed execution contract for trusted workflow orchestration across the sociosphere.

## Owned here

- WorkflowSpec
- WorkflowRun
- StepSpec
- ArtifactRef
- ExecutionEnvelope
- ExecutionRecord
- ApprovalRequest
- TrustProfile
- PolicyPack
- workspace-level policy packs
- workflow fixtures

## Owned elsewhere

`mcp-a2a-zero-trust` owns:
- AttestationBundle
- PolicyDecision
- Grant
- QuorumProof
- LedgerEvent
- transport-facing capability registry

`agentplane` owns:
- bundle materialization
- placement
- execution
- receipts
- replay

## Invariant

No side-effecting step may cross a trust boundary without a verifiable chain:

`AttestationBundle -> PolicyDecision -> QuorumProof (if required) -> Grant -> Dispatch -> LedgerEvent`

## Capability identity

`StepSpec.capabilityRef` MUST align to CapD identity, for example:

- `capd://caps.semantic.search_bi`
- `capd://caps.bus.tritrpc`
- `capd://caps.membrane.policy`
- `capd://caps.audit.appendonly`

A digest-bound form may also be used for immutable pinning:
- `capd+sha256://caps.semantic.search_bi@<64hex>`

## Projection targets

The workflow kernel compiles to:
- MCP request projections
- A2A task projections
- deployment/model request projections
- human approval requests
- agentplane bundle projections
