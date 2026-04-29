# Angel of the Lord Hardening Regime v0.1

## Purpose

The Angel of the Lord is the Sociosphere adversarial hardening regime for recurring repository, CI, release, and platform-boundary critique.

It is not a passive checklist and it is not a label for generic scanning. It is the critic workflow whose job is to inspect each implementation from a defensive standpoint and produce hard findings about weak boundaries, unsafe exposure, missing evidence, hidden trust assumptions, and unproven security claims.

## Operating thesis

Agentic development changes the economics of reconnaissance. Public code, CI metadata, dependency manifests, issue history, docs, release artifacts, and topology hints can be reviewed at machine speed. The platform therefore needs a recurring defensive reviewer that treats every repository as a possible source of sensitive implementation intelligence.

The Angel of the Lord regime turns that reviewer into a governed CI and workspace workflow.

## Core mandate

For every repository and every release path, the regime asks:

1. What sensitive implementation detail is visible here?
2. Which trust boundary is implicit, weak, undocumented, or unenforced?
3. Which CI permission, workflow, token, artifact, or log creates unnecessary leverage?
4. Which dependency, parser, endpoint, or serializer is exposed without enough evidence?
5. Which documentation or example accidentally reveals production structure?
6. Which claim lacks a test, policy, attestation, or reproducible artifact?
7. Which failure path is unaudited, silent, or non-deterministic?
8. Which security finding must block release, block publication, or remain restricted?

## Non-goals

Public Angel of the Lord outputs must not become misuse-enabling material. Public artifacts should identify classes of weakness, impacted surfaces, severity, evidence gaps, and remediation requirements without publishing sensitive operational detail.

Sensitive reproduction material, raw telemetry, incident evidence, and live topology remain restricted-security or restricted-operations material under the Source Exposure Governance Standard.

## Workflow lanes

| Lane | Purpose | First-class evidence |
|---|---|---|
| `source_exposure` | Prevent public repos and release mirrors from exposing privileged reconnaissance. | Source exposure report, blocked path/content findings, publication decision. |
| `ci_permissions` | Inspect workflow permissions, token scopes, third-party actions, logs, and deployment paths. | CI permission report, pinned action report, token-scope findings. |
| `repo_boundary` | Verify repo responsibility boundaries and prevent hidden feature work in controller repos. | Boundary report, topology report, canonical-source mapping. |
| `dependency_vulnerability` | Check dependency lag, known-risk components, SBOM/VEX posture, and release impact. | SBOM, VEX/impact report, vulnerability findings. |
| `runtime_policy` | Verify runtime enforcement expectations: identity, authorization, network policy, egress, tenant isolation. | Policy report, trust report, runtime conformance evidence. |
| `telemetry_publication` | Prevent logs, HARs, traces, and screenshots from leaking live structure. | Telemetry sanitation report, synthetic fixture declaration. |
| `release_mirror` | Gate public release mirrors and source snapshots after hardening checks pass. | Release gate report, provenance, SBOM, VEX, signed artifact refs. |
| `adversarial_review` | Produce the explicit critic narrative: what is weak, what is missing, and what must be remediated. | Critic findings, severity ledger, owner/remediation backlog. |

## Review posture

The regime is expected to be severe, explicit, and evidence-bound. It should say when an implementation is weak. It should not soften findings to avoid discomfort. Every severe claim must identify the surface, boundary, evidence, severity, and remediation.

## Severity model

| Severity | Meaning | Required action |
|---|---|---|
| `blocker` | Unsafe to merge, release, publish, or deploy. | Must remediate or explicitly quarantine/restrict. |
| `high` | Security boundary is weak or evidence is materially incomplete. | Must create tracked remediation before release. |
| `medium` | Meaningful hardening gap. | Backlog with owner and target tranche. |
| `low` | Hygiene or clarity issue. | Fix opportunistically or fold into nearby work. |
| `info` | Observation useful for posture accounting. | No immediate remediation required. |

## Required report structure

Every Angel of the Lord report should include:

- target repository, branch, commit, and workflow context;
- surfaces inspected;
- findings by severity;
- trust boundaries found and trust boundaries missing;
- evidence accepted;
- evidence missing;
- publication/deployment decision;
- remediation backlog;
- whether public disclosure is safe or restricted handling is required.

## Sociosphere implementation status

Current implemented lane:

- `source_exposure`: `standards/source-exposure/README.md`, `standards/source-exposure/policy.v0.json`, `tools/check_source_exposure.py`, `make source-exposure-check`, and CI wiring in `validate`.

Planned hardening lanes:

- `ci_permissions`: workflow permission and third-party action audit.
- `repo_boundary`: enforce controller/component boundary claims against canonical registry metadata.
- `dependency_vulnerability`: workspace-level OSV/SBOM/VEX gate.
- `release_mirror`: delayed public release mirror gate with signed artifacts.
- `adversarial_review`: structured critic report and dashboard view.

## Operating loop

1. Enumerate repositories and current materialized refs from the Sociosphere manifest and registry.
2. Run deterministic hardening lanes in CI and workspace checks.
3. Produce structured reports and a critic narrative.
4. Block unsafe publication, release, or deployment where severity requires it.
5. Register remediation work in the running backlog.
6. Re-run the regime on every pass until findings are closed or explicitly accepted with evidence.

## Boundary with implementation teams

The Angel of the Lord does not own downstream feature implementation. It owns critique, evidence requirements, hardening gates, release/publication decisions, and remediation pressure. Downstream repos own their fixes unless Sociosphere is the correct implementation home.
