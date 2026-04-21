# workspace-fabric v0

Status: draft protocol surface.

This slice defines the first governed contract for local-first workspace mounts in the fabric.
It treats a workspace mount as a governed object rather than an untyped filesystem path.

## Scope

In scope for v0:
- mount registration handshake
- authority mode declaration
- dataset and index binding
- adapter role declaration
- policy and quorum gating
- lease issuance
- lease renewal and revocation requests
- authority-transition request and decision artifacts
- tombstone decision artifacts
- reconcile-required artifacts
- lifecycle transition artifacts
- evidence emission
- machine-readable request, lease, evidence, lifecycle, and reconcile schemas
- lightweight fixture validation

Out of scope for v0:
- full sync protocol implementation
- full UI implementation
- cryptographic signature format details beyond required fields
- billing or tenancy accounting

## Core entities

- **Cell**: namespace root
- **Workspace**: operational boundary for a user or project
- **Mount**: governed attachment to local or remote storage
- **Dataset**: logical content domain
- **Index**: authoritative or derived lookup structure
- **Adapter**: bounded integration role such as topic distribution, object snapshot, or compatibility mirror
- **Lease**: time-bounded registration authorization

## Canonical namespace

```text
/cells/<cell>/workspaces/<workspace>/mounts/<mount>/
/cells/<cell>/datasets/<dataset>/indexes/<index>/
/cells/<cell>/topics/<topic>/
/cells/<cell>/evidence/<stream>/
```

## Authority modes

- `local_first`
- `provider_first`
- `hybrid`

Default posture: `local_first`.

## Lifecycle

```text
DISCOVERED
  -> PROPOSED
  -> POLICY_EVALUATING
  -> QUORUM_EVALUATING
  -> LEASE_ISSUED
  -> ACTIVE
  -> DEGRADED
  -> RECONCILE_REQUIRED
  -> REVOKED | TOMBSTONED
```

## Required protocol rules

- unsigned tombstones are rejected
- local dirty plus remote delete forces reconcile
- stale remote mirrors under local-first degrade to metadata-only unless policy explicitly allows more
- authority transitions require quorum unless the request is a no-op
- index authority must be declared, not inferred from engine type

## Proof-slice intent

This protocol slice is the first implementation-facing target for:
- local TopoLVM-backed mounts
- Hyper-style topic replication
- S3/MinIO snapshot replicas
- rsync bootstrap/bulk sync
- Google Drive compatibility mirrors

## Companion files

Narrative and acceptance:
- `ACCEPTANCE.md`
- `FIXTURE.md`
- `ADAPTERS.md`
- `VALIDATION.md`

Machine-readable schemas:
- `mount-registration-request.schema.json`
- `mount-registration-lease.schema.json`
- `evidence-event.schema.json`
- `lease-renewal-request.schema.json`
- `lease-revocation-request.schema.json`
- `authority-transition-request.schema.json`
- `authority-transition-decision.schema.json`
- `tombstone-decision.schema.json`
- `reconcile-required.schema.json`
- `lifecycle-transition.schema.json`

Fixtures:
- `fixtures/mount-registration-request.example.json`
- `fixtures/mount-registration-lease.example.json`
- `fixtures/evidence-event.example.json`
- `fixtures/lease-renewal-request.example.json`
- `fixtures/lease-revocation-request.example.json`
- `fixtures/authority-transition-request.example.json`
- `fixtures/authority-transition-decision.example.json`
- `fixtures/tombstone-decision.example.json`
- `fixtures/reconcile-required.example.json`
- `fixtures/transition.example.json`

Validation entrypoint:
- `python3 tools/validate_workspace_fabric_fixtures.py`
