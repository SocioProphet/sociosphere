# Workspace Content, Query, and Support Choreography

## Purpose

This document defines how `sociosphere` composes and validates the multi-repo workspace needed for governed content, support, premium support, query orchestration, operational intelligence, memory, learning, and bounded execution.

`Sociosphere` is the canonical workspace controller. It owns deterministic repo composition, role registration, runner semantics, topology validation, and cross-repo policy/trust checks.

## Repository role

`Sociosphere` owns:

- workspace manifest and lock state
- deterministic multi-repo materialization
- repo role registration and dependency validation
- topology and trust checks across the repo graph
- orchestration of validation lanes before preview, eval, or release

It does not own feature implementation inside downstream repos.

## Control-loop composition target

The content/query/support control loop requires at minimum these repos in the workspace graph:

- `ontogenesis`
- `socioprophet-standards-storage`
- `sherlock-search`
- `global-devsecops-intelligence`
- `memory-mesh`
- `alexandrian-academy`
- `prophet-platform`
- `agentplane`

Optional or later lanes may include additional standards, policy, or UI repos.

## Choreography stages

### 1. Materialize

The workspace runner should materialize the required repos and revisions from the canonical manifest and lock.

### 2. Validate semantic and contract authority

The workspace should ensure:

- ontology authority comes from `ontogenesis`
- transport/storage/interface authority comes from `socioprophet-standards-storage`
- ops-domain specialization comes from `global-devsecops-intelligence`
- query-plane design comes from `sherlock-search`
- retained memory comes from `memory-mesh`
- learning-objective guidance comes from `alexandrian-academy`
- runtime/eval comes from `prophet-platform`
- execution/evidence comes from `agentplane`

### 3. Preview and evaluation materialization

For any controlled slice, `sociosphere` should be able to materialize a preview/eval workspace that includes the exact repo set and revisions needed to exercise:

- query flows
- support flows
- premium overlay paths
- ops-domain retrieval
- memory writeback / recall
- Academy-backed explanation objects
- bundle execution and evidence emission

### 4. Promotion / release checks

Before promotion, `sociosphere` should validate that topology and trust constraints remain intact across the participating repos.

## Workspace-driven validation lanes

The runner should support or evolve toward explicit lanes such as:

- semantic authority check
- contract authority check
- query plane presence check
- ops-domain processing presence check
- memory integration check
- learning-objective integration check
- execution/evidence path check

## Local overrides

Local overrides remain useful for active development, but they must not obscure canonical repo role ownership or permit invalid dependency inversion.

## Immediate implementation tranche

1. Register the above repo set and role relationships clearly in workspace docs and registry metadata.
2. Add a documentation-level choreography record for this control loop.
3. Ensure future runner checks can validate presence of semantic, contract, query, ops, memory, learning, runtime, and execution lanes.
4. Keep this substrate work separate from ongoing public-site sprint changes.

## Outcome

When implemented correctly, `sociosphere` becomes the deterministic choreography layer that lets the full cross-repo control system be materialized, validated, previewed, and evolved without waiting on final UI alignment.
