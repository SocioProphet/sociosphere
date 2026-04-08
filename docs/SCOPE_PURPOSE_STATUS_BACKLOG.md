# Sociosphere scope, purpose, current state, and backlog

## Purpose
Sociosphere is the workspace controller repo that keeps multi-repo development reproducible. It defines the canonical workspace manifest and lock, provides a runner to fetch/build/test components, and hosts the protocol/fixtures that define adapter compatibility. The goal is deterministic orchestration of component repositories rather than feature work inside those repositories.

## Scope
### In scope
- **Workspace orchestration**: the manifest + lock format, plus tools to list/fetch/run components deterministically.
- **Execution primitives**: repeatable build/test tasks, inventory reports, and compatibility fixtures.
- **Protocol + fixtures**: shared adapter contracts and fixtures used across components.
- **Dependency pins**: submodule pins for core dependencies (for example TritRPC) and policies for updating them.

### Out of scope
- **Product features** that live inside component repos (application logic, UI, APIs).
- **Long-lived forks** of dependencies (we only pin versions and surface integration notes here).
- **CI implementations** owned by downstream repos (Sociosphere only provides the primitives and checks needed for workspace determinism).

## Current state (v0.2)
- **Manifest is fully populated**: all 20 repos (components, adapters, governance, third-party, tools, docs) are declared in `manifest/workspace.toml` with canonical GitHub URLs, `ref`, and `license_hint` fields.
- **Lock is live**: `manifest/workspace.lock.json` carries real commit SHAs for every remote-backed repo, generated 2026-04-08.
- **Runner extended to v0.2**: `tools/runner/runner.py` now implements `list`, `fetch`, `lock-verify`, `lock-update`, `inventory`, and `run`. Supports new roles (`governance`, `docs`).
- **CI enforces workspace integrity**: `.github/workflows/validate.yml` runs `runner list`, `runner lock-verify`, `runner inventory`, and `check_topology.py` on every push and PR.
- **Topology enforcement**: `tools/check_topology.py` enforces submodule-path rules, self-dependency prohibition, and third-party pinning. Runs in CI.
- **Canonical ownership expanded**: `governance/CANONICAL_SOURCES.yaml` now maps all 20 manifest entries to their GitHub repos, with roles and descriptions.
- **Architecture docs filled**: `docs/architecture/overview.md` and `docs/architecture/validation-contract.md` are no longer stubs.
- **CI runbook written**: `docs/runbooks/ci.md` covers all CI steps and how to fix common failures.
- **ADR template standardised**: `docs/governance/adr/0000-template.md` follows a complete Status / Date / Context / Decision / Consequences / Alternatives structure.
- **Makefile extended**: `make lock-verify`, `make lock-update`, `make inventory`, `make topology-check` targets added.

## Ontology integration (broader repos)
Sociosphere treats the manifest as the source of truth for repo roles and relationships. This section clarifies what is **functional today** versus what is **self-describing on paper** so the integration story stays explicit.

### Functional state (what exists today)
- **Role taxonomy is documented**: component, adapter, and third_party roles are defined in the workspace composition spec.
- **Materialization paths are specified**: components are expected under `components/`, adapters under `adapters/`, and third_party under `third_party/`.
- **Runner expectations are described**: the runner reads manifest + lock and orchestrates tasks across materialized repos.

### Self-describing state (what should be encoded in metadata)
- **Manifest fields describe intent**: `name`, `url`, `ref`/`rev`, `role`, `path`, and `license_hint` (plus `required_capabilities` for adapters) define how each repo should be interpreted.
- **Task contracts are explicit**: component repos expose build/test tasks via Makefile/justfile/Taskfile/scripts, allowing the runner to reason about execution without bespoke glue.
- **Protocol + fixtures define compatibility language**: adapter fixtures and error codes provide the vocabulary for reasoning about integration outcomes.

### Integration and reasoning model
- **Integration is role-driven**: the manifest role determines where a repo is materialized and which execution primitives apply.
- **Reasoning is deterministic**: the lock file pins exact revisions so compatibility assertions (fixtures, task contracts) are evaluated against known inputs.
- **Status is traceable**: updates to pins and integration notes are recorded in `docs/INTEGRATION_STATUS.md`.

## Backlog (rolling, v0.2)
This backlog is intentionally scoped to Sociosphere’s responsibilities. Each item should link to an issue/PR when created.

### P0 — Must-have to preserve determinism
1. ✅ **Manifest/lock fully populated**
   - All repos carry URLs and pinned revs. `lock-verify` passes cleanly.
2. ✅ **Lock verification in CI**
   - `runner lock-verify` and `check_topology.py` run on every push/PR.
3. ✅ **Version pin policy clarity**
   - `docs/NAMING_VERSIONING.md` documents bump process; `check_topology.py` enforces third-party pinning.

### P1 — Standardise execution contracts
1. **Task discovery normalization**
   - Define how `tools/runner` discovers tasks from Makefile/justfile/Taskfile/scripts.
   - Add fixture tasks under `protocol/fixtures` and wire to runner.
2. **Structured failure reporting**
   - Emit consistent error metadata from runner for downstream CI usage.
3. **Ontology enforcement**
   - Validate manifest `role` and `path` conventions during `runner fetch`.
   - Emit a structured report mapping repos to roles and capabilities.

### P2 — Supply-chain visibility
1. ✅ partial — `runner inventory` prints a text/JSON table; full SBOM not yet emitted.
2. **SBOM stub**
   - Start emitting CycloneDX JSON from `runner inventory --json`.
3. **Commit signature verification**
   - Optional; add when GPG/SSH signing is enforced org-wide.

### P3 — Adapter portability
1. **Protocol fixtures**
   - Move canonical JSON schemas + fixture vectors into `protocol/fixtures/`.
   - Wire `runner run protocol:test` against at least one adapter.
2. **Adapter contract tests**
   - Run adapter contract tests locally and in CI using the same fixtures.
3. **macOS/Linux parity**
   - Document portable adapter expectations and edge cases.

## How to keep this current
- Update the **Current state** section when a capability lands in `manifest/`, `tools/runner`, or `protocol/`.
- Add or re-prioritize backlog items as new gaps are discovered in integration work.
