# Epistemic claim lifecycle

Status: draft v0.2.1  
Owner: SocioSphere  
Scope: claim, decision, action, appeal, contradiction, repair, and profile-state lifecycle semantics

## 1. Claim lifecycle

A claim moves through explicit states:

```text
raw
→ parsed
→ classified
→ challenged
→ tested
→ grounded
→ verified
→ repaired | revised | rejected
→ accepted_for_context
→ canonized
→ deprecated | reversed
```

## 2. State definitions

| State | Meaning |
|---|---|
| `raw` | Unprocessed text, speech, artifact, code, log, or visual input. |
| `parsed` | Segmented into possible claims, warrants, evidence, and rhetorical structure. |
| `classified` | Assigned claim type, domain, language, register, speaker/agent context, and modality. |
| `challenged` | A detector, human, agent, policy, or conflicting claim raised a challenge. |
| `tested` | One or more required counter-tests executed or were explicitly waived under policy. |
| `grounded` | Candidate evidence is attached with authority and provenance metadata. |
| `verified` | Verification gates passed for the claim type and domain. |
| `repaired` | Claim was improved by clarification, steelman, evidence, narrowing, or qualification. |
| `revised` | Speaker or authorized agent materially changed the claim. |
| `rejected` | Required gates failed or policy prohibits promotion. |
| `accepted_for_context` | Locally usable under explicit scope and confidence, but not canonical truth. |
| `canonized` | Promoted into a stable institutional record under promotion law. |
| `deprecated` | No longer active, stale, superseded, or demoted by later policy/evidence. |
| `reversed` | Materially contradicted, invalidated, or successfully appealed. |

## 3. Claim types

Initial claim types:

```text
empirical
causal
probabilistic
normative
legal_policy
mathematical_formal
operational
identity
authority
preference
forecast
risk_threat
promise_commitment
interpretive
rhetorical_metaphorical
technical_engineering
```

Different claim types require different gates. A causal claim requires counterfactual or causal-structure evidence. A mathematical claim requires proof or computational gate discipline. An operational claim requires runtime, repository, replay, or run-artifact evidence. A normative claim requires value-premise extraction.

## 4. Claim, decision, and action separation

Claims, decisions, and actions are separate state machines.

```text
Claim     = what is asserted.
Decision  = what an authority chooses, based on claims plus values, policy, risk, jurisdiction, and context.
Action    = what is done in the world, repository, platform, policy, or runtime.
```

A claim can be true while a decision remains invalid, disproportionate, unauthorized, or jurisdictionally wrong. An action can be technically successful while the decision authorizing it is invalid.

## 5. Decision lifecycle

```text
proposed
→ supported
→ contested
→ reviewed
→ approved | denied | deferred
→ action_authorized | no_action
→ appealed | closed
```

A `decision.record.v1` must cite:

- decision authority;
- supporting claim IDs;
- rejected or contested claim IDs;
- value premises;
- policy refs;
- jurisdiction or scope;
- risk posture;
- appeal path;
- audit ID.

## 6. Action lifecycle

```text
proposed
→ authorized
→ scheduled
→ executed
→ verified
→ remediated | rolled_back | closed
```

An action must cite a decision record. Repository-changing, policy-changing, profile-changing, publication-changing, or world-changing actions must be replayable or explain why replay is impossible.

## 7. Contradiction lifecycle

Contradictions are not silently erased. They are governed objects.

```text
detected
→ scoped
→ reviewed
→ resolved | bounded_uncertainty | escalated
→ archived
```

A contradiction record must include:

- contradiction ID;
- claim A;
- claim B;
- scope of conflict;
- conflict type;
- current resolution status;
- synthesis attempt, if any;
- remaining uncertainty;
- review authority;
- audit ID.

## 8. Appeal lifecycle

```text
submitted
→ accepted_for_review | rejected_as_invalid
→ assigned
→ evidence_reviewed
→ decision_rendered
→ corrections_applied | no_change
→ closed
```

Appealable objects include detector findings, counter-test results, evidence authority classifications, policy interventions, generation blocks, claim rejection, claim promotion, claim reversal, reasoning-calibration profile updates, decisions, actions, and retention/redaction decisions.

## 9. Repair lifecycle

```text
suggested
→ accepted | rejected | modified
→ applied
→ retested
→ resolved | still_blocked
```

Initial repair actions:

```text
steelman_rewrite
evidence_request
term_lock
claim_split
causal_dag_request
confidence_widening
source_content_separation
burden_reassignment
baseline_request
counterexample_request
scope_narrowing
value_premise_extraction
citation_replacement
temporal_qualification
```

## 10. Detector finding lifecycle

Detector findings are hypotheses, not verdicts.

```text
raised
→ counter_test_pending
→ confirmed | cleared
→ appealed
→ upheld | reversed
→ archived
```

Required display posture:

```text
Possible reasoning defect detected.
Confidence: <score>
Span/artifact region: <location>
Counter-test: <test id>
Repair path: <repair id or recommendation>
Appeal path: <appeal case link>
```

## 11. Privacy and storage tier

Every lifecycle event must declare a privacy/storage tier:

```text
public
internal
sensitive
local_only
hash_commitment_only
redacted
sealed
```

Raw text should not be retained when a derived claim object, redacted span, and hash commitment are sufficient.
