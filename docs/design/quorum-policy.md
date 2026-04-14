# Quorum and policy

## Purpose
Govern high-impact actions in a local-first multi-user fabric.

## Action classes

### Class 0 — no quorum
- read/search within ACLs
- local reindex
- local tool run without network/secrets expansion

### Class 1 — owner or project-admin approval
- add approved connector to project
- publish read-only release to allowlisted peers
- adjust project quota within cell limits

### Class 2 — quorum required
- enable WAN egress for tools
- publish discovery topics beyond allowlist
- add tool with network + secrets
- rotate dataset root keys
- destructive purge of canonical data
- promote cloud twin as authority

## Object model
- `proposal`: action, scope, threshold, expiry, nonce, requested_by
- `approval`: proposal_id, approver, signature, timestamp
- `commit`: proposal_id, threshold_met, applied_at, controller_ref, resulting policy/version refs

## Filesystem placement
- `/fabric/<cell>/.quorum/proposals/`
- `/fabric/<cell>/.quorum/approvals/`
- `/fabric/<cell>/.quorum/commits/`

## Policy bundles
Profiles should include:
- normal
- high_threat
- airgap
- connector-specific rules
- vendor egress rules
- retention classes
