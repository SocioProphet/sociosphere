# Identity Is Prime protocol fixtures

These fixtures anchor the Sociosphere conformance lane for Identity Is Prime, Regis Entity Graph, Authority Concordance Rex (ACR), and Agent Registry integration.

The fixture set is intentionally small in this first pass. It establishes deterministic semantics for:

- policy polytope membership
- forbidden identity mixtures
- token congruence and non-escape violations
- ACR golden-record proof shape

Each fixture should eventually be backed by executable validators under `tools/conformance/` and by TRIT RPC request/response fixtures for the relevant service surfaces.

## Required result vocabulary

- `VERIFIED`: the claim or state satisfies the pinned policy and schema versions.
- `REFUTED`: the claim or state structurally violates policy, admissibility, or non-escape rules.
- `UNDECIDABLE`: the current abstraction lacks enough evidence to prove or refute.
- `STALE`: the fixture or certificate pins outdated schema, policy, resolver, or template versions.
- `REQUIRES_REVIEW`: the fixture requires steward review before graph mutation or publication.

## Determinism fields

Conformance outputs should pin the following where available:

- `schema_version`
- `policy_version`
- `resolver_version`
- `template_version`
- `fixture_version`
- `input_hash`
- `result_hash`
- `certificate_hash`
- `ledger_pointer`

## First fixture families

- `fixtures/polytope.valid.json`
- `fixtures/polytope.invalid.json`
- `fixtures/token.non_escape.violation.json`
- `fixtures/acr.golden_record.proof.json`
- `expected/polytope.valid.result.json`

Follow-on fixtures should add transition graph, no-admissible-path, zeta audit, agent manifest rejection, and TRIT RPC wire examples.
