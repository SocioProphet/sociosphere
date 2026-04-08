# Local-Hybrid Smoke v0

## Purpose

This note documents the thin smoke-path runner for the first local-hybrid slice.

The runner is intentionally small. It is not a full supervisor. It is a workspace-level demonstration that the current example artifacts and tenant-side stubs can be driven in sequence from a local checkout.

## Expected workspace layout

By default the runner assumes sibling clones under a common workspace root:

- `sociosphere`
- `agentplane`
- `TriTRPC`

## What the runner does

1. Resolve a capability binding from the `agentplane` capability example.
2. Build a dispatch payload from the `TriTRPC` task and policy fixture examples.
3. Build a worker request with side effects and network egress disabled.
4. Execute the deterministic worker stub.
5. Print a combined JSON bundle containing binding, dispatch, worker request, and worker result.

## Default command

```bash
python3 tools/smoke/run_local_hybrid_smoke.py
```

## Override examples

```bash
python3 tools/smoke/run_local_hybrid_smoke.py --workspace-root ~/dev
```

```bash
python3 tools/smoke/run_local_hybrid_smoke.py --lane tenant
```

## Scope limits

- no policy engine invocation yet; it consumes fixture outputs
- no evidence append or cairn materialization yet; those remain the next executable follow-on
- no packed TriTRPC vector generation yet; it consumes JSON-level fixture files
