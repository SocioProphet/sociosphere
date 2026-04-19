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
- evidence emission

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

See companion files:
- `ACCEPTANCE.md`
- `FIXTURE.md`
- `ADAPTERS.md`
