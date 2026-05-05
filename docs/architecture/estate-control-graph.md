# SocioProphet Estate Control Graph v0

## Purpose

This document records the current cross-repo control graph for the active SocioProphet estate.

Sociosphere owns this map because it coordinates workspace state, repository roles, cross-repo validation lanes, and adversarial hardening. It does not move feature implementation out of the owning component repositories.

## Current control graph

```text
Agentic PR Control Plane
  -> Diff Hygiene Gate
  -> Sociosphere workspace/materialization controls
  -> Component repo implementation lanes
  -> Evidence, receipt, parity, and promotion artifacts
  -> Post-merge ledger / integration status
```

## Control lanes

### 1. Agentic PR control

Owner: `SocioProphet/agentplane`

Role:
- defines the agentic PR lifecycle
- represents work orders as evidence-producing execution units
- separates implementation, review, merge, and ledger authority

Current anchor:
- Agentic PR Control Plane v0

### 2. Diff hygiene gate

Owner: `SocioProphet/policy-fabric`

Role:
- blocks polluted diffs before review and merge
- rejects denied generated paths such as `.venv/`, `.venv-tools/`, `node_modules/`, caches, and build output
- requires PR-body evidence, scoped changed paths, and expected head/base state

Current anchors:
- Diff Hygiene Gate v0 contract
- Diff Hygiene Gate validator wired into `make validate`

### 3. FogStack deployment parity and live preflight

Owner: `SocioProphet/prophet-platform`

Role:
- owns FogStack runtime/deploy evidence records
- maintains local demo, deploy plan, GitOps bundle, runtime adapter, dry-run, parity readiness, and live preflight proof paths
- forbids live cluster mutation by default

Current safety invariants:
- `read-only-live-preflight`
- `live_apply_allowed=false`
- `mutated_cluster=false`
- human approval required before any live apply path

### 4. Identity/auth proof ingress

Owner: `SocioProphet/prophet-platform`

Upstream standard owner: `SocioProphet/socioprophet-agent-standards`

Role:
- consumes pinned agent authentication standards
- defines platform-facing identity contracts
- prepares the first `identity-prime` proof-ingress seam

Current anchors:
- `IdentitySubjectContext`
- `IdentitySessionContext`
- `IdentityProofIngressRecord`
- generated examples and validation helper

### 5. Semantic hyperknowledge / SHIR

Spec owner: `SocioProphet/ontogenesis`

Execution-pack owner: `SocioProphet/prophet-platform-fabric-mlops-ts-suite`

Serde/schema owner: `SocioProphet/semantic-serdes`

Role:
- defines SHIR as the semantic hyperknowledge intermediate representation
- compiles bounded RDF/Turtle inputs to SHIR artifacts
- records projection, evidence, receipt, and future graph-ML lowering boundaries

Current anchors:
- SHIR v0.1 spec
- `rdf-to-shir` pack v0.1

### 6. Michael machine-science execution

Standards owner: `SocioProphet/socioprophet-agent-standards`

Semantic owner: `SocioProphet/ontogenesis`

Instance owner: `SocioProphet/gaia-world-model`

Governance/runtime owner: `SocioProphet/prophet-platform`

Execution-pack owner: `SocioProphet/prophet-platform-fabric-mlops-ts-suite`

Role:
- machine-science agent with symbolic/neuro-symbolic deduction, probabilistic-relational abduction, and symbolic-regression induction
- emits plans, run records, status transitions, dry-run execution records, and governed attribution deltas
- must not bypass identity, policy, SHIR, or receipt controls

Current anchors:
- Michael profile and conformance
- Michael epistemic and twin ontology modules
- machine-science schemas and attribution deltas
- Michael packs/gates
- workflow template, submission, plan, run record, status transition, dry-run execution record, and CI validation

### 7. Lattice / GAIA / governed data-runtime lane

Platform owner: `SocioProphet/prophet-platform`

Execution owner: `SocioProphet/prophet-platform-fabric-mlops-ts-suite`

Policy owner: `SocioProphet/policy-fabric`

Spec owner: `SourceOS-Linux/sourceos-spec`

World-model owner: `SocioProphet/gaia-world-model`

Role:
- carries Data/GovernAI contracts, runtime profiles, governed Ray/Beam execution fixtures, promotion evidence, and GAIA bounded ingest surfaces
- keeps fixture/demo lanes separate from production serving claims

Current anchors:
- Lattice Data/GovernAI contract tranche
- RuntimeAsset promotion evidence
- governed Ray/Beam replay evidence
- bounded OSM ingest and GAIA layer catalog bridge

### 8. Open office runtime lane

Platform owner: `SocioProphet/prophet-platform`

Host/product surfaces:
- `SourceOS-Linux/sourceos-shell`
- `SourceOS-Linux/TurtleTerm`
- `SourceOS-Linux/BearBrowser`

Role:
- owns open WOPI/saveback runtime contracts
- keeps closed providers quarantined as disabled-by-default compatibility/import/export surfaces
- prevents Google Workspace, Microsoft 365, Microsoft Graph, Apple iCloud, and Apple Notes from becoming default runtime dependencies or canonical authority

Current anchors:
- office version record
- office writeback record
- office policy decision record
- office adapter profile

## Binding rules

1. Implementation stays in the owning component repo.
2. Sociosphere records cross-repo control graph, topology, validation, and hardening posture.
3. Agentic work must pass through AgentPlane work-order semantics and Policy Fabric diff hygiene before merge.
4. Identity-sensitive execution must go through identity proof-ingress contracts before runtime authority is granted.
5. Semantic projection work must account for SHIR projection/loss boundaries before graph-ML lowering or ontology promotion.
6. FogStack deployment parity must preserve non-mutating preflight evidence until human-approved live apply is explicitly added.
7. Michael execution must consume the common evidence, policy, identity, and SHIR control surfaces rather than defining a parallel governance stack.

## Immediate backlog

1. Add `identity-prime` proof-ingress emitter seam in `prophet-platform`.
2. Add projection-loss accounting follow-up for `rdf-to-shir` before SHIR-to-graph-ML lowering.
3. Extend Michael execution records with external receipt refs compatible with eval-fabric / FogStack evidence style.
4. Add Sociosphere topology/dependency checks that recognize the control graph edges in this document.
5. Keep Diff Hygiene Gate enforcement in the pre-review and pre-merge path for all agent-authored PRs.
