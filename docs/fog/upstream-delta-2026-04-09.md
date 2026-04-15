# Fog upstream delta — 2026-04-09

This note records the upstream changes observed after the initial Fog pack bootstrap work landed.

## What changed upstream

### `SocioProphet/sociosphere`
Recent merged work strengthened the shared meta/workspace lane:
- workflow trust / agentic workbench v1
- local hybrid smoke runner
- scheduler orchestration / automation framework work
- validation, registry, topology, and workspace checks

**Implication:** `sociosphere` is now more clearly the cross-pack governance and workspace-control surface. Fog pack repos should consume these shared workflow/workspace patterns rather than duplicate them.

### `SocioProphet/agentplane`
Recent merged work strengthened the shared agent runtime lane:
- trust integration scaffolding and execution envelope contract
- runtime receipt promotion / local receipt builder
- durablegraph runtime skeleton
- semantic-proof consumer bridge

**Implication:** `fog-pack-data`, `fog-pack-business-automation`, and `fog-pack-aiops` should treat `agentplane` as the shared runtime/control-plane dependency. Pack repos should not fork runtime envelope, receipt, proof-consumer, or durablegraph ownership.

### `SocioProphet/TriTRPC`
Recent merged work strengthened the shared protocol lane:
- local-hybrid slice method/fixture pack
- semantic-proof transport bridge
- branch/PR integration audit tooling and CI hardening
- AOKC descriptor/order transport notes

**Implication:** transport methods, protocol slices, and wire-facing fixture canon remain in `TriTRPC`. Fog pack repos should consume protocol surfaces, not restate them as pack-local canon.

## Net effect on Fog repo plan
The 7-pack repo topology still stands.

What changes is the **import discipline**:
- `fog-pack-data` should import/use shared protocol/runtime/workspace surfaces from `TriTRPC`, `agentplane`, and `sociosphere`
- `fog-pack-data` should own data distro packaging, release manifests, BOM, profiles, lake/catalog/knowledge/trust composition, and pack-local overlays
- shared foundations should continue to evolve independently and remain outside the 7-pack count

## Immediate consequence
Before importing more staged artifacts into `fog-pack-data`, prefer references, pins, and dependency notes over copying shared-foundation materials.
