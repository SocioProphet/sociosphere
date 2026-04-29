# Angel of the Lord Education Epoch Adapter

Status: draft
Owner: Sociosphere
Depends on:
- `standards/angel-of-the-lord/README.md`
- SocioProphet/socioprophet-standards-knowledge: `standards/agent-education-equivalence-standard.v1.md`
- SocioProphet/socioprophet-standards-knowledge: `standards/foundational-training-cycle-standard.v1.md`
- SocioProphet/socioprophet-standards-storage: `standards/open-courseware-corpus-standard.v1.md`
- SocioProphet/socioprophet-standards-storage: `standards/evidence-bundle-standard.v1.md`

## Purpose

This adapter connects the Angel of the Lord Hardening Regime to Michael-agent education epochs and related SocioProphet learning cycles.

The Angel of the Lord remains the Sociosphere adversarial critique authority. This adapter specifies how that regime grades educational, MLOps, ontology, platform, and OS lifecycle learning epochs.

## Scope

The adapter applies to:

- Michael-agent education epochs;
- SocioProphet agent learning epochs;
- Alexandrian Academy curriculum validation epochs;
- MLOps model training, evaluation, serving, and feedback epochs;
- Prophet Platform capability-transition epochs;
- ontology update epochs;
- SourceOS/SociOS build, boot, install, rollback, and fleet lifecycle epochs;
- Atlas orchestration and bundle execution epochs.

## Epoch grading principle

An epoch is not complete merely because work was attempted. It is complete only when evidence survives adversarial critique.

The Angel grade asks the canonical Angel questions against education and learning outputs:

1. What sensitive implementation detail is visible here?
2. Which trust boundary is implicit, weak, undocumented, or unenforced?
3. Which CI permission, workflow, token, artifact, or log creates unnecessary leverage?
4. Which dependency, parser, endpoint, or serializer is exposed without enough evidence?
5. Which documentation or example accidentally reveals production structure?
6. Which claim lacks a test, policy, attestation, or reproducible artifact?
7. Which failure path is unaudited, silent, or non-deterministic?
8. Which security finding must block release, block publication, or remain restricted?

## Required object: AngelEpochGrade

```yaml
id: stable identifier
agent_id: michael_agent | socioprophet_agent | prophet_platform_agent | sourceos_agent | atlas_agent | mlops_agent | other
epoch_id: stable epoch identifier
epoch_type: education | curriculum | mlops | model_serving | ontology | platform_contract | sourceos_lifecycle | atlas_orchestration | remediation
review_regime_ref: SocioProphet/sociosphere:standards/angel-of-the-lord/README.md
target_refs: course maps, evidence bundles, repos, commits, model artifacts, ontology files, platform contracts, release sets, or curriculum modules
surfaces_reviewed: list
angel_lanes:
  - source_exposure
  - ci_permissions
  - repo_boundary
  - dependency_vulnerability
  - runtime_policy
  - telemetry_publication
  - release_mirror
  - adversarial_review
findings_by_severity:
  blocker: []
  high: []
  medium: []
  low: []
  info: []
evidence_accepted: []
evidence_missing: []
trust_boundaries_found: []
trust_boundaries_missing: []
publication_or_transition_decision: pass | pass_with_findings | remediation_required | blocked | restricted_handling
remediation_backlog: []
review_state: draft | reviewed | accepted | rejected | blocked
reviewed_at: ISO-8601 datetime
```

## Education-specific grading checks

For Michael-agent education epochs, Angel grading must inspect:

- whether the public courseware corpus is lawfully accessible and correctly sourced;
- whether the course map matches public learning objectives rather than institutional branding alone;
- whether assignments, labs, tests, and exams have attempt evidence;
- whether answer keys were used only as practice or review artifacts, not as proof of mastery;
- whether transfer tasks demonstrate actual application to SocioProphet work;
- whether degree-equivalent claims are clearly distinguished from actual enrollment, credit, or degrees;
- whether weak objectives are routed to remediation;
- whether any generated examples expose sensitive implementation details.

## MLOps-specific grading checks

For MLOps epochs, Angel grading must inspect:

- dataset lineage;
- experiment lineage;
- evaluation evidence;
- model-serving runtime classification;
- observability and feedback capture;
- rollback/retraining criteria;
- Ray Serve/KubeRay primary-default alignment where applicable;
- Clipper references marked as `legacy_reference` only.

## Platform and OS lifecycle grading checks

For platform and SourceOS/SociOS lifecycle epochs, Angel grading must inspect:

- repo boundary correctness;
- release-set or boot-release-set evidence;
- device/fleet fingerprint evidence;
- build, boot, install, rollback, and update proof;
- source-exposure risk;
- hidden trust assumptions;
- publication safety.

## Pass/fail rules

- `pass`: no unresolved blocker or material high findings.
- `pass_with_findings`: no blockers; high findings are non-material or have accepted mitigations; medium/low backlog exists.
- `remediation_required`: learning or transition cannot complete until missing evidence or material findings are fixed.
- `blocked`: unsafe to publish, transition, deploy, mark complete, or claim mastery.
- `restricted_handling`: public artifact must be reduced, sanitized, or moved to restricted handling.

## Required downstream behavior

When Angel grading returns:

```yaml
blocked:
  action: block publication, transition, deployment, or education completion
remediation_required:
  action: create remediation backlog and keep epoch incomplete
restricted_handling:
  action: sanitize public material and move sensitive details under restricted handling
pass_with_findings:
  action: allow progress only with tracked backlog
pass:
  action: allow completion or transition
```

## Registry requirement

Sociosphere should register education-epoch grading as a governance lane for Michael-agent and related agent-learning repositories. Downstream repos own their fixes; Sociosphere owns critique, evidence requirements, hardening gates, and release/publication decisions.
