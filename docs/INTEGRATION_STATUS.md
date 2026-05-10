# Integration Status

This file is the canonical current-state ledger for cross-repo integration
facts that were previously repeated in multiple places.

## Current state

### TritRPC
- Canonical upstream: `SocioProphet/TriTRPC`
- Workspace declaration: `manifest/workspace.toml` repo `tritrpc`
- Materialization path: `third_party/tritrpc`
- Status: active workspace dependency

### Trit-to-Trust
- Status: removed as an independent workspace dependency
- Notes/content: folded into TritRPC docs during de-commingling

### Edge capabilities upstream bindings
- Narrative binding doc: `docs/architecture/upstream-bindings-edge-capabilities.md`
- Machine-readable baseline map: `registry/upstream-bindings-edge-capabilities.yaml`
- Drift check tool: `tools/check_upstream_edge_capabilities.py`
- Airshare baseline: `KuroLabs/Airshare master @ 92a144dbf7af2d2a5fbcfbfb3078f4c9ecf86c13`
- cdncheck baseline: `projectdiscovery/cdncheck main @ 68bfbae83a4aad30d9cbb17c30bb44c32e10affb`
- papers baseline: `marawangamal/papers main @ 1ae5061b7ec9d2ab7d0e37ad254ad435a58fc5ec`
- Fast-LLM baseline: `ServiceNow/Fast-LLM main @ 7a7129d7775cea459cb19a48be0d831ccc7b4e7d`
- Status: captured in repo; policy disposition lives in the architecture note and operational baseline lives in the registry + drift check tool

### Agent harness delivery routing
- Routing doc: `docs/integration/agent-harness-delivery-routing.md`
- Delivery/performance authority: `SocioProphet/delivery-excellence`
- Delivery automation authority: `SocioProphet/delivery-excellence-automation`
- Runtime evidence producer: `SocioProphet/agentplane`
- Policy/guardrail producers: `SocioProphet/policy-fabric`, `SocioProphet/guardrail-fabric`
- Memory/context producer: `SocioProphet/memory-mesh`
- Browser and terminal producers: `SourceOS-Linux/BearBrowser`, `SourceOS-Linux/TurtleTerm`, `SourceOS-Linux/agent-term`
- Security validation producer: `SocioProphet/SCOPE-D`
- Status: routing captured in repo; Delivery Excellence owns scoreboards, KPI/OKR definitions, customer-proof readouts, and operating cadence; SocioSphere owns topology and must not duplicate scoreboards

## Resolved migration timeline

| Stage | Snapshot |
|---|---|
| Initial coupling | `tritrpc` + `trit-to-trust` tracked together |
| First pinning pass | both pinned at `v0.1.0` |
| Second pinning pass | `tritrpc v0.1.1 @ 6091e55`, `trit-to-trust v0.1.1 @ 68186ab` |
| De-commingled state | TritRPC retained, Trit-to-Trust removed from workspace deps |
| Current steady state | TritRPC remains as standalone core dependency |

## Interpretation rule

If another document references Trit-to-Trust as an active workspace dependency,
treat that content as historical context. Current behavior is defined by
`manifest/workspace.toml` + `manifest/workspace.lock.json`.

For edge-capability upstreams, treat the registry file plus drift-check tool as
the operational baseline, and treat the narrative binding doc as the policy /
disposition explanation.

For agent harness delivery routing, treat `docs/integration/agent-harness-delivery-routing.md`
as the topology and boundary source. Delivery Excellence remains the performance,
scoreboard, KPI/OKR, work packaging, and customer-proof authority.
