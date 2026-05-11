# Proof Apparatus First-Green Verification

This runbook defines the evidence required before declaring the proof-apparatus continuous-validation path operationally green.

A green checkmark is not enough. The first green run must show that the controller validated the intended domain repo/ref/SHA, strict adapter validation actually ran, controller gates ran, and generated outputs were preserved as artifacts.

## Scope

Verify first green runs for:

- `SocioProphet/bsd-proof-program`
- `SocioProphet/Heller-Godel`
- `SocioProphet/yang-mills`
- `SocioProphet/Heller-Winters-Theorem`
- `SocioProphet/hphd-zeta-mirror-lattice`
- `SocioProphet/sociosphere`

## Required evidence from a valid green run

For each repo, inspect the Actions run and confirm the following appeared in logs or artifacts.

### 1. Trigger context is correct

The run log must show:

```text
event=<push|pull_request|workflow_dispatch|repository_dispatch|schedule>
caller_repo=<triggering repo>
domain_repo=<triggering repo>
domain_ref=<triggering ref>
domain_sha=<triggering SHA>
```

For pull requests, `domain_ref` must be `refs/pull/<number>/head` and `domain_sha` must equal the PR head commit SHA, not the base branch and not an unrelated merge/default ref.

### 2. SocioSphere controller checkout is correct

If the caller is not `SocioProphet/sociosphere`, the run must checkout:

```text
repository: SocioProphet/sociosphere
ref: main
```

This proves the domain repo is calling the controller rather than copying controller logic locally.

### 3. Changed-domain materialization is exact

The materializer log must show:

```text
using changed domain repo override for <repo>: ref=<domain_ref> sha=<domain_sha>
```

It must then fetch the triggering ref and checkout the exact SHA.

### 4. Strict adapter validation ran

The run must execute:

```text
python3 tools/validate_proof_apparatus.py --strict-adapters
```

The output must show all manifest repos were checked and no materialized adapter was missing.

### 5. Negative adapter tests ran

The run must execute:

```text
python3 tools/test_proof_adapter_negative_cases.py
```

Expected output includes passing expected-failure cases for:

- missing claims block;
- undeclared gate reference;
- undeclared non-claim reference;
- missing non-claim coverage;
- invalid obstruction wall;
- repo-local self-promotion;
- checked claim without passed gates;
- passed gate missing digests;
- invalid manifest role.

### 6. Controller gates ran

The run must execute:

```text
python3 tools/run_proof_workspace_gates.py
```

The output must report all controller metadata gates passing. Passing the controller gates does not promote theorem status.

### 7. Generated outputs were preserved

The run must execute:

```text
python3 tools/generate_proof_workspace_outputs.py
```

The run must upload the artifact:

```text
proof-apparatus-controller-outputs
```

The artifact must include:

- `status/proof-apparatus/claim-boundary-table.md`
- `status/proof-apparatus/claim-ledger-events.jsonl`
- `status/proof-apparatus/gate-report.json`
- `status/proof-apparatus/gate-report.md`

## First-green acceptance checklist

For each repo:

- [ ] Run triggered on push, pull request, or manual dispatch.
- [ ] Run called SocioSphere reusable workflow.
- [ ] Trigger context names correct domain repo/ref/SHA.
- [ ] Changed-domain repo was materialized at exact SHA.
- [ ] Strict adapter validation ran.
- [ ] Negative adapter tests ran.
- [ ] Controller gates ran.
- [ ] Controller outputs were uploaded as artifacts.
- [ ] No claim was automatically promoted.

## Failure triage

If first-green fails, classify the failure before patching:

| Failure class | Meaning | Response |
|---|---|---|
| `workflow_call_failure` | Domain repo cannot call SocioSphere reusable workflow. | Check repo visibility, Actions settings, and reusable workflow syntax. |
| `checkout_failure` | SocioSphere controller checkout failed. | Check repository/ref permissions. |
| `materialization_failure` | Domain repo/ref/SHA cannot be materialized. | Check ref/SHA fetch behavior and PR-head resolution. |
| `adapter_shape_failure` | `proof-adapter.json` violates schema/validator. | Fix adapter, not controller. |
| `negative_test_failure` | Bad adapter case passed unexpectedly or valid adapter failed. | Fix validator or negative-test fixture. |
| `controller_gate_failure` | SocioSphere gate found metadata contradiction. | Fix domain adapter or controller doctrine. |
| `artifact_failure` | Outputs generated but not uploaded. | Fix workflow artifact path or generator. |

## Branch protection after first green

After all current proof repos have at least one observed green run, add branch protection requiring the proof-apparatus continuous-validation check on claim-bearing branches.

Do not require branch protection before first green runs, or the repos may be locked behind a workflow bug.
