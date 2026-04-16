# EMVI ↔ Agent Stack Alignment

Status: Draft v0.1

## Purpose

This document maps EMVI to the platform agent stack so the shell layer is not
mistaken for the planner, policy engine, knowledge substrate, or browser runtime.

## Stack position

EMVI is the **operator shell**.
It owns:
- summon and focus
- grammar and token interpretation
- preview and plan review
- capture into collections/snapshots
- operator-visible routing

EMVI does **not** own:
- planning/decomposition
- policy truth
- graph truth
- runtime placement
- ledger truth
- remote page trust

## Surrounding service families

The shell lowers into stable service families rather than direct implementation details.

- `user` — operator identity, preferences, local context
- `planner` — plan proposal and decomposition
- `policy` — authorization, confirmation, execution gating
- `graph` — symbolic/graph façade, Cypher-friendly query surface
- `knowledge` — ingestion, snippet/page/file interpretation
- `search` — lexical and scoped retrieval
- `shell` — guarded command execution and shell capture
- `network` — fetch, mediation, and external I/O
- `ui_runtime` — local digital-twin rendering/runtime boundary
- `collection` — collection, snapshot, export, membership
- `ledger` — provenance, run package, event visibility
- `placement` — host/LMS/fog/cloud routing and execution locality

## Browser alignment

Browser work is not direct remote-web trust.
Browser-like actions route through:
- `ui_runtime` for local rendering/runtime
- `network` for fetch and transport
- `policy` for trust and permission checks

That means `open page`, `capture page`, `summarize page`, and `submit form` are
local-runtime mediated actions, not arbitrary remote DOM trust.

## Knowledge alignment

Collections, snapshots, annotations, and exports are the shell-facing equivalent
of run-package and provenance-oriented workflow units.

- Collections are mutable operator working sets.
- Snapshots are immutable evidence/handoff units.
- Annotations are the interpretation layer attached to anchors.
- Exports are portable, externalized representations of captured work.

## Placement alignment

Default placement is host-first and offline-first.
Escalation to LMS, fog, or cloud-twin is allowed only when policy, privacy,
resource constraints, or execution requirements demand it.

This prevents accidental cloud assumptions from entering the shell contract.

## Execution-plan rule

EMVI emits ActionSpecs, not raw side effects.
An ActionSpec must identify:
- normalized intent
- target objects
- service-family routing
- trust class
- confirmation requirements
- provenance sink
- placement expectations

## Invariants

1. The shell must remain compatible with host-boundary ownership rules.
2. The shell must not bypass policy for state-changing actions.
3. The shell must not treat UI runtime as graph truth.
4. The shell must not treat planner proposals as execution facts.
5. The shell must make ledger/provenance visible to the operator.
