# Workspace Fabric State Machine

This file complements `state-machine.schema.json` and `fixtures/state-machine.example.json`.
It documents the canonical lifecycle states and the minimum allowed transition edges for the v0 proof slice.

## Canonical states

- `DISCOVERED`
- `PROPOSED`
- `POLICY_EVALUATING`
- `QUORUM_EVALUATING`
- `LEASE_ISSUED`
- `ACTIVE`
- `DEGRADED`
- `RECONCILE_REQUIRED`
- `REVOKED`
- `TOMBSTONED`

## Minimum required edges

- `DISCOVERED -> PROPOSED`
- `PROPOSED -> POLICY_EVALUATING`
- `LEASE_ISSUED -> ACTIVE`
- `ACTIVE -> DEGRADED`
- `ACTIVE -> RECONCILE_REQUIRED`
- `ACTIVE -> TOMBSTONED`
- `ACTIVE -> REVOKED`

## Why these edges matter

- `ACTIVE -> DEGRADED` proves the slice can represent stale or partial mirror conditions.
- `ACTIVE -> RECONCILE_REQUIRED` proves the slice can represent local/remote conflict posture.
- `ACTIVE -> TOMBSTONED` proves the slice can represent a signed destructive state change.
- `ACTIVE -> REVOKED` proves the slice can represent lease invalidation without pretending the mount is still active.

## Validation intent

The lightweight validator checks that:
- the state set matches the canonical set above
- the required edges are present in the state-machine fixture
- the live transition fixture edge is present in the state-machine table
- the reconcile fixture is supported by at least one transition into `RECONCILE_REQUIRED`
- the applied tombstone fixture is supported by a transition into `TOMBSTONED`
