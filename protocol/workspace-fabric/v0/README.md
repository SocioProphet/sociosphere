# workspace-fabric v0

Status: draft protocol surface.

This slice defines the first governed contract for local-first workspace mounts in the fabric.

## Scope

In scope for v0 includes:
- mount registration handshake
- lifecycle, reconcile, policy, quorum artifacts
- state-machine transition table
- schemas, fixtures, validation, CI

## Companion files

- ACCEPTANCE.md
- FIXTURE.md
- ADAPTERS.md
- VALIDATION.md
- STATE_MACHINE.md

## Schemas (excerpt)

- mount-registration-request.schema.json
- mount-registration-lease.schema.json
- evidence-event.schema.json
- lease-renewal-request.schema.json
- lease-revocation-request.schema.json
- authority-transition-request.schema.json
- authority-transition-decision.schema.json
- policy-decision.schema.json
- quorum-decision.schema.json
- tombstone-decision.schema.json
- reconcile-required.schema.json
- lifecycle-transition.schema.json
- state-machine.schema.json
- adapter-profile.schema.json

## Fixtures (excerpt)

- fixtures/mount-registration-request.example.json
- fixtures/mount-registration-lease.example.json
- fixtures/evidence-event.example.json
- fixtures/transition.example.json
- fixtures/state-machine.example.json

## Validation

- python3 tools/validate_workspace_fabric_fixtures.py
- .github/workflows/workspace-fabric.yml
