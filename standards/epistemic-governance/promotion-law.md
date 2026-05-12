# Epistemic promotion, reversal, decision, and authority law

Status: draft v0.2.1  
Owner: SocioSphere  
Scope: cross-repo claim promotion, reversal, decision authorization, action authorization, authority, and appeal requirements

## 1. Promotion principle

No epistemic claim may be promoted by prose alone.

Promotion requires:

- stable claim ID;
- prior lifecycle state;
- target lifecycle state;
- claim type;
- claim boundary and non-claims;
- required gates;
- passed gate records;
- evidence IDs and artifact digests;
- policy version;
- promotion authority;
- audit record;
- replay manifest where executable evidence exists.

This mirrors SocioSphere proof-apparatus discipline for discourse, governance, policy, operational, and institutional claims.

## 2. Promotion record

A promotion record must include:

```json
{
  "promotion_id": "prom_<ULID>",
  "claim_id": "clm_<ULID>",
  "claim_type": "operational",
  "from_state": "accepted_for_context",
  "to_state": "canonized",
  "promotion_authority": "authority:<id>",
  "required_gates": ["gate:<id>"],
  "passed_gates": ["gate_result:<id>"],
  "evidence_ids": ["ev_<ULID>"],
  "claim_boundary": "bounded scope of what is promoted",
  "non_claims": ["what this promotion does not prove"],
  "policy_version": "epigov.policy.0.1",
  "ruleset_semver": "1.3.0",
  "ruleset_hash": "sha256:<hex>",
  "model_hashes": ["sha256:<hex>"],
  "audit_id": "aud_<ULID>",
  "timestamp": "2026-05-12T00:00:00Z"
}
```

## 3. Authority model

Every material operation must be governed by role and attribute policy.

Initial authority actions:

```text
create_claim
challenge_claim
run_detector
clear_detector
confirm_detector
override_detector
request_counter_test
waive_counter_test
attach_evidence
classify_evidence
promote_claim
reverse_claim
create_decision
authorize_action
execute_action
rollback_action
view_sensitive_event
export_manifest
change_policy_threshold
approve_ruleset_update
view_reasoning_calibration_projection
appeal_profile_update
```

## 4. RBAC / ABAC matrix

| Action | Minimum authority | Notes |
|---|---|---|
| `create_claim` | participant, agent, service | must preserve speaker/agent context |
| `challenge_claim` | participant, reviewer, detector, policy engine | challenge does not prove defect |
| `run_detector` | detector service, authorized reviewer | must record ruleset hash |
| `override_detector` | reviewer or governance authority | requires rationale and audit |
| `waive_counter_test` | governance authority | requires controlled exception |
| `attach_evidence` | participant, agent, retrieval service | evidence authority required |
| `classify_evidence` | evidence authority service or reviewer | must record source class |
| `promote_claim` | promotion authority | cannot be automated without policy grant |
| `reverse_claim` | reversal authority | must preserve prior state and rationale |
| `create_decision` | decision authority | must cite claims and value premises |
| `authorize_action` | action authority | must cite decision record |
| `change_policy_threshold` | policy authority quorum | requires backtest and signed update |
| `view_reasoning_calibration_projection` | profile owner or consented viewer | scope-limited |
| `export_manifest` | export authority | must apply privacy tiers and redactions |

## 5. Claim, decision, and action law

Claims do not authorize actions directly.

A valid governance sequence is:

```text
Claim(s) -> DecisionRecord -> ActionRecord
```

A decision must cite:

- claims used;
- claims rejected or unresolved;
- evidence summary;
- value premises;
- policy refs;
- decision authority;
- jurisdiction/scope;
- uncertainty;
- appeal path.

An action must cite:

- authorizing decision;
- action authority;
- execution subject;
- expected effect;
- rollback path, if applicable;
- evidence emitted after execution.

## 6. Reversal law

A canonized claim can be reversed only through a reversal record.

Reversal causes include:

```text
contradictory evidence
failed replay
invalid evidence authority
policy change
successful appeal
fraud or tampering
scope error
model/ruleset defect
```

A reversal record must include:

- reversed claim ID;
- prior state;
- new state;
- reversal cause;
- authority;
- evidence or failed gate;
- downstream affected decisions/actions;
- notification requirements;
- audit ID.

## 7. Contradiction handling

Contradictions must become ledger objects, not silent overwrites.

Outcomes:

```text
coexist_with_scope
supersede
reverse
split_claim
bounded_uncertainty
escalate_to_review
```

If two canonized claims conflict, the system must create a `contradiction.record.v1` event and prevent unreviewed promotion of dependent claims.

## 8. Appeal requirement

Promotion, reversal, detector confirmation, evidence rejection, decision authorization, action authorization, and profile projection updates must be appealable unless law or safety policy explicitly forbids it.

Appeal outcomes:

```text
upheld
partially_upheld
denied
requires_more_evidence
policy_exception_granted
detector_bug_confirmed
profile_update_reversed
claim_state_changed
decision_changed
action_reversed
```

## 9. Release gate for this standard

An implementation is not release-ready unless it can prove:

- schemas validate;
- fixtures pass;
- negative tests fail for expected reasons;
- audit replay works;
- SourceOS lane mapping exists where local-first state is used;
- AgentPlane replay bundle exists where executable detector/counter-test runs are used;
- Policy Fabric contracts validate where policy gates are enforced;
- privacy tiers are enforced;
- appeal path exists;
- migration compatibility is documented.
