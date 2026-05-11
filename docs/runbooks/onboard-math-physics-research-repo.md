# Onboard a Mathematics or Physics Research Repo

This runbook makes the proof apparatus reusable for any SocioProphet mathematics, physics, mathematical-physics, proof, computational, or experimental research repository.

## Goal

A new research repo is onboarded when:

1. the repo has a `proof-adapter.json`;
2. the repo has `.github/workflows/proof-apparatus-continuous-validation.yml`;
3. SocioSphere lists the repo in `manifest/proof-workspace.toml`;
4. SocioSphere can materialize the repo;
5. strict adapter validation passes;
6. controller gates run without claim inflation.

## What belongs in the research repo

The research repo owns:

- manuscripts;
- proofs and proof drafts;
- computations and notebooks;
- fixtures and datasets;
- repo-local tests;
- claim boundaries;
- non-claim boxes;
- the repo's `proof-adapter.json`.

The research repo does not own cross-repo promotion state. SocioSphere owns that.

## What belongs in SocioSphere

SocioSphere owns:

- `manifest/proof-workspace.toml`;
- `standards/proof-apparatus/*`;
- `registry/proof-adjacency-ranking.v0.yaml`;
- materialization;
- strict adapter validation;
- controller gates;
- claim-boundary table generation;
- claim-ledger event generation.

## Repo roles

Use one of these roles in `manifest/proof-workspace.toml`:

| Role | Use |
|---|---|
| `mathematics-engine` | Pure/applied mathematics research repo |
| `physics-engine` | Physics research repo |
| `mathematical-physics-engine` | Gauge theory, QFT, geometry/physics bridge repo |
| `proof-engine` | Formal proof, proof-governance, metatheory repo |
| `research-engine` | General research repo that does not yet fit a narrower category |
| `computational-engine` | Computation-heavy research repo |
| `experimental-engine` | Empirical or simulation-heavy research repo |
| `domain-engine` | Existing domain proof repo role |
| `metatheory-engine` | Existing metatheory proof repo role |
| `finite-channel-engine` | Existing finite representation/channel proof repo role |
| `analytic-number-theory-engine` | Existing analytic-number-theory proof repo role |

## Add files to the research repo

Copy these templates from SocioSphere:

```text
templates/proof-research/proof-adapter.json
-> proof-adapter.json

templates/proof-research/proof-apparatus-continuous-validation.yml
-> .github/workflows/proof-apparatus-continuous-validation.yml
```

Then edit `proof-adapter.json`:

- replace `repo` with `SocioProphet/<repo-name>`;
- set `domain`;
- define claims only if there is a real claim to track;
- define gates for repo-local checks;
- define non-claims aggressively;
- keep initial claim state `draft` or `diagnosed` unless evidence already exists.

## Add the repo to SocioSphere

Add a block to `manifest/proof-workspace.toml`:

```toml
[[repos]]
name = "REPLACE_WITH_REPO_NAME"
role = "mathematics-engine"
domain = "replace-with-domain"
url = "https://github.com/SocioProphet/REPLACE_WITH_REPO_NAME"
ref = "main"
local_path = "proof/REPLACE_WITH_REPO_NAME"
owned_gates = [
  "claim-boundary",
  "non-claim",
  "fixture-or-proof-check"
]
primary_walls = ["certificate_wall"]
```

Select the best role and primary walls.

## Validation behavior

After onboarding, a push or PR in the research repo immediately calls:

```text
SocioProphet/sociosphere/.github/workflows/proof-apparatus.yml@main
```

The caller passes:

```text
domain_repo = github.repository
domain_ref  = github.ref_name
domain_sha  = github.sha
```

SocioSphere then:

```text
validates controller metadata
materializes the proof workspace
materializes the changed repo at the triggering SHA
strictly validates all proof adapters
runs controller gates
generates proof workspace outputs
```

## Promotion rule

No research claim is promoted by prose alone.

Promotion requires:

- a domain artifact;
- a passed gate;
- an artifact digest;
- severity movement;
- claim-boundary update;
- non-claim update if needed;
- SocioSphere controller decision.

## Minimal initial adapter policy

For a new repo, start conservative:

- use `state: draft`;
- use `severity: E7`;
- include a non-claim that blocks theorem/final-result interpretation;
- add gates as `planned` until executable evidence exists.

## First green-run checklist

- [ ] Domain repo push creates a `Proof apparatus continuous validation` run.
- [ ] The run calls SocioSphere reusable workflow.
- [ ] SocioSphere materializes the changed repo at the triggering SHA.
- [ ] Strict adapter validation passes.
- [ ] Controller gates pass.
- [ ] No claim is promoted automatically.

## Branch protection

After first green runs, require `validate-with-sociosphere` or the called SocioSphere validation job as a required check before merging claim-bearing branches.
