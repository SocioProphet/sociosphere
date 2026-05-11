# BSD Candidate 3 Negative-Test PR Specification

Purpose: prove the proof-apparatus controller rejects claim inflation in a BSD domain repo before we trust green runs on real research.

This is the Candidate 3 verification test from the first-green BSD validation plan. It deliberately creates a bad PR against `SocioProphet/bsd-proof-program` and confirms SocioSphere rejects it for the right reason.

## Why this test exists

A green replay run is not sufficient. A controller can pass because it ran correctly, or because it did not enforce the claim boundary. This negative PR proves the adapter-validator-output chain is load-bearing.

The test should fail.

If it passes, the apparatus is not safe for claim-bearing research branches.

## Current available stress surface

The BSD adapter currently declares three claim surfaces:

| Claim id | Intended state | Purpose |
|---|---|---|
| `BSD-C5-001-consistency-grid` | `diagnosed` | C5 arithmetic consistency evidence only. |
| `BSD-M6-002-four-descent-named-primes` | `draft` | M6 four-descent named-prime lane. |
| `BSD-SHA-003-tower-bounding-diagnostic` | `diagnosed` | Sha/tower-bounding diagnostic only. |

The most important non-claims are:

| Non-claim id | Blocks |
|---|---|
| `bsd.no-full-bsd-proof` | Any claim that the adapter proves BSD-I or BSD-II. |
| `bsd.no-sha-finiteness-proof` | Any Sha finiteness or BSD-II leading-term claim. |
| `bsd.no-unchecked-rank-promotion` | Rank promotion without repo-local descent and SocioSphere gate evidence. |
| `bsd.no-parity-assumption-promotion` | Algebraic-rank promotion using parity, BSD, or Sha assumptions. |
| `bsd.no-bsd-ii-leading-term-proof` | BSD-II leading-term certification. |

## Exact negative mutation

Create a PR branch in `SocioProphet/bsd-proof-program` that edits `proof-adapter.json` as follows.

### Mutation A — repo-local self-promotion

Change:

```json
"claim_id": "BSD-M6-002-four-descent-named-primes",
"state": "draft",
"severity": "E7"
```

to:

```json
"claim_id": "BSD-M6-002-four-descent-named-primes",
"state": "promoted",
"severity": "E1"
```

This should fail because repo-local adapters are forbidden to self-promote. Only SocioSphere can record promotion decisions.

Expected validator class:

```text
repo-local adapter self-promotion
```

Expected validator wording should include one of:

```text
claim BSD-M6-002-four-descent-named-primes has invalid state
```

or:

```text
claim BSD-M6-002-four-descent-named-primes cannot self-promote in repo adapter
```

### Mutation B — checked claim without passing gates

If Mutation A is too early to reach semantic validation because schema rejects `promoted`, use this second PR or second commit instead:

Change:

```json
"claim_id": "BSD-M6-002-four-descent-named-primes",
"state": "draft",
"severity": "E7"
```

to:

```json
"claim_id": "BSD-M6-002-four-descent-named-primes",
"state": "checked",
"severity": "E1"
```

Leave all owned gates as:

```json
"status": "planned"
```

This should fail because checked/cross-checked claims require all owned gates to be `pass`, and passed gates must carry input/output SHA-256 digests.

Expected validator class:

```text
checked claim without passed gates
```

Expected validator wording:

```text
checked claim BSD-M6-002-four-descent-named-primes has non-passing gates
```

### Mutation C — delete non-claim coverage

For an additional discipline test, delete `bsd.no-parity-assumption-promotion` from the claim's `non_claim_refs` and remove `BSD-M6-002-four-descent-named-primes` from that non-claim's `applies_to` list.

This should fail because a claim must be covered by explicit non-claims either through `claim.non_claim_refs` or `non_claim.applies_to`.

Expected validator class:

```text
claim lacks non-claim coverage
```

Expected validator wording:

```text
claim BSD-M6-002-four-descent-named-primes must be covered by non_claim_refs or non_claim.applies_to
```

## The exact PR title

```text
Negative test: BSD adapter must reject unsupported M6 promotion
```

## The exact PR body

```markdown
## Purpose

This is an intentional failing PR for SocioSphere proof-apparatus validation.

It verifies that the BSD adapter cannot promote `BSD-M6-002-four-descent-named-primes` without the four-descent gates passing and without SocioSphere controller promotion.

## Expected result

The `Proof apparatus continuous validation` check must fail.

Expected failure class:

- repo-local self-promotion, or
- checked claim without passed gates, or
- missing non-claim coverage.

## Success condition

This PR is successful only if it fails validation for the expected reason.

Do not merge.
```

## What to inspect in the failed run

The failed run must show:

1. `domain_repo=SocioProphet/bsd-proof-program`.
2. `domain_ref` resolves to the PR head ref.
3. `domain_sha` equals the PR head commit.
4. SocioSphere materializes the changed BSD repo at that SHA.
5. `python3 tools/validate_proof_apparatus.py --strict-adapters` fails before controller output promotion.
6. The failure message names the claim or gate problem, not a generic checkout error.

## Acceptance

This negative-test PR is accepted when it fails for the expected validator reason.

If it passes, stop the apparatus validation effort and fix the validator before running Candidate 1 or any real BSD M6 work.

## Why no dataset row is specified here

The current connector-visible BSD repo state exposes the README and adapter but not the full referenced v0.5 dataset or test files. Therefore this negative PR targets the adapter boundary directly, which is the available load-bearing surface and the most direct test of claim-inflation discipline.

When the dataset is visible in-repo, add a second negative PR that corrupts a known v0.5 row or a C5 register value. That second PR should be a gate-execution negative test. This spec is the adapter-discipline negative test.
