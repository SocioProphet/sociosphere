# Validation contract

This document defines **what is validated, where, and by whom** across the sociosphere workspace.

## Layers of validation

### 1. Workspace structural validation (`runner lock-verify`)

Runs on every push and PR via `.github/workflows/validate.yml`.

| Check | Failure condition |
|-------|-----------------|
| Every manifest repo present in lock | Repo in `workspace.toml` missing from `workspace.lock.json` |
| All remote repos pinned | Repo has a `url` but `lock.rev` is null |
| No stale lock entries | Repo in lock but not in manifest |
| No drift (materialized repos) | `git HEAD != lock.rev` for a checked-out repo |

### 2. Dependency-direction validation (`check_topology.py`)

Runs on every push and PR.

| Check | Failure condition |
|-------|-----------------|
| Submodule paths under `third_party/` | Any `.gitmodules` entry with `path` not starting with `third_party/` |
| No self-referential component | A component/adapter URL contains `sociosphere` |
| Third-party entries pinned | A `role=third_party` repo has no `rev` in the lock |

### 3. Standards validation (`make validate-standards`)

Runs on every push and PR.

| Check | What it validates |
|-------|-----------------|
| `validate_adaptation_program.py` | Adaptation program JSON references registered metric IDs |
| `validate_qes_contracts.py` | QES CloudEvents schemas and topic catalog |

### 4. UI validation (`make ui-check`)

Runs on every push and PR.

| Check | What it validates |
|-------|-----------------|
| TypeScript compile | `apps/ui-workbench` builds without type errors |
| Vue + Vite build | Production bundle compiles successfully |

## Planned future checks (E1–E3 backlog)

- **Protocol fixture tests**: run adapter contract tests against fixtures in `protocol/fixtures/` (E1).
- **Task contract compliance**: `runner fetch` validates that each component has a Makefile/justfile/Taskfile (E1).
- **SBOM generation**: emit CycloneDX JSON from `runner inventory` output (E2).
- **Adapter contract tests**: run E3 adapter portability checks in CI.

