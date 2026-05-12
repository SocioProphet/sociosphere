# Epistemic Governance migration and provenance ledger

Status: draft v0.2.1  
Owner: SocioSphere  
Scope: lineage from Debater 2.0 / Argument Hygiene artifacts into Epistemic Governance Standard

## Purpose

This ledger prevents artifact drift. It records how the prior Debater 2.0 design, argument-hygiene layer, Ruleset v1.3.0 material, and v0.2/v0.2.1 synthesis map into the SocioSphere estate.

The governing migration rule is:

```text
Debater 2.0 is the reference application.
Epistemic Governance is the cross-platform standard.
```

## Source artifacts

| Source | Status | Role |
|---|---|---|
| Debater 2.0 - Evidence-Grounded Debate and Argument Hygiene Specification | prior canonical artifact | reference application and first full architecture snapshot |
| Debater_2_0_Argument_Hygiene_Specification.pdf | immutable snapshot | portable review artifact |
| Ruleset v1.3.0 argument hygiene material | upgrade ledger | detector/counter-test/measurement layer |
| Epistemic Governance Standard v0.2 synthesis | scope promotion | elevates the work from Debater app to estate standard |
| Epistemic Governance Standard v0.2.1 addendum | implementation hardening | adds authority, tenancy, promotion, appeal, privacy, package, and MVS controls |

## Migration table

| Source concept | v0.2.1 destination | Status | Notes |
|---|---|---|---|
| DebaterBot critique | Reference application rationale | kept | Historical negative-control case |
| Event-driven Debater 2.0 pipeline | Protocol topic catalog + MVS reference flow | kept and generalized | No longer debate-only |
| Ingress and consent gateway | Identity/consent requirements | kept | Must support tenant and profile projection boundaries |
| Moderation and safety | Policy intervention surface | expanded | Split from epistemic detector findings |
| Argument mining | Claim lifecycle and claim event model | expanded | Adds decision/action separation |
| Discourse graph | Claim/contradiction/repair graph | expanded | Adds contradiction ledger and repair states |
| Evidence retrieval | Evidence authority policy | expanded | Adds source class, jurisdiction, freshness, quote exactness |
| Verification | Promotion gates | expanded | Verification is necessary but not sufficient for canonization |
| Counterargument generation | Reference application generation | narrowed | Generation is downstream of governance gates |
| Rationale explainer | User-visible explanation and repair path | expanded | Must avoid hidden chain-of-thought logging |
| Audit ledger | Audit append + replay manifest | kept | Requires canonical hashing/signature rules in later schema pack |
| LOGFALL detector library | Detector map | kept | Detector outputs are hypotheses, not accusations |
| COGBIAS profiler library | Reasoning Calibration Projection | renamed | Bias Passport demoted from user-facing term |
| CTEST counter-tests | Counter-test catalog | kept | Required for warn/block findings unless waived under policy |
| Bias Passport | Reasoning Calibration Projection | renamed and constrained | Self-owned, consent-scoped, low-N guarded |
| MQI | Measurement quality gate | kept | Required for metrics and profiles |
| Drift monitor | Drift and policy-freeze topic | kept | Threshold changes require signed update and backtest |
| Small-N discipline | Small-N policy | kept | N<=10 enumerates examples and forbids generalization |
| Debater UI frames | Reference app UI frames | moved | Not owned by SocioSphere implementation |
| JSON Schemas | Future schema pack | pending | To be created in next implementation turn |
| AsyncAPI/OpenAPI | Protocol and API specs | pending | Topic catalog seeded here; full specs later |
| Agent execution | AgentPlane bundle ownership | expanded | Detector/counter-test runs must be replayable bundles |
| Local-first state | SourceOS lane mapping | expanded | Discourse events map to SourceOS lanes |
| Delivery metrics | DeliveryExcellence metrics | expanded | KPIs and dashboards external to SocioSphere |

## Version policy

The migration policy is conservative:

- `v0.1` remains the reference application snapshot.
- `v0.2` defines the cross-platform standard shape.
- `v0.2.1` defines implementation-hardening requirements.
- Future `v0.3` should not remove `v0.1` lineage; it should add schema compatibility and replay guidance.

## Required future migration fields

Machine-readable migration rows should eventually include:

```yaml
source_section: string
source_version: string
source_artifact: string
destination_section: string
destination_repo: string
status: kept | renamed | expanded | superseded | moved | deleted
rationale: string
implementation_priority: P0 | P1 | P2 | P3
```

## Chain-of-custody requirements

Every future revision should preserve:

- source artifact ID or link;
- revision date;
- author or acting agent;
- section-level migration status;
- compatibility impact;
- affected repos;
- audit or PR reference.

## Immediate estate target

This ledger is registered in SocioSphere because SocioSphere owns cross-repo standards and canonical ownership maps. Downstream implementation PRs must cite this ledger when creating Policy Fabric contracts, AgentPlane bundles, SourceOS event schemas, HolographMe projection schemas, or DeliveryExcellence metrics.
