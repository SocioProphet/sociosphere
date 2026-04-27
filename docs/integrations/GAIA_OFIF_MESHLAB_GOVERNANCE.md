# GAIA / OFIF / MeshLab Governance Integration

Status: v0 governance contract

## Purpose

SocioSphere is the governance and workspace-controller authority for the GAIA / OFIF / MeshLab / Control Tower program.

The program spans multiple repositories. SocioSphere does not own feature implementation inside those repositories; it owns registration, topology, validation gates, change propagation, source-exposure safety, and readiness reporting.

## Governed repositories

Initial governed set:

- `SocioProphet/prophet-platform`
- `SocioProphet/gaia-world-model`
- `SocioProphet/orion-field-intelligence`
- `SocioProphet/sherlock-search`
- `SocioProphet/lattice-forge`
- `SocioProphet/lampstand`
- `SocioProphet/meshrush`
- `SocioProphet/agentplane`
- `SociOS-Linux/nlboot`

## Governance doctrine

```text
Domain repo changes
  -> contract/schema/fixture validation
  -> source-exposure check
  -> topology/dependency check
  -> progress ledger update
  -> readiness signal
```

No cross-repo integration is considered ready until its owning repository has:

1. a named contract or schema;
2. at least one fixture where appropriate;
3. dependency-light validation or CI coverage where possible;
4. clear authority boundaries;
5. source-exposure safety posture;
6. progress ledger update in `prophet-platform`.

## Validation lanes

### Lane 1 — GAIA contract fixtures

Repository: `SocioProphet/gaia-world-model`

Required checks:

- contract fixture validator;
- OFIF-to-GAIA bridge proof;
- bridge invariant check;
- soil-intelligence fusion proof;
- control-tower anomaly output proof.

### Lane 2 — Sherlock discovery records

Repository: `SocioProphet/sherlock-search`

Required checks:

- geospatial/evidence result schema validation;
- decision-card fixture validation;
- mesh-experiment result validation.

### Lane 3 — MeshRush graph artifacts

Repository: `SocioProphet/meshrush`

Required checks:

- crystallization fixture validation;
- graph-view integration docs present;
- advisory/action boundary preserved.

### Lane 4 — Agentplane execution candidates

Repository: `SocioProphet/agentplane`

Required checks:

- MeshRush execution candidate schema;
- advisory candidate fixture;
- candidate validator;
- CI success;
- non-runnable advisory semantics preserved.

### Lane 5 — Lattice Forge runtime admission

Repository: `SocioProphet/lattice-forge`

Required checks before any runtime asset is added:

- executable runtime entrypoint exists in owning domain repo;
- validation command exists;
- policy constraints and rollback semantics are explicit;
- at least one fixture passes validation;
- runtime boundary has been reviewed.

### Lane 6 — Smart Spaces domain-home decision

Repository: undecided

Required checks before implementation:

- domain-home decision closed or narrowed;
- privacy/surveillance risk requirements defined;
- event authority split between GAIA/OFIF/SocioSphere/future repo documented;
- no speculative runtime fixtures added prematurely.

## Readiness states

- `planned`: strategy or doctrine only.
- `contracted`: schema/contract exists.
- `fixture-backed`: one or more fixtures exist.
- `validated`: fixture validator or CI exists.
- `executable`: deterministic executable proof exists.
- `admission-ready`: ready for runtime packaging or cross-repo consumption.
- `blocked`: explicit unresolved dependency or policy issue.

## Current readiness snapshot

| Workstream | State |
| --- | --- |
| GAIA / OFIF soil proof | executable |
| Control tower anomaly proof | executable |
| Sherlock geospatial/evidence records | validated |
| MeshRush crystallization fixture | validated |
| Agentplane MeshRush adapter | PR-open / validated-on-branch |
| Lattice Forge runtime assets | blocked until runtime admission criteria are met |
| Smart Spaces / Built Environment | planned / domain-home-open |

## SocioSphere responsibilities

1. Track repo topology and dependency direction.
2. Ensure cross-repo contracts do not create cyclic authority confusion.
3. Enforce source-exposure and publication-safety checks.
4. Register program capability states.
5. Track validation readiness across repositories.
6. Notify affected repos when schemas/contracts change.
7. Keep the master plan and progress ledger aligned.

## Non-goals

- SocioSphere does not implement GAIA world-model logic.
- SocioSphere does not own OFIF event schemas.
- SocioSphere does not define MeshRush traversal semantics.
- SocioSphere does not package Lattice runtimes.
- SocioSphere does not decide Smart Spaces domain home without explicit architecture review.
