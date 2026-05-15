# ProCybernetica Registry Mapping

Status: v0.1 registry mapping  
Upstream issue: `SocioProphet/ProCybernetica#28`  
SocioSphere issue: `SocioProphet/sociosphere#342`  
Runtime claim: none

## Purpose

This document defines how SocioSphere consumes ProCybernetica cybernetic-governance objects for workspace governance, safety-case registry, and cross-repo promotion mapping.

ProCybernetica owns the public constitutional schemas, fixtures, validators, and conformance vocabulary. SocioSphere owns workspace governance, registry behavior, and cross-repo orchestration.

## Upstream anchors

- `SocioProphet/ProCybernetica#26` — Tier 1 cybernetic-governance schemas.
- `SocioProphet/ProCybernetica#27` — defensive fixtures and validator.
- `SocioProphet/ProCybernetica#28` — integration-boundary record.

## Registry rule

SocioSphere registry entries may reference ProCybernetica safety cases, promotion decisions, evidence receipts, privacy/evidence classifications, incidents, release deltas, and authority graph snapshots.

SocioSphere-specific fields must remain adapter metadata around the referenced ProCybernetica object. They must not silently redefine the source object.

## Object mapping

| ProCybernetica object | SocioSphere consumption |
| --- | --- |
| `cybernetic_safety_case.v1.json` | Safety-case registry entry. |
| `promotion_decision.v1.json` | Cross-repo promotion, hold, or quarantine mapping. |
| `authority_graph_snapshot.v1.json` | Separation-of-powers and authority-concentration view. |
| `evidence_receipt.v1.json` | Governance-board evidence reference. |
| `privacy_evidence_classification.v1.json` | Public/private evidence boundary display. |
| `incident_record.v1.json` | Incident or control-failure triage reference. |
| `release_delta_report.v1.json` | Release or change governance view. |
| `authority_chain.v1.json` | Authority path displayed during review. |
| `agent_action_trace.v1.json` | Action trace reference for governed work. |
| `tool_permission_scope.v1.json` | Capability or permission boundary reference. |

## Public-synthetic fixture

The initial fixture is:

```text
registry/procybernetica/safety-case-registry.synthetic.json
```

It demonstrates a SocioSphere registry entry that points to ProCybernetica safety-case, promotion, evidence, privacy, incident, release-delta, and authority graph objects without importing private evidence or claiming runtime readiness.

## Non-goals

This mapping does not implement registry runtime, production promotion, policy runtime, or downstream runtime changes. It records a public registry contract and fixture surface only.
