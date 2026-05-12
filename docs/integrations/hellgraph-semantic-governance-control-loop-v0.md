# HellGraph Semantic Governance Control Loop v0

## Status

Integration directive. This document turns the refreshed upstream-repo view into the first executable semantic-governance control slice for SocioProphet and SourceOS.

The current platform already has the relevant organs:

- `SocioProphet/hellgraph` — graph-store substrate for the semantic link graph.
- `SocioProphet/ontogenesis` — vocabulary, ontology, SHACL/JSON-LD, and semantic-module authority.
- `SocioProphet/sociosphere` — workspace registry, orchestration, validation, and admission control.
- `SocioProphet/policy-fabric` — authored policy, compiled plans, release packs, and validation evidence.
- `SocioProphet/agentplane` — governed execution, run receipts, replay, and evidence sealing.
- `SocioProphet/prophet-platform` — platform APIs, schema surfaces, provenance, evaluation, and product integration.
- `SocioProphet/slash-topics`, `SocioProphet/new-hope`, and `SocioProphet/sherlock-search` — semantic routing, membrane integration, and search activation.
- `SourceOS-Linux/sourceos-syncd`, `SourceOS-Linux/TurtleTerm`, `SourceOS-Linux/BearBrowser`, and `SourceOS-Linux/librewolf-source-mirror` — active SourceOS surfaces that must consume the same semantic governance loop.

The goal is not another abstract ontology pass. The goal is a fail-closed semantic control loop that proves every governed asset has meaning, lineage, policy, quality state, execution evidence, and replayable receipt material.

## Claim boundary

This v0 slice does not claim platform-wide completion. It defines the first enforceable loop. It is acceptable when one governed asset can move through semantic activation, graph persistence, policy binding, execution receipt, and release/admission validation without manual side channels.

## Control-loop thesis

A SocioProphet asset is not release-ready until it has five mandatory semantic edges:

1. `lg:represents` — asset or field represents a business/domain term.
2. `lg:derivedFrom` — asset is derived from an upstream source, transform, repo, model, run, or authoritative origin.
3. `lg:conformsTo` — asset conforms to a technical profile, schema, contract, or shape.
4. `lg:governedBy` — asset or term is bound to an applicable policy object.
5. `lg:hasQualitySignal` — asset or term is bound to a current quality/evidence signal.

Missing required edges are not warnings in governed namespaces. They are admission failures.

## Repository ownership

### HellGraph

HellGraph owns graph persistence and query execution for the semantic link graph. It must expose a minimal store/query surface for:

- semantic nodes,
- semantic edges,
- edge provenance,
- receipt references,
- graph snapshots,
- graph diff queries,
- replay lookup by `ingestion_run_id`, `receipt_id`, or `asset_id`.

HellGraph does not author vocabulary. It stores and serves the graph.

### Ontogenesis

Ontogenesis owns the vocabulary and shape layer:

- BO namespace: `bo:*` business/domain terms.
- TO namespace: `to:*` technical profiles and schema identities.
- LG namespace: `lg:*` predicates and edge semantics.
- CT namespace: `ct:*` candidate terms.
- SHACL or equivalent validation for mandatory node and edge shapes.
- JSON-LD contexts for API/runtime interchange.

### SocioSphere

SocioSphere owns workspace admission and control-plane validation:

- register the semantic-governance control loop,
- validate that repos declare their semantic role,
- validate that governed assets expose semantic activation records,
- fail release/admission when mandatory graph evidence is absent,
- coordinate affected repos through workspace check targets.

### Policy Fabric

Policy Fabric owns semantic policy profiles:

- `profile:semantic_first@1.0.0`, required for staging/prod governed surfaces,
- `profile:technical_only@0.1.0`, allowed only for sandbox/dev and expiring by default,
- policy binding requirements for PII, retention, residency, provenance, release, and replay,
- denial/review states for missing or conflicting semantic edges.

### AgentPlane

AgentPlane owns execution evidence and receipt sealing:

- consume a semantic activation bundle,
- run the assigned validator/executor bundle,
- emit run artifacts,
- preserve replay lineage,
- seal a `SemanticActivationReceipt`,
- fail closed when required evidence is missing.

### Prophet Platform

Prophet Platform owns user-facing and API-facing integration:

- semantic activation API,
- asset registration and lookup,
- schema/technical-profile API,
- semantic diff API,
- provenance and replay API,
- product dashboard surfaces.

### Slash Topics / New Hope / Sherlock Search

These consume the graph:

- slash-topics maps terms and topic packs onto routing/membrane decisions,
- New Hope consumes semantic edges as membrane constraints,
- Sherlock Search indexes graph-backed semantic state and evidence refs.

### SourceOS surfaces

SourceOS consumers must treat semantic governance as the workstation and OS coordination substrate:

- `sourceos-syncd` consumes graph-backed object/actor/schema/provenance state,
- `TurtleTerm` and `agent-term` expose governed agent workflow state,
- `BearBrowser` and `browser-use` consume policy-bound browser automation semantics,
- `librewolf-source-mirror` remains a clean upstream mirror; SourceOS changes belong in overlay/product repos.

## Minimum object model

### SemanticAsset

Required fields:

- `asset_id`
- `asset_kind`
- `namespace`
- `owner_repo`
- `release_state`
- `observed_at`
- `ingestion_run_id`
- `provenance_hash`

### BusinessTerm

Required fields:

- `term_id`
- `surface_form`
- `canonical_label`
- `domain`
- `version`
- `status`
- `asserted_at`

### TechnicalProfile

Required fields:

- `profile_id`
- `profile_kind`
- `schema_hash`
- `version`
- `compatibility`

### LinkEdge

Required fields:

- `edge_id`
- `subject_id`
- `predicate_id`
- `object_id`
- `confidence`
- `assertion_source`
- `observed_at`
- `asserted_at`
- `ingestion_run_id`
- `provenance_hash`

### CandidateTerm

Required fields:

- `candidate_id`
- `surface_form`
- `context_window`
- `confidence`
- `evidence_spans`
- `proposer_run_id`
- `first_seen_at`
- `last_seen_at`

### AssignmentProposal

Required fields:

- `proposal_id`
- `asset_id`
- `field_fqn`
- `top_k_terms`
- `confidences`
- `evidence_spans`
- `policy_hits`
- `provenance_hash`

### PromotionRecord

Required fields:

- `promotion_record_id`
- `proposal_id`
- `decision`
- `curator_id`
- `asserted_at`
- `decision_hash`

### SemanticActivationReceipt

Required fields:

- `receipt_id`
- `asset_id`
- `ingestion_run_id`
- `graph_snapshot_id`
- `policy_bundle_id`
- `quality_snapshot_id`
- `executor_id`
- `run_artifact_refs`
- `replay_artifact_ref`
- `receipt_hash`

## v0 ingest loop

1. Asset enters governed ingest.
2. Prophet Platform emits or accepts an asset registration envelope.
3. Ontogenesis supplies BO/TO/LG/CT context and validation shapes.
4. Term assignment proposes or writes `lg:represents` edges.
5. Technical-profile validation writes `lg:conformsTo` or quarantines the asset.
6. Lineage capture writes `lg:derivedFrom`.
7. Policy Fabric resolves and writes `lg:governedBy`.
8. Quality/evidence evaluation writes `lg:hasQualitySignal`.
9. HellGraph persists the graph snapshot.
10. AgentPlane executes the validator bundle and seals a `SemanticActivationReceipt`.
11. SocioSphere admission checks the receipt and graph evidence.
12. Release proceeds only if `profile:semantic_first@1.0.0` passes.

## Failure semantics

The following are hard failures in staging/prod governed namespaces:

- missing `lg:represents`,
- missing `lg:governedBy`,
- missing `lg:conformsTo`,
- missing lineage or authoritative-origin declaration,
- missing quality signal when a policy requires one,
- candidate term not generated for an unmapped field,
- policy conflict without explicit approval,
- receipt missing replay material,
- graph snapshot missing provenance hash.

## First acceptance target

The first acceptance test should use a single representative platform asset, preferably an API/schema artifact from `prophet-platform` or a semantic contract from `semantic-serdes`.

Done means:

- Ontogenesis defines the needed terms, technical profile, and predicate shapes.
- Prophet Platform emits the asset activation envelope.
- Policy Fabric resolves policy bindings.
- HellGraph stores the nodes and five mandatory edges.
- AgentPlane emits a sealed semantic activation receipt.
- SocioSphere fails the release when any required edge is removed.
- Sherlock Search can retrieve the asset by business term, technical profile, policy, and receipt id.

## Initial implementation issues

Open or link issues in:

- `SocioProphet/hellgraph`: implement graph persistence/query surface for semantic nodes, edges, snapshots, and receipts.
- `SocioProphet/ontogenesis`: define BO/TO/LG/CT vocabularies and shapes for v0.
- `SocioProphet/policy-fabric`: define `semantic_first` and `technical_only` profiles and enforcement policies.
- `SocioProphet/agentplane`: define and validate `SemanticActivationReceipt` execution artifacts.
- `SocioProphet/prophet-platform`: emit semantic activation envelopes and semantic diff API.
- `SocioProphet/sociosphere`: add workspace admission target and fail-closed fixture.
- `SocioProphet/sherlock-search`: index graph-backed semantic evidence.
- `SourceOS-Linux/sourceos-syncd`: consume semantic graph state as object/actor/schema/provenance substrate.

## Non-goals for v0

- No universal migration of every repo.
- No replacement of existing ontology work.
- No claim that HellGraph is the only possible graph backend forever.
- No mutation of clean upstream mirrors such as `librewolf-source-mirror` for SourceOS product policy.
- No implicit promotion of candidate terms without audit.

## Governance rule

If an object is important enough to ship, it is important enough to name, link, govern, measure, and replay.
