# TriRPC v0 Conformance Standard (v0.1)

Status: **Implemented**  
Applies to: `sociosphere/tools/conformance/trirpc-v0`

## 1. Purpose

This standard defines a minimal, deterministic conformance gate for TriRPC v0 schema artifacts.

It provides:
- A **schema fingerprint** (SHA-256) computed over canonical schema files
- A **smoke check** for file presence and correct repository root resolution
- A **golden hash** file that makes schema drift explicit and reviewable

## 2. Canonical Inputs

Required schema artifacts (relative to repo root):
- `schemas/avro/trirpc/envelope.v0.avsc`
- `schemas/avro/trirpc/value.v0.avsc`
- `schemas/avro/trirpc/error.v0.avsc`
- `schemas/schemasalad/trirpc-schema-bundle.v0.yml`

## 3. Fingerprint Algorithm

- Read bytes of each canonical file in a stable order.
- Update SHA-256 hash with the file bytes in sequence.
- Output:

`TRIRPC_V0_SCHEMA_SHA256 <hex>`

Current golden fingerprint:
`c7780ffbe6f5fec1c9e5699ae974bf7a8521156512d559cb67a34f5cce447d9a`

## 4. Commands

From `sociosphere/tools/conformance/trirpc-v0`:

- Print current fingerprint:
  - `make schema-fingerprint`

- Verify fingerprint matches golden:
  - `make schema-verify`

- Smoke-check required artifacts exist:
  - `make conformance-smoke`

- Run everything required for gating:
  - `make check`

## 5. Updating the Golden Fingerprint

If and only if schema changes are intended and reviewed:

- `make schema-update-fingerprint`
- Commit the updated `TRIRPC_V0_SCHEMA_SHA256` file with the schema change.

This makes drift explicit in review.

## 6. CI / Tekton Integration Guidance

Recommended Tekton gate:
- Clone `sociosphere` repo at a specific revision (preferably commit SHA)
- Run:
  - `make check`
- Only proceed to privileged OS builds (COSA lane) if the gate passes.

## 7. Failure Modes

- Missing artifacts: `conformance-smoke` exits non-zero with list of missing paths.
- Fingerprint mismatch: `schema-verify` exits non-zero, printing expected vs actual.
- Wrong root resolution: `conformance-smoke` prints computed `ROOT` for diagnosis.

