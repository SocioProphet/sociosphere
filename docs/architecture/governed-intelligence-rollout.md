# Governed-intelligence reference architecture rollout

Status: draft  
Owner: Sociosphere governance layer  
Scope: cross-repo coordination for canonical governed-intelligence contract adoption.

## Canonical platform loop

`Observe -> Anchor -> Normalize -> Propose -> Explain -> Verify -> Govern -> Act -> Receipt -> Learn`

## Required slash-topic governance membranes

| Membrane | Registered owner in this rollout |
| --- | --- |
| `/architecture/governed-intelligence` | `SocioProphet/sociosphere` |
| `/sherlock/evidence-answers` | `SocioProphet/sherlock-search` |
| `/holmes/proof-claims` | `SocioProphet/holmes` |
| `/gaia/world-claims` | `SocioProphet/gaia-world-model` |
| `/agents/action-admission` | `SocioProphet/agentplane` |
| `/policy/claim-action-admission` | `SocioProphet/guardrail-fabric` |
| `/ontogenesis/schema-contracts` | `SocioProphet/ontogenesis` |

## Adoption status projection

Allowed repo adoption states: `not_started`, `schema_stubbed`, `adapter_in_progress`, `contract_tests_present`, `vertical_slice_ready`.

| Repository | Child issue | Current status |
| --- | --- | --- |
| `SocioProphet/sociosphere` | parent rollout issue | `schema_stubbed` |
| `SocioProphet/ontogenesis` | [#77](https://github.com/SocioProphet/ontogenesis/issues/77) | `not_started` |
| `SocioProphet/holmes` | [#7](https://github.com/SocioProphet/holmes/issues/7) | `not_started` |
| `SocioProphet/sherlock-search` | [#51](https://github.com/SocioProphet/sherlock-search/issues/51) | `not_started` |
| `SocioProphet/gaia-world-model` | [#25](https://github.com/SocioProphet/gaia-world-model/issues/25) | `not_started` |
| `SocioProphet/guardrail-fabric` | [#23](https://github.com/SocioProphet/guardrail-fabric/issues/23) | `not_started` |
| `SocioProphet/agentplane` | [#152](https://github.com/SocioProphet/agentplane/issues/152) | `not_started` |
| `SocioProphet/model-governance-ledger` | [#16](https://github.com/SocioProphet/model-governance-ledger/issues/16) | `not_started` |

## Canonical object governance matrix

| Check | Canonical object | Source-of-truth repo | Consuming repos |
| --- | --- | --- | --- |
| - [ ] | `Entity` | `SocioProphet/ontogenesis` | `holmes`, `sherlock-search`, `gaia-world-model`, `agentplane`, `sociosphere` |
| - [ ] | `Anchor` | `SocioProphet/ontogenesis` | `sherlock-search`, `holmes`, `gaia-world-model`, `sociosphere` |
| - [ ] | `Evidence` | `SocioProphet/sherlock-search` | `holmes`, `gaia-world-model`, `guardrail-fabric`, `sociosphere` |
| - [ ] | `Claim` | `SocioProphet/holmes` | `gaia-world-model`, `guardrail-fabric`, `agentplane`, `sociosphere` |
| - [ ] | `ProofCertificate` | `SocioProphet/holmes` | `guardrail-fabric`, `agentplane`, `sociosphere` |
| - [ ] | `ExplanationTrace` | `SocioProphet/holmes` | `guardrail-fabric`, `agentplane`, `model-governance-ledger`, `sociosphere` |
| - [ ] | `VectorCandidate` | `SocioProphet/sherlock-search` | `holmes`, `gaia-world-model`, `sociosphere` |
| - [ ] | `PolicyDecision` | `SocioProphet/guardrail-fabric` | `agentplane`, `sociosphere`, `model-governance-ledger` |
| - [ ] | `ActionProposal` | `SocioProphet/agentplane` | `guardrail-fabric`, `sociosphere` |
| - [ ] | `ActionAdmission` | `SocioProphet/guardrail-fabric` | `agentplane`, `sociosphere` |
| - [ ] | `RuntimeReceipt` | `SocioProphet/agentplane` | `model-governance-ledger`, `sociosphere` |
| - [ ] | `LearningEvent` | `SocioProphet/model-governance-ledger` | `ontogenesis`, `holmes`, `guardrail-fabric`, `sociosphere` |
| - [ ] | `Revocation` | `SocioProphet/guardrail-fabric` | `agentplane`, `holmes`, `sociosphere` |
| - [ ] | `SlashTopicProfile` | `SocioProphet/slash-topics` | `sherlock-search`, `gaia-world-model`, `sociosphere` |

## Child rollout issues

- `SocioProphet/ontogenesis#77` — canonical schemas and vector encoding manifests
- `SocioProphet/holmes#7` — proof-claim and neuro-symbolic reasoning contracts
- `SocioProphet/sherlock-search#51` — evidence-answer contract
- `SocioProphet/gaia-world-model#25` — governed world-claim contract
- `SocioProphet/guardrail-fabric#23` — claim/action admission policy contract
- `SocioProphet/agentplane#152` — action proposal, admission, runtime receipt contract
- `SocioProphet/model-governance-ledger#16` — model lineage, inference trace, learning-event contract

## Workspace / mesh rollup

| Rollup surface | Covered repos | Operational projection |
| --- | --- | --- |
| `/architecture/governed-intelligence` | sociosphere, ontogenesis, holmes, sherlock-search, gaia-world-model, guardrail-fabric, agentplane, model-governance-ledger | `schema_stubbed` (tracked in Sociosphere registry) |
| Evidence and claim mesh | sherlock-search, holmes, gaia-world-model, guardrail-fabric | `not_started` |
| Action admission mesh | guardrail-fabric, agentplane | `not_started` |

## Non-goals

- Sociosphere coordinates rollout and projects operating state; it does not own all canonical schemas.
- Ontogenesis-generated contracts are not bypassed.
- `VectorCandidate` remains `candidate_only` until evidence/proof/policy gates admit downstream actions.

## Validation

- `python3 tools/validate_governed_intelligence_rollout.py`
