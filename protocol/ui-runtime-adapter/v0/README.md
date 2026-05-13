# UI Runtime Adapter Protocol v0

Status: draft
Owner: SocioSphere control plane
Origin: rescued SocioProphet platform integration backlog
Tracking issue: https://github.com/SocioProphet/sociosphere/issues/333

## Purpose

This protocol prevents product UI surfaces from being described as live or fully functional when they are backed only by local mock data. Every UI feature that represents platform state, agent state, graph state, ontology state, educational state, telemetry, capture state, or execution state must declare its runtime adapter boundary.

The rule is simple: no SocioProphet UI surface is functional until it has an owning service, typed adapter, fixture payload, error/degraded state, and at least one integration test or replay fixture.

## Scope

This protocol applies to the Vue product UI in `SocioProphet/socioprophet`, including work descended from `mdheller/socioprophet-web`.

It also applies to any future UI extracted into `prophet-ui`, `ui-workbench`, or similar component repos when those surfaces render SocioProphet platform state.

## Non-scope

SocioSphere does not implement downstream product features. SocioSphere owns the adapter protocol, fixture expectations, ownership ledger, and release-readiness checks.

## Required feature declaration

Each UI feature must declare:

| Field | Meaning |
|---|---|
| `feature_id` | Stable feature identifier. |
| `display_name` | Human-readable UI name. |
| `ui_owner_repo` | Repository owning the UI implementation. |
| `service_owner_repo` | Repository owning the live service/runtime contract. |
| `adapter_name` | Typed frontend adapter consumed by the UI. |
| `runtime_state` | `mock`, `fixture`, `live`, `degraded`, `unavailable`, or `retired`. |
| `mock_boundary` | What is simulated, if anything. |
| `fixture_ref` | Path or URI to fixture payloads. |
| `live_contract_ref` | Path, URL, or issue defining the live backend contract. |
| `authz_profile_ref` | Capability/session/grant requirement, where applicable. |
| `integration_test_ref` | Test, replay, or planned test proving the adapter. |
| `evidence_level` | `E0` through `E4`, as defined below. |

## Evidence levels

| Level | Meaning |
|---|---|
| E0 | Mock-only visual component. No runtime contract. Must be labeled mock. |
| E1 | Fixture-backed component with typed adapter boundary. |
| E2 | Contract-backed component with service owner and negative fixtures. |
| E3 | Live adapter works against a local/dev service and has integration tests. |
| E4 | Production-ready adapter with authz, degraded-state handling, telemetry, and release gate coverage. |

A feature may not be called “live,” “working,” or “fully functional” below E3.

A feature may not be called “production-ready” below E4.

## Initial adapter names

The rescued platform backlog identifies these initial adapters:

- `TriTRPCClient`
- `MCPA2ASessionClient`
- `AgentPlaneClient`
- `KnowledgeGraphClient`
- `OntologyClient`
- `CaptureClient`
- `TelemetryClient`
- `EducationDialogueClient`
- `LatticeRuntimeClient`

## Initial feature surfaces

- Graph Universe Explorer
- Domain Ontology Workbench
- Agent Configuration Workbench
- Life Mirror Telemetry Panel
- Cloud Shell / Notebook Launch Surface
- Browser Capture Status and Clip Inbox
- Educational Dialogue Workbench
- Lattice Runtime / Execution Placement Surface

## Ownership fanout

- UI / Vue runtime adapter layer: https://github.com/SocioProphet/socioprophet/issues/323
- AgentPlane runtime contracts: https://github.com/SocioProphet/agentplane/issues/159
- MCP/A2A session and capability grants: https://github.com/SocioProphet/mcp-a2a-zero-trust/issues/6
- Alexandrian Academy educational dialogue runtime: https://github.com/SocioProphet/alexandrian-academy/issues/18
- Ontogenesis ontology validation and promotion contract: https://github.com/SocioProphet/ontogenesis/issues/88
- Lattice/runtime placement assessment: https://github.com/SocioProphet/lattice-forge/issues/16
- Knowledge capture / cryptographic sealing / micro-publication standards: https://github.com/SocioProphet/socioprophet-standards-knowledge/issues/79
- Agent configuration workbench schemas: https://github.com/SocioProphet/socioprophet-agent-standards/issues/23

## Placement rule

Product Vue UI work belongs in `SocioProphet/socioprophet`.

Lattice/runtime work is routed to `SocioProphet/lattice-forge` unless and until a separate `SocioProphet/prophet-lattice` repository exists.

SocioSphere owns only the control-plane protocol, fixture convention, and fanout ledger.
