# Proof Research Workflow

SocioSphere is the controller. Domain proof repositories are the engines.

This runbook describes what happens when new proof research is produced in a proof repository and how SocioSphere absorbs it without silently promoting claims.

## Proof workspace roles

| Layer | Owner | Responsibility |
|---|---|---|
| Domain repo | BSD, Heller-Godel, Yang-Mills, Heller-Winters, HPHD | Research artifacts, repo-local tests, proof drafts, computations, fixtures, non-claims |
| Adapter manifest | Each domain repo | `proof-adapter.json` exposing claims, gates, non-claims, and obstruction walls |
| Controller | SocioSphere | Manifest, materialization, strict adapter validation, controller gates, claim-boundary table, ledger events |

## Normal research flow

1. Research lands in the domain repo.
2. The domain repo updates its local proof artifacts, tests, fixtures, notes, or manuscripts.
3. If the work changes claim state, gate state, claim boundary, or non-claim posture, update that repo's `proof-adapter.json` in the same PR or commit.
4. The domain repo's continuous validation workflow immediately calls SocioSphere's reusable proof-apparatus workflow.
5. SocioSphere checks out the controller workspace and materializes the proof workspace from `manifest/proof-workspace.toml`.
6. SocioSphere materializes the changed domain repo at the exact triggering repo/ref/SHA.
7. SocioSphere validates every materialized `proof-adapter.json` with strict adapter validation.
8. SocioSphere runs controller gates.
9. SocioSphere generates the claim-boundary table and claim-ledger events.
10. No claim is promoted unless a domain repo emits evidence and SocioSphere records the promotion decision with digest, boundary, and non-claims.

## What happens when new research is produced

### If the research is exploratory

Use repo-local docs or notes. Add a non-claim if the work could be misread as a theorem.

Adapter state should remain `draft`, `diagnosed`, or absent.

### If the research adds a new executable check

Add or update a gate in the domain repo's `proof-adapter.json`.

Gate status should be one of:

- `planned`
- `skip`
- `blocked`
- `fail`
- `pass`

Passing a gate is not theorem promotion by itself.

### If the research changes a claim boundary

Update the claim's `boundary` and `non_claim_refs` in `proof-adapter.json`.

SocioSphere will regenerate claim-boundary and ledger outputs after materialization.

### If the research supports promotion

Promotion requires all of the following:

- domain artifact or proof output;
- gate status update;
- artifact digest;
- severity movement;
- claim-boundary update;
- non-claim update if needed;
- SocioSphere controller decision.

Prose alone cannot promote a claim.

## Continuous validation path

Each proof repo now contains `.github/workflows/proof-apparatus-continuous-validation.yml`. On push, pull request, or manual dispatch, that workflow calls:

```text
SocioProphet/sociosphere/.github/workflows/proof-apparatus.yml@main
```

It passes:

```text
domain_repo = github.repository
domain_ref  = github.ref_name
domain_sha  = github.sha
```

SocioSphere's reusable workflow then runs:

```text
validate controller metadata
-> materialize proof workspace repos
-> materialize changed repo at triggering SHA
-> strict adapter validation
-> run controller gates
-> generate controller outputs
```

The SocioSphere controller workflow also still supports:

- manual `workflow_dispatch`;
- `repository_dispatch` event type `proof_apparatus_domain_repo_changed`;
- daily scheduled validation;
- direct validation when SocioSphere control-plane files change.

## Domain repos with immediate validation

- `SocioProphet/bsd-proof-program`
- `SocioProphet/Heller-Godel`
- `SocioProphet/yang-mills`
- `SocioProphet/Heller-Winters-Theorem`
- `SocioProphet/hphd-zeta-mirror-lattice`

## Local command path

From the SocioSphere checkout:

```bash
python3 tools/validate_proof_apparatus.py
python3 tools/materialize_proof_workspace.py --force
python3 tools/validate_proof_apparatus.py --strict-adapters
python3 tools/run_proof_workspace_gates.py
python3 tools/generate_proof_workspace_outputs.py
```

To locally simulate a changed domain repo:

```bash
PROOF_WORKSPACE_DOMAIN_REPO=SocioProphet/Heller-Godel \
PROOF_WORKSPACE_DOMAIN_REF=main \
PROOF_WORKSPACE_DOMAIN_SHA=<commit-sha> \
python3 tools/materialize_proof_workspace.py --force
```

## Remaining hardening

The immediate trigger path is present. Remaining hardening is operational:

- observe a successful workflow run from each proof repo after the first post-workflow push;
- decide whether generated controller outputs should be committed automatically, uploaded as artifacts, or only used for CI validation;
- add branch-protection requirements once the first runs are green.

## Researcher rule

When in doubt, update the domain repo first and keep claims fail-closed. SocioSphere should be used to validate, route, register, and gate the work, not to inflate it.
