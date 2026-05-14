# Identity Prime ER+ Conformance Lane

Status: v0.1 workspace conformance registration.

This lane binds the merged ER+ reference implementation in `identity-is-prime-reference` to the merged ER+ graph evidence contract in `regis-entity-graph`.

## Purpose

The ER+ conformance lane checks that the estate now has a complete, portable path from executable reference semantics to graph-stored evidence:

1. Identity Is Prime defines and tests intrinsic record path costs.
2. Identity Is Prime defines and tests intrinsic entity move path costs.
3. Identity Is Prime defines and tests behavioral delay-coordinate features.
4. Identity Is Prime defines and tests finite-graph expansion diagnostics.
5. Identity Is Prime defines and tests neutrality replay certificates.
6. Regis stores those outputs as proof-carrying graph evidence.
7. Regis validates ER+ evidence bundles and decision-ledger references.

## Upstream merged anchors

- `SocioProphet/identity-is-prime-reference` PR #4: ER+ intrinsic geometry reference implementation.
- `SocioProphet/regis-entity-graph` PR #15: ER+ graph evidence contracts.

## Workspace inputs

The focused workspace overlay is `manifest/identity-prime-workspace.toml`.

Required Identity Is Prime artifacts under `components/identity_is_prime_reference`:

- `docs/70_ER_PLUS_INTRINSIC_GEOMETRY.md`
- `schemas/er_plus/ERPlusConfig.v0.1.json`
- `src/prime_er/edit_geometry.py`
- `src/prime_er/entity_geometry.py`
- `src/prime_er/behavior.py`
- `src/prime_er/neutrality.py`
- `tests/test_er_plus_geometry.py`

Required Regis artifacts under `components/regis_entity_graph`:

- `docs/architecture/er-plus-regis-graph-contract.md`
- `schemas/er_plus/ERPlusEvidenceBundle.v0.1.json`
- `fixtures/er_plus/er_plus_evidence_bundle.valid.json`
- `tools/validate_er_plus_evidence_bundle.py`

## Conformance command

From the Sociosphere workspace root after materializing the overlay:

```bash
python tools/conformance/validate_er_plus_workspace.py
```

The validator is intentionally dependency-free. It checks file presence and parses the ER+ JSON schema/fixture surfaces. It does not execute the full upstream ER+ algorithm. That remains owned by the reference repo tests.

## Acceptance criteria

- The workspace overlay declares ER+ capabilities for Identity Is Prime and Regis.
- The materialized Identity Is Prime component exposes ER+ docs, schema, modules, and tests.
- The materialized Regis component exposes ER+ graph contract docs, schema, fixture, and validator.
- Regis ER+ evidence bundle fixture parses as JSON.
- Regis evidence bundle declares `schema_version = regis.er_plus.evidence_bundle.v0.1`.
- Identity ER+ config declares `schema_version = er_plus.config.v0.1`.

## Non-goals

This lane does not deploy runtime behavior into `prophet-platform/apps/identity-prime`.

This lane does not allow search, Holmes, Sherlock, or agents to write canonical human identity truth directly. They remain evidence, finding, retrieval, or proposal surfaces unless a governed Regis reducer emits a decision-ledger entry.
