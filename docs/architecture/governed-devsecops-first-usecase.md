# Governed DevSecOps as the first hypergraph use case

Status: proposed canonical use case 001  
Owner: SocioSphere  
Scope: workspace governance, CI/security evidence, release/publication gates, cross-repo orchestration  
Non-scope: downstream product feature implementation

## Decision

SocioSphere will treat **governed DevSecOps** as the first concrete use case for the governed hypergraph substrate.

This establishes a practical bridge between the current SocioSphere execution spine and the proposed Fog / governed hypergraph IR:

- repositories, manifests, locks, CI workflows, tools, policies, findings, attestations, and release gates become typed objects;
- build, test, scan, verify, attest, publish, deploy, and critique operations become typed boxes;
- shared evidence objects such as SBOMs, VEX records, source-exposure reports, policy decisions, provenance anchors, and audit traces become dots or hyperedges;
- valid DevSecOps execution is composition subject to schema, policy, identity, capability, source-exposure, topology, and evidence gates.

The first use case is not a generic security checklist. It is a governed composition model for software delivery.

## Why SocioSphere owns this

SocioSphere is already the workspace controller for the SocioProphet estate. It owns the manifest, lock, runner semantics, topology checks, shared standards, protocol fixtures, governance metadata, source-exposure checks, and adversarial hardening regime. That makes it the correct place to define the first governed DevSecOps composition model.

Downstream repositories remain responsible for their own product implementation. SocioSphere owns the cross-repo admissibility rules, validation contracts, evidence requirements, and release/publication gates.

## Current substrate already present

This use case starts from capabilities already present in SocioSphere:

- deterministic workspace manifest and lock;
- `tools/runner/runner.py` workspace execution primitives;
- topology and dependency-direction validation;
- standards validation;
- source-exposure governance;
- Angel of the Lord adversarial hardening lanes;
- registry metadata for canonical repositories, dependencies, and DevOps automation;
- execution spine E0-E3.

The use case turns those capabilities into the first typed governed hypergraph composition.

## Use case statement

When a change is proposed anywhere in the SocioProphet workspace, SocioSphere should be able to construct a governed DevSecOps graph that answers:

1. Which repositories, components, policies, and release surfaces are affected?
2. Which build, test, security, source-exposure, topology, and evidence checks must run?
3. Which typed evidence objects were produced?
4. Which gates passed, failed, warned, or require human escalation?
5. Which claims are now admissible: buildable, testable, publishable, releasable, deployable?
6. Which findings block merge, publication, release, or deployment?
7. Which downstream owners receive remediation work?

The output is not merely CI pass/fail. The output is an audit-ready DevSecOps admissibility decision.

## Hypergraph mapping

### Objects

Typed objects include:

- `Repository`
- `WorkspaceManifest`
- `WorkspaceLock`
- `CommitRef`
- `PullRequest`
- `WorkflowRun`
- `BuildArtifact`
- `TestResult`
- `SourceExposureReport`
- `SBOM`
- `VEXDecision`
- `PolicyDecision`
- `TopologyReport`
- `CapabilityScope`
- `EvidenceReceipt`
- `ProvenanceAnchor`
- `ReleaseCandidate`
- `DeploymentCandidate`
- `AdmissibilityDecision`
- `RemediationIssue`

### Boxes

Typed boxes include:

- `lock_verify`
- `topology_check`
- `source_exposure_check`
- `validate_standards`
- `runner_inventory`
- `task_discovery`
- `build`
- `test`
- `security_scan`
- `sbom_emit`
- `vex_emit`
- `attest`
- `angel_review`
- `policy_evaluate`
- `publication_gate`
- `release_gate`
- `deployment_gate`
- `remediation_route`

### Dots / hyperedges

Shared governed resources include:

- canonical repo identity;
- pinned revision;
- dependency edge;
- affected surface;
- evidence receipt;
- policy guard;
- source-exposure finding;
- vulnerability finding;
- artifact provenance;
- release decision;
- remediation owner.

These are not ordinary pipeline edges. They are shared typed governance objects that many checks may read, produce, constrain, or merge.

## First executable flow

The minimum first flow is:

```text
PullRequest
  -> affected_repo_resolution
  -> lock_verify
  -> topology_check
  -> validate_standards
  -> source_exposure_check
  -> runner_inventory
  -> policy_evaluate
  -> admissibility_decision
  -> remediation_route
```

The first evidence set is:

```text
WorkspaceLock
TopologyReport
StandardsValidationReport
SourceExposureReport
InventoryReport
PolicyDecision
AdmissibilityDecision
RemediationIssue[]
```

This is enough to prove the model because it uses existing SocioSphere lanes while exposing the missing governed-IR layer.

## Gate model

A governed DevSecOps composition can produce one of five decisions:

| Decision | Meaning |
|---|---|
| `admissible_to_merge` | The change has passed all required merge gates. |
| `admissible_to_publish` | Public exposure gates and evidence requirements are satisfied. |
| `admissible_to_release` | Release evidence, provenance, SBOM/VEX, and security posture are sufficient. |
| `admissible_to_deploy` | Runtime and deployment gates are satisfied. |
| `blocked_or_escalate` | At least one required gate failed or requires human governance review. |

A decision is valid only if it cites the evidence objects used to reach it.

## Basis discipline

Only basis-declared, provenance-addressable, type-stable DevSecOps objects may use classical copy/merge/delete semantics.

Allowed classical objects include:

- commit SHAs;
- lock entries;
- manifest entries;
- source-exposure findings;
- CI status records;
- SBOM component records;
- VEX decisions;
- signed attestations;
- policy decisions;
- remediation issues.

Not allowed as classical facts without promotion gates:

- heuristic model judgments;
- unverified scanner summaries;
- raw logs containing live operational structure;
- probabilistic risk estimates;
- latent embeddings;
- unaudited agent memory;
- unreviewed natural-language claims.

This prevents the system from treating uncertain or sensitive operational material as stable public governance evidence.

## First implementation tranche

### M0 — Canonical use case registration

Deliverables:

- this document;
- docs index entry;
- tracking issue for governed DevSecOps hypergraph IR v0.

Definition of done:

- SocioSphere has one canonical first use case for the governed hypergraph substrate.

### M1 — Report schema

Define a `governed_devsecops_report.v0.json` schema with:

- target repository;
- commit/ref/PR context;
- affected surfaces;
- boxes/checks executed;
- evidence objects produced;
- gates evaluated;
- findings by severity;
- admissibility decision;
- remediation routing.

### M2 — Valid and invalid fixtures

Add fixtures that prove:

- valid PR governance flow passes;
- missing source-exposure report fails;
- stale lock fails;
- topology violation fails;
- missing evidence receipt fails;
- unverified scanner summary cannot be promoted to release evidence;
- raw operational log cannot be published as public trust evidence.

### M3 — Validator

Add a stdlib-first validator:

```bash
python3 tools/validate_governed_devsecops_report.py
make governed-devsecops-validate
```

### M4 — Runner integration

Add a runner command or report mode:

```bash
python3 tools/runner/runner.py governed-devsecops-report --target <repo>
```

The initial implementation may compose existing outputs rather than reimplementing every check.

### M5 — CI gate

Wire validation into workspace CI after fixtures stabilize.

## Acceptance criteria

This use case is credible when SocioSphere can produce a machine-readable report that says:

- what changed;
- what was affected;
- what checks were required;
- what checks ran;
- what evidence was produced;
- what was blocked;
- what is admissible;
- what needs remediation;
- which decision is safe to expose publicly and which evidence must remain restricted.

## Relationship to existing standards

This use case composes the existing standards rather than replacing them.

- Angel of the Lord supplies adversarial critique posture and lanes.
- Source Exposure Governance supplies publication safety rules.
- The execution spine supplies deterministic runner and CI progression.
- Registry and topology metadata supply repo identity and dependency context.
- The governed hypergraph model supplies the compositional semantics tying these into one auditable DevSecOps decision.

## Non-goals

This use case does not require full Fog Hypergraph IR implementation before it starts.

It does not move downstream product implementation into SocioSphere.

It does not publish sensitive operational details.

It does not treat scanner summaries, model outputs, embeddings, or unaudited agent claims as release evidence without promotion gates.

## Summary

Governed DevSecOps is the correct first use case because SocioSphere already owns the cross-repo execution spine and hardening regime. The governed hypergraph substrate makes that spine explicit: every change becomes a typed composition of repositories, checks, evidence, policies, gates, and admissibility decisions.

This turns CI from a pile of workflow jobs into an auditable governance graph.
