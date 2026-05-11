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
4. SocioSphere materializes the proof workspace from `manifest/proof-workspace.toml`.
5. SocioSphere validates every materialized `proof-adapter.json` with strict adapter validation.
6. SocioSphere runs controller gates.
7. SocioSphere generates the claim-boundary table and claim-ledger events.
8. No claim is promoted unless a domain repo emits evidence and SocioSphere records the promotion decision with digest, boundary, and non-claims.

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

## SocioSphere validation path

The proof apparatus workflow runs on SocioSphere control-plane changes, on a daily schedule, and manually through GitHub Actions.

The workflow sequence is:

```text
validate controller metadata
-> materialize proof workspace repos
-> strict adapter validation
-> run controller gates
-> generate controller outputs
```

The CI file is `.github/workflows/proof-apparatus.yml`.

## Local command path

From the SocioSphere checkout:

```bash
python3 tools/validate_proof_apparatus.py
python3 tools/materialize_proof_workspace.py --force
python3 tools/validate_proof_apparatus.py --strict-adapters
python3 tools/run_proof_workspace_gates.py
python3 tools/generate_proof_workspace_outputs.py
```

## Current important limitation

A push to a domain proof repository does not by itself trigger SocioSphere's workflow unless an external dispatch or scheduled run occurs. SocioSphere currently covers this through:

- manual `workflow_dispatch`;
- daily scheduled validation;
- direct validation when SocioSphere control-plane files change.

The next hardening step is to add repo-dispatch or reusable workflow calls from each proof repository so domain research pushes immediately notify SocioSphere.

## Researcher rule

When in doubt, update the domain repo first and keep claims fail-closed. SocioSphere should be used to validate, route, register, and gate the work, not to inflate it.
