# Identity Is Prime × Regis × ACR × Sociosphere Integration

Issue: https://github.com/SocioProphet/sociosphere/issues/284

## Purpose

This document defines the Sociosphere integration spine for the Identity Is Prime reference implementation, Regis Entity Graph, Authority Concordance Rex (ACR), Agent Registry, Holmes, and Sherlock Search. Sociosphere is the cross-repo workspace controller: it pins repositories, executes validation, records conformance, and provides deterministic retest lanes.

The integration is not a centralized lakehouse design. The runtime target is local-first and cache-first: assertion cache, crosswalk cache, golden projection cache, delta cursors, proof artifacts, and certificate ledgers. Sociosphere coordinates the workspace and retest evidence; it does not become the data warehouse.

## Architectural hierarchy

1. Identity Is Prime is the doctrine and reference implementation. It defines prime-topic identity, Event-IR, policy polytopes, congruence lanes, non-escape semantics, proof artifacts, and fog-first deployment.
2. Regis Entity Graph is the graph implementation surface. It stores canonical entities, source records, identity states, concordance links, transition edges, decision ledger entries, and proof certificates.
3. ACR is the authority concordance service profile. It owns versioned authority templates, connector schema evolution, entity resolution, crosswalks, golden projections, and point-in-time proofs.
4. Holmes is the investigative/evidence-reasoning layer for Regis. It should consume Regis graph state, proof artifacts, ledger entries, policy decisions, and contradiction/refutation events to form explainable investigative cases.
5. Sherlock Search is the retrieval and search surface for Regis/Holmes evidence. It should index entities, events, assertions, certificates, source records, crosswalks, and decision-ledger entries without becoming canonical truth.
6. Agent Registry declares the agents that observe, normalize, classify, resolve, retrieve, reason, prove, and audit. Agents submit observations, search results, decisions, proposed graph mutations, and certificates. They do not free-write canonical truth.
7. Sociosphere coordinates and retests the full estate through its manifest, lock file, runner, workspace policy, and protocol fixtures.

## Existing upstream anchors

The Sociosphere manifest already contains the following relevant repositories:

- `identity-is-prime-reference`
- `regis-entity-graph`
- `tritrpc`
- `agentplane`
- `human_digital_twin`
- `ontogenesis`
- `socioprophet_standards_storage`
- `sourceos-spec`
- `policy-fabric`

The manifest should also include `agent-registry`, `holmes`, and `sherlock-search` as first-class components or focused lane overlay entries if they are not already materialized through another repo entry.

## Integration contracts

### Identity Is Prime reference

The reference repo provides the normative behavior for:

- Event-IR ingestion
- fog-first scope classes
- prime-topic labeling
- policy-constrained entity resolution
- policy polytope checks
- congruence lanes for modular evidence
- proof artifact production
- zeta-style identity-state audit metrics

### Regis Entity Graph

Regis consumes Identity Is Prime as graph semantics. Required graph object families:

- `CanonicalEntity`
- `SourceRecord`
- `ConcordanceLink`
- `DecisionLedgerEntry`
- `IdentityPrime`
- `ScopeFlag`
- `IdentityState`
- `IdentityMixture`
- `IdentityPolytope`
- `WorldlineEvent`
- `AdmissibleTransition`
- `TokenLane`
- `ProofCertificate`
- `TransitionCertificate`
- `NonEscapeCertificate`
- `ConcordanceDecisionCertificate`
- `SearchIndexRecord`
- `InvestigationCase`
- `EvidenceFinding`

### Holmes reasoning layer

Holmes should be the Regis-native investigative reasoning surface. Its responsibilities are:

- consume Regis graph snapshots and ledger/certificate pointers
- assemble evidence findings into investigation cases
- explain why a linkage was verified, refuted, undecidable, stale, or review-bound
- detect contradictions across ACR concordance, identity polytope policy, token non-escape, and source assertions
- emit proposed graph annotations or case findings, not canonical truth

Holmes outputs must be reducible to Regis evidence objects and must carry policy/schema/resolver/template version pins.

### Sherlock Search retrieval layer

Sherlock Search should be the retrieval layer for evidence discovery and operator/user query. Its responsibilities are:

- index canonical entities, source records, identity states, worldline events, ledger entries, certificates, and Holmes findings
- provide search over proof and evidence surfaces
- return cited graph pointers, source pointers, and ledger pointers
- support delta indexing for local-first/cache-first runtime
- avoid writing canonical entity truth directly

Sherlock Search should be treated as an indexing and retrieval adapter for Regis/Holmes, not as the system of record.

### ACR service profile

ACR supplies mastered entity truth and proof-carrying concordance:

- authority template versions
- connector schema versions
- schema migration records
- source assertions
- source-to-canonical crosswalks
- golden record projections
- point-in-time golden record proofs
- template migration simulations

### Agent Registry

Required agent families:

- `prime-topic-agent`
- `identity-polytope-agent`
- `transition-graph-agent`
- `congruence-non-escape-agent`
- `zeta-audit-agent`
- `acr-template-agent`
- `acr-connector-agent`
- `acr-concordance-agent`
- `acr-golden-projection-agent`
- `regis-proof-agent`
- `regis-policy-agent`
- `regis-steward-agent`
- `holmes-case-agent`
- `holmes-contradiction-agent`
- `sherlock-index-agent`
- `sherlock-query-agent`

Each manifest must declare input schemas, output schemas, graph write permissions, policy scopes, TRIT RPC bindings, retrieval permissions, and evidence outputs. A manifest that lacks the required policy scope or graph/search permission must be rejected by conformance.

## Sociosphere conformance lanes

The Sociosphere retest controller should expose these lanes:

1. `identity-prime-schema`: validates Identity Is Prime fixtures and schemas.
2. `identity-prime-policy`: evaluates polytope membership and forbidden mixtures.
3. `identity-prime-transition`: validates admissible transition and no-path cases.
4. `identity-prime-token`: validates congruence and token non-escape cases.
5. `identity-prime-audit`: validates zeta-style identity audit summaries.
6. `regis-graph-contracts`: validates Regis graph objects and proof certificate pointers.
7. `holmes-case-contracts`: validates Holmes case/finding outputs against Regis evidence semantics.
8. `sherlock-index-contracts`: validates Sherlock index records, search result pointers, and delta indexing receipts.
9. `agent-registry-identity`: validates agent manifests and policy scopes.
10. `acr-concordance-profile`: validates source assertion, crosswalk, golden projection, and proof fixtures.
11. `tritrpc-wire`: verifies deterministic request/response fixture encoding.
12. `workspace-identity-conformance`: runs the clean end-to-end lane across pinned repos.

## Required fixture families

Fixtures live under `protocol/identity-is-prime/` and should be portable across repos.

- polytope valid and invalid examples
- forbidden mixture examples
- admissible transition examples
- no-admissible-path refutations
- token non-escape valid examples
- token non-escape violation examples
- zeta audit windows
- ACR concordance and golden record proof examples
- Holmes case and contradiction examples
- Sherlock search index and query-result pointer examples

## Determinism requirements

Every conformance result must pin:

- `schema_version`
- `policy_version`
- `resolver_version`
- `template_version`, when ACR participates
- `index_version`, when Sherlock Search participates
- `case_model_version`, when Holmes participates
- `fixture_version`
- `input_hash`
- `result_hash`
- `certificate_hash`, when a proof is emitted

A repeated clean checkout with the same pins must produce equivalent results.

## Acceptance criteria

- Sociosphere can fetch the pinned repos and execute the Identity Is Prime / Regis / Holmes / Sherlock / ACR / Agent Registry conformance suite.
- Identity polytope fixtures return deterministic `VERIFIED` or `REFUTED` results.
- Token non-escape violations produce structural refutations rather than probabilistic scores.
- ACR golden record proof fixtures include shared ledger and certificate pointers.
- Holmes findings cite Regis graph, ledger, certificate, or source pointers.
- Sherlock search results cite indexed Regis/Holmes pointers and never claim canonical truth without graph/ledger backing.
- Agent manifests without required policy scopes, graph permissions, or search permissions are rejected.
- The integration remains local-first and cache-first; no central lakehouse dependency is introduced.

## Follow-on work

1. Materialize `agent-registry`, `holmes`, and `sherlock-search` in `manifest/workspace.toml` or the focused Identity Prime workspace overlay if absent.
2. Add executable validators under `tools/conformance/`.
3. Promote the fixture skeleton into schema-backed JSON validation.
4. Add TRIT RPC fixtures for `identityprime.v1`, `regis.proof.v1`, `holmes.case.v1`, `sherlock.search.v1`, and `acr.concordance.v1`.
5. Wire conformance outputs into the Sociosphere registry/evidence pattern.
