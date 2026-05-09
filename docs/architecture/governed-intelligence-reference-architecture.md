# Governed Intelligence Reference Architecture

Status: draft
Owner repo: `SocioProphet/sociosphere`
Parent issue: `SocioProphet/sociosphere#310`

## Purpose

This document defines the SocioProphet governed-intelligence reference architecture. It converts the program synthesis across typed proof systems, hyperknowledge graphs, neuro-symbolic reasoning, explainable text models, and vector-symbolic architectures into a single operational contract for the estate.

The architecture is not a model feature and not a search feature. It is the shared control loop for turning observations into governed claims and governed actions.

## Canonical loop

```text
Observe -> Anchor -> Normalize -> Propose -> Explain -> Verify -> Govern -> Act -> Receipt -> Learn
```

Every participating repo should preserve this sequence and declare which segment it owns.

| Step | Meaning | Primary owner |
| --- | --- | --- |
| Observe | Ingest raw state, text, code, map, model, event, or runtime signal. | GAIA, Sherlock, Agentplane, Model Governance Ledger |
| Anchor | Bind the observation to a source span, geometry, code range, table cell, log range, or media region. | Sherlock, GAIA, Ontogenesis |
| Normalize | Convert raw inputs into typed entities, evidence, observations, or candidate objects. | Ontogenesis, Regis, Sherlock, GAIA |
| Propose | Emit a candidate claim, action, model output, or vector candidate. | Holmes, Sherlock, GAIA, Agentplane, Model Governance Ledger |
| Explain | Attach rule traces, evidence paths, model scores, phrase evidence, graph paths, or fusion chains. | Holmes, Model Governance Ledger, GAIA, Sherlock |
| Verify | Type-check, validate, reason over contradiction, and confirm required evidence is present. | Holmes, Ontogenesis |
| Govern | Admit, deny, require review, or mark provisional. | Guardrail Fabric, Policy Fabric |
| Act | Execute only after admission when the operation is effectful. | Agentplane |
| Receipt | Emit runtime, artifact, workflow, or learning receipts. | Agentplane, Model Governance Ledger, Sociosphere |
| Learn | Register evaluation, drift, calibration, rollout, and adoption events. | Model Governance Ledger, Sociosphere |

## Architecture invariant

No model, graph, vector index, parser, agent, or runtime is authoritative by itself.

```text
Candidate + Evidence + Explanation + Verification + PolicyDecision => AdmittedClaim or AdmittedAction
```

Corollaries:

- Raw model output is a proposal, not admitted truth.
- Raw graph candidates are proposals, not admitted truth.
- Raw vector candidates remain `candidate_only`.
- Holmes verifies and explains claims but does not admit them.
- Policy/Guardrail Fabric admits, denies, requires review, or marks provisional.
- Agentplane performs effectful work only after admission and must emit receipts.

## Canonical objects

| Object | Definition | Source-of-truth responsibility | Initial consumers |
| --- | --- | --- | --- |
| `Entity` | Canonical actor, repo, concept, region, model, artifact, or domain object. | Ontogenesis / Regis | Sherlock, Holmes, GAIA, Sociosphere |
| `Anchor` | Pointer into a source artifact such as a text span, image region, geospatial selector, H3 cell, code range, log range, table cell, or media segment. | Ontogenesis | Sherlock, GAIA, Model Governance Ledger |
| `Evidence` | Source-backed support or opposition for a claim or action. | Ontogenesis | Sherlock, Holmes, Policy Fabric, GAIA |
| `Claim` | Typed assertion over a subject, predicate, object, context, evidence, uncertainty, and lifecycle state. | Ontogenesis / Holmes | Sherlock, GAIA, Sociosphere, Policy Fabric |
| `ProofCertificate` | Machine-checkable or structured reasoning artifact for a claim. | Holmes | Policy Fabric, Sociosphere |
| `ExplanationTrace` | Human/operator-readable reasoning, rule, model, graph, phrase, or fusion trace. | Holmes / Model Governance Ledger / GAIA | Sherlock, Policy Fabric, Sociosphere |
| `VectorCandidate` | Candidate retrieved through vector-symbolic or embedding-based recall. It is never authoritative. | Ontogenesis / Sherlock / Holmes | Sherlock, Holmes, GAIA, Agentplane |
| `PolicyDecision` | `allow`, `deny`, `require_review`, or `provisional` decision for a claim, action, model, artifact, or workflow. | Guardrail Fabric / Policy Fabric | Holmes, Sherlock, GAIA, Agentplane, Sociosphere |
| `ActionProposal` | Structured request to perform effectful work with intent, scope, expected effects, required capabilities, and evidence. | Agentplane | Policy Fabric, Sociosphere |
| `ActionAdmission` | Policy-bound decision to allow or deny an action proposal or require review. | Guardrail Fabric / Agentplane | Agentplane, Sociosphere |
| `RuntimeReceipt` | Execution record containing agent/runtime identity, policy reference, inputs/outputs, hashes, logs, and status. | Agentplane | Sociosphere, Model Governance Ledger |
| `LearningEvent` | Evaluation, drift, calibration, adoption, rollout, or feedback event. | Model Governance Ledger / Sociosphere | Holmes, Sherlock, Policy Fabric |
| `Revocation` | Lifecycle event that withdraws or supersedes a claim, policy decision, artifact, action, or receipt. | Policy Fabric / Sociosphere | All consumers |
| `SlashTopicProfile` | Governance membrane for allowed objects, evidence requirements, policy profile, and query/display behavior. | Sociosphere | Sherlock, Holmes, GAIA, Agentplane |

## Slash-topic membranes

The first rollout registers these membranes:

- `/architecture/governed-intelligence`
- `/sherlock/evidence-answers`
- `/holmes/proof-claims`
- `/gaia/world-claims`
- `/agents/action-admission`
- `/policy/claim-action-admission`
- `/ontogenesis/schema-contracts`
- `/models/governance-ledger`

A slash-topic is not a tag. It is a governance membrane defining allowed object types, evidence requirements, policy profile, query behavior, display behavior, and lifecycle expectations.

## Repo responsibilities

| Repo | Responsibility in this architecture | Issue |
| --- | --- | --- |
| `SocioProphet/sociosphere` | Rollout registry, slash-topic membranes, adoption status, workspace/mesh projection. | `#310` |
| `SocioProphet/ontogenesis` | Canonical schema, ontology, SHACL, JSON-LD, and vector encoding manifests. | `#77` |
| `SocioProphet/holmes` | Proof-claim, contradiction, truth-bound, explanation, and neuro-symbolic reasoning contracts. | `#7` |
| `SocioProphet/sherlock-search` | Evidence-answer contract, anchors, proposed claims, vector candidates, answer display handoff. | `#51` |
| `SocioProphet/gaia-world-model` | Governed world claims, geospatial anchors, fusion evidence, uncertainty, `/map` evidence contract. | `#25` |
| `SocioProphet/guardrail-fabric` | Claim/action admission policy, decision states, evidence sufficiency, review gates, revocation. | `#23` |
| `SocioProphet/agentplane` | Action proposals, action admission handoff, runtime boundary records, receipts. | `#152` |
| `SocioProphet/model-governance-ledger` | Model lineage, inference traces, evaluation reports, drift events, learning events. | `#16` |

## Minimum vertical slice

The first complete implementation slice is:

```text
Sherlock query -> Anchor -> Evidence -> ProposedClaim -> Holmes ExplanationTrace -> PolicyDecision -> Answer display
```

Acceptance for this slice:

1. Sherlock emits a structured answer candidate with `Anchor`, `Evidence`, and `Claim`.
2. Holmes emits an `ExplanationTrace` and, where applicable, `ProofCertificate`, `ContradictionReport`, and `TruthBounds`.
3. Guardrail/Policy Fabric emits `PolicyDecision`.
4. Sociosphere projects adoption status under `/architecture/governed-intelligence`.
5. Vector candidates, if present, remain `candidate_only`.

## GAIA vertical slice

The GAIA slice is:

```text
Bounded source evidence -> GeoAnchor -> WorldClaim -> FusionExplanation -> Uncertainty -> PolicyDecision -> /map evidence display
```

Acceptance for this slice:

1. GAIA emits geospatial anchors for source evidence.
2. GAIA emits proposed world claims with valid time and uncertainty.
3. Holmes or GAIA emits the fusion/explanation trace.
4. Policy Fabric emits admitted, denied, review, or provisional status.
5. `/map` displays source attribution, evidence chain, uncertainty, and policy status.

## Agentplane vertical slice

The Agentplane slice is:

```text
AgentIntent -> ActionProposal -> PolicyDecision/ActionAdmission -> RuntimeBoundary -> RuntimeReceipt -> Sociosphere/LearningEvent
```

Acceptance for this slice:

1. Agentplane emits `ActionProposal` before effectful runtime work.
2. Policy Fabric emits an action decision.
3. Agentplane records runtime identity, sandbox/runtime profile, input/output hashes, logs ref, policy ref, start/end time, and status.
4. Sociosphere projects the receipt into workspace/mesh status.

## Adoption states

Sociosphere tracks rollout using these states:

- `not_started`
- `schema_stubbed`
- `adapter_in_progress`
- `contract_tests_present`
- `vertical_slice_ready`

## Non-goals

- Sociosphere does not own every canonical schema.
- Vector candidates do not become truth.
- Holmes does not admit claims.
- Policy Fabric does not perform runtime work.
- Agentplane does not decide policy.
- Model outputs do not become claims without downstream evidence, explanation, validation, and policy status.

## Definition of done

This architecture is minimally real when the estate can produce one full evidence-governed answer and one action receipt:

1. A Sherlock technical question produces a typed, cited, policy-statused claim.
2. A GAIA observation produces an admitted, provisional, review-required, or denied world claim.
3. An agent action executes only after action admission and emits a runtime receipt.
4. Model outputs remain proposals with lineage, evaluation, and inference trace references.
5. Sociosphere can report adoption status across the participating repos.
