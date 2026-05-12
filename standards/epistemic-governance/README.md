# Epistemic Governance Standard

Status: draft v0.2.1 anchor  
Owner: SocioSphere  
Scope: cross-repo reasoning, claim, evidence, critique, repair, promotion, replay, and governance contracts  
Non-scope: downstream product implementation, model-specific detector internals, private tenant data, hidden model reasoning traces

## Purpose

Epistemic Governance is the SocioSphere standard for turning claims, evidence, critiques, decisions, actions, and repairs into governed, replayable, auditable objects.

The first reference application is Debater 2.0, but the standard is broader than debate. It applies to GitHub review, governance boards, agent planning, policy review, proof-program critique, SourceOS incident narratives, DeliveryExcellence retrospectives, HolographMe interviews, and institutional decision systems.

The operating doctrine is:

```text
Claims are state.
Reasoning is telemetry.
Critique is a control loop.
Evidence is the promotion substrate.
Repair is the product.
```

## Why SocioSphere owns the standard

SocioSphere is the workspace controller and standards surface for the estate. It owns workspace manifests, lock discipline, topology rules, registry metadata, shared protocol fixtures, standards validation, and cross-repo orchestration. Epistemic Governance is therefore registered here as a standard and protocol surface.

Downstream repositories remain responsible for implementation:

- ProCybernetica owns doctrine and cybernetic control law.
- Policy Fabric owns intervention, profile-projection, retention, drift, and promotion policy as code.
- AgentPlane owns executable detector, counter-test, replay, and backtest bundles.
- SourceOS owns local-first discourse event integrity, privacy lanes, repair/tombstone behavior, and replayable state.
- HolographMe / Human Digital Twin owns consent-scoped reasoning-calibration projections.
- DeliveryExcellence owns metrics, dashboards, and release-readiness signals.
- Ontogenesis owns semantic ontology, claim types, reasoning-defect vocabulary, and counter-test bindings.

## Relationship to existing SocioSphere standards

Epistemic Governance composes existing standards rather than replacing them.

- The Proof Apparatus standard supplies claim, gate, evidence, obstruction, promotion, and non-claim discipline.
- QES supplies event, topic, run, evidence, deterministic replay, and compatibility discipline.
- Source Exposure Governance supplies publication-safety and disclosure discipline.
- Angel of the Lord supplies adversarial critique posture.
- Workspace manifest and topology checks supply cross-repo determinism.

## Core objects

```text
Claim
Evidence
Warrant
Backing
Rebuttal
Qualifier
Counterexample
DetectorFinding
CounterTestResult
RepairAction
DecisionRecord
ActionRecord
AppealCase
ContradictionRecord
PromotionRecord
ReversalRecord
AuditRecord
ReplayManifest
ReasoningCalibrationProjection
```

## Claim, decision, and action separation

This standard distinguishes epistemic claims from governance decisions and operational actions.

```text
Claim: a statement that can be parsed, tested, grounded, accepted, canonized, deprecated, or reversed.
Decision: an authority-scoped governance choice made using one or more claims plus values, policy, risk, jurisdiction, and mission context.
Action: a world-changing or repository-changing operation taken after a decision.
```

A true claim does not automatically authorize an action. A valid action must cite the decision record that authorized it, and the decision must cite its supporting claims and policies.

## Detector fallibility rule

LOGFALL, COGBIAS, TECHCLAIM, and related detector outputs are hypotheses, not final accusations.

Required framing:

```text
possible reasoning defect
confidence score
span or artifact region
signal stack
required counter-test
status: raised | counter_test_pending | confirmed | cleared | appealed | reversed | archived
```

User-facing surfaces must not label people as biased or defective. They must show the finding, uncertainty, repair path, and appeal path.

## Human dignity rule

The user-facing profile artifact is named Reasoning Calibration Projection, not Bias Passport.

The system must not create public bias leaderboards, use calibration scores as sole employment criteria, expose low-N scores outside self-private diagnostic mode, compare people across domains without MQI, mutate human profiles without audit, or treat contextual calibration telemetry as permanent identity.

## Conformance surface

A conforming implementation must support:

1. typed discourse ingress;
2. claim lifecycle records;
3. detector findings as hypotheses;
4. paired counter-tests for warn/block findings;
5. claim repair events;
6. evidence authority metadata;
7. claim / decision / action separation;
8. promotion and reversal law;
9. appeal and dispute records;
10. privacy tiers and tombstones;
11. replay manifests;
12. deterministic validation of schemas and examples;
13. SourceOS lane mapping where local-first state applies;
14. AgentPlane replay where executable detector/counter-test runs apply;
15. DeliveryExcellence metrics for drift, appeal, repair, evidence, and review load.

## Minimal viable slice

MVS-1 is intentionally small:

```text
claim ingress
claim parser
LOGFALL.STRAWMAN.V2 deterministic detector
CTEST.STEELMAN.CONFIRM.V2 stub
repair suggestion
audit append
JSON Schema validation
one AgentPlane replay bundle
one SourceOS event-store write
```

MVS-1 proves that the standard is executable without requiring the full Debater 2.0 application.

## Files in this standard

| File | Purpose |
|---|---|
| `README.md` | Standard anchor and estate placement |
| `claim-lifecycle.md` | Claim, decision, action, contradiction, appeal, and repair lifecycle model |
| `promotion-law.md` | Promotion, canonization, reversal, decision, action, and authority rules |
| `detector-countertest-map.yaml` | Initial detector/counter-test/severity/repair bindings |
| `migration-ledger.md` | v0.1 Debater → v0.2/v0.2.1 migration map |

Protocol files live under `protocol/epistemic-governance/v1/`.

Registry and estate ownership live under `registry/epistemic-governance.yaml`.
