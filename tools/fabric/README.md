# Fabric implementation skeleton

This directory contains a dependency-light Python scaffold for the fabric control plane contracts introduced in PRs #82-#86.

## Scope
This is not the final runtime. It is a thin implementation bridge that:
- gives the mount registration handshake a concrete in-repo home
- persists checkpoints atomically
- emits evidence events in NDJSON form
- provides an in-memory retrieval registry surface
- keeps object shapes aligned with the draft schemas

## Files
- `types.py` — dataclasses and enums for core control objects
- `checkpoints.py` — atomic checkpoint persistence helpers
- `events.py` — NDJSON evidence event emitter
- `retrieval_registry.py` — in-memory registration surface for `IndexRef`
- `mount_agent.py` — minimal mount registration flow scaffold
- `schema_refs.py` — schema path constants and lookup helpers

## Design constraints
- standard library only
- no ambient authority
- local-first defaults
- schema-aware, but not yet full JSON Schema validation

## Expected follow-on
- real schema validation wiring
- connector executor implementations
- policy/compiler integration
- CI entrypoints and tests
