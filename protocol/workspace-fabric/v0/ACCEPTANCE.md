# Acceptance gates

A conforming v0 implementation should satisfy the following checks.

## Registration

1. A local TopoLVM-backed mount can register as `local_first`.
2. Dataset bindings are validated before activation.
3. Index bindings are validated before activation.
4. Adapter roles are validated before activation.
5. A lease is issued only after policy and quorum checks complete.

## Authority and reconcile

6. Unsigned tombstones are rejected.
7. Signed tombstones do not silently override local dirty state.
8. Local dirty plus remote delete enters `RECONCILE_REQUIRED`.
9. Stale mirrors under `local_first` degrade to metadata-only unless policy explicitly allows more.
10. Authority transitions require quorum unless the requested authority is already current.

## Adapter role safety

11. Hyper-style feeds do not become mutable workspace authority by default.
12. S3/MinIO roles default to snapshot/replica rather than mutable authority.
13. Drive defaults to compatibility mirror rather than source of truth.
14. rsync is treated as transport/bootstrap, not as an authority root.

## Evidence

15. Registration emits an evidence event.
16. Lease issuance emits an evidence event.
17. Authority transition requests emit an evidence event.
18. Tombstone decisions emit an evidence event.
19. Reconcile-required states emit an evidence event.

## Minimum worked examples

20. Local-first TopoLVM + Xapian index + Hyper topic registration.
21. Provider-first remote authority with signed tombstone application.
22. Local-first stale remote mirror with metadata-only result posture.
23. Authority transition request that fails without quorum.
24. Authority transition request that succeeds with quorum.
