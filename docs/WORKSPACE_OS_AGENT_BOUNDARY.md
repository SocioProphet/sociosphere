# Workspace, OS, and Agent-Plane Boundary

This document clarifies what belongs in `SocioProphet/sociosphere` rather than drifting into product repositories such as `SocioProphet/socioprophet`.

## Why this document exists

Repo boundaries are part of governance.
If cross-repo orchestration doctrine, workspace-controller doctrine, runtime substrate doctrine, and product doctrine all pile into the same place, the system becomes harder to reason about and easier to misgovern.

Sociosphere should be the home for the cross-repo layer.

## What belongs here

The following concerns are primarily **Sociosphere concerns** when they are cross-repo rather than product-local:

- workspace controller doctrine
- repo composition and materialization rules
- lock, manifest, and reproducibility doctrine
- OS and runtime substrate expectations for the development and execution environment
- agent-plane orchestration boundaries across repos
- capability routing and execution-scoping doctrine for shared workspace flows
- transport or protocol doctrine when it governs multiple component repos rather than one product surface
- evidence requirements for workspace-level mutation, rollout, and replay

## What does not belong here

Sociosphere is not where product-specific user experience doctrine should accumulate.
Product repos should still own their own constitutional layer for:

- user-facing governance surfaces
- product moderation and appeals
- evidence views specific to that product
- product data publication boundaries
- product feature acceptance criteria

## Product vs workspace split

### `SocioProphet/socioprophet`
Owns the SocioProphet product doctrine:
- evidence before authority in product surfaces
- privacy for persons and transparency for power in product behavior
- replay and appeal expectations for product workflows
- product-facing spec stubs and acceptance criteria

### `SocioProphet/sociosphere`
Owns the shared orchestration layer:
- how repos compose into one workspace
- how execution is made reproducible
- how agent or automation surfaces are scoped across repos
- how workspace policy and evidence apply across component boundaries
- how runtime substrate expectations are documented at the workspace level

## Cross-repo primitives

At the workspace/controller layer, several primitives matter across repositories:

1. content-addressed artifacts and durable references
2. explicit manifests and locked revisions
3. replayable workspace actions
4. least-privilege execution and bounded automation
5. visible evidence for consequential shared-repo mutations

These are broader than any single product and should therefore live here.

## Immediate implication for cleanup

When doctrine text in a product repo starts expanding into:
- SourceOS or OS-substrate theory
- broad agent-plane orchestration rules
- workspace controller semantics
- repo-topology doctrine
- cross-repo capability or transport governance

that text should be moved or restated here.

## Interface with product repos

The cleaner pattern is:
- product repos keep product doctrine
- Sociosphere keeps cross-repo orchestration doctrine
- both sides link across the boundary explicitly instead of smearing concepts together

That yields clearer ownership, cleaner pull requests, and fewer ontology leaks.

## Backlog

1. Add explicit references from product repos to this boundary doc where appropriate.
2. Expand workspace-level doctrine into concrete policy and replay contracts.
3. Define how agent-plane and OS-substrate expectations map onto manifest, lock, runner, and protocol surfaces.
4. Keep product doctrine out of Sociosphere unless the concern truly spans repositories.
