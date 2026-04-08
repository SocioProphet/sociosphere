# Local-Hybrid Full Smoke v1

## Purpose

This note documents the full seven-step smoke-path runner for the first local-hybrid slice.

It extends the earlier smoke runner by adding the last two execution steps:

- `evidence.v1.Event/Append`
- `replay.v1.Cairn/Materialize`

## What the runner now does

1. Resolve a capability binding.
2. Build a tenant dispatch payload from fixture examples.
3. Build and execute a worker request.
4. Build an evidence append request from the worker result.
5. Append the evidence via the deterministic evidence stub.
6. Build a replay/cairn materialization request from the journal offset.
7. Materialize the cairn via the deterministic replay stub.

## Default command

```bash
python3 tools/smoke/run_local_hybrid_full_smoke.py
```

## Scope limits

- still uses fixture outputs instead of a live policy engine
- still uses JSON-level example artifacts instead of packed TriTRPC vectors
- still uses deterministic stubs rather than production worker/runtime services
