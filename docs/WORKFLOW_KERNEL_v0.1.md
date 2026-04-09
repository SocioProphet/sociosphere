# Workflow Kernel v0.1

## Purpose

Define the workflow-kernel objects and controller/runtime split for trusted execution across the sociosphere.

## Ownership boundaries

### Owned by sociosphere
- WorkflowSpec
- WorkflowRun
- StepSpec
- ArtifactRef
- ExecutionEnvelope
- ExecutionRecord
- ApprovalRequest
- TrustProfile
- PolicyPack
- workflow fixtures
- workspace-level preflight and compatibility checks

### Owned by mcp-a2a-zero-trust
- AttestationBundle
- PolicyDecision
- Grant
- QuorumProof
- LedgerEvent
- capability registry

### Owned by agentplane
- bundle materialization
- placement
- execution
- receipts
- replay

## Dispatch chain

No side-effecting step may cross a trust boundary without:

`AttestationBundle -> PolicyDecision -> QuorumProof (if required) -> Grant -> Dispatch -> LedgerEvent`

## Projection targets

- MCP tool request
- A2A task request
- deployment/model execution request
- human approval request
- agentplane bundle projection

## Fail-closed rules

- missing trust profile => fail closed
- missing policy pack => fail closed
- missing required trust repos => fail closed
- missing grant/attestation refs for required steps => fail closed

## Capability identity

Capabilities are named using the CapD namespace already present in the workspace:
- `caps.semantic.search_bi`
- `caps.bus.tritrpc`
- `caps.membrane.policy`
- `caps.audit.appendonly`

A digest-bound form may be used where immutable pinning is required.

## Replay / compensation

Replay and compensation are modelled as first-class run phases recorded via:
- WorkflowRun state
- ExecutionRecord phases
- linked ledger events in the trust plane
