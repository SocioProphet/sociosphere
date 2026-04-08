# Workspace Hardening Matrix

This matrix turns the workspace-controller backlog into a concrete execution spine. The goal is to make `sociosphere` materially deterministic before more UX or orchestration layers are added.

## Principles
- Manifest + lock are the canonical workspace truth.
- Runner output must be machine-readable and evidence-friendly.
- Protocol fixtures must execute in CI, not only exist in prose.
- UI/workbench may consume workspace artifacts, but must not outrank the workspace spine.

## Matrix

| ID | Capability | Current state | Gap | Primary file targets | Validation gate |
|---|---|---|---|---|---|
| P0.1 | Deterministic manifest + lock | Manifest and lock exist, but remote source data is incomplete and `fetch` only clones when `url` is present. | Canonical repos need resolved source metadata and lock verification. | `manifest/workspace.toml`, `manifest/workspace.lock.json`, `tools/runner/runner.py` | `python3 tools/runner/runner.py lock-verify` |
| P0.2 | Canonical role ontology | Spec/docs emphasize `component`, `adapter`, `third_party`; manifest currently also uses `docs`; runner role choices include `tool`. | Role enum is drifting across docs, manifest, and code. | `docs/Repo_Layout_Workspace_Composition_Spec_v0.1.md`, `docs/SCOPE_PURPOSE_STATUS_BACKLOG.md`, `manifest/workspace.toml`, `tools/runner/runner.py` | `runner list` and `lock-verify` fail on unknown roles |
| P0.3 | CI for workspace spine | Current CI validates UI and standards. | CI must validate runner + lock + protocol before UI polish. | `.github/workflows/validate.yml`, `Makefile`, `tools/runner/runner.py` | required checks: `runner list`, `runner lock-verify`, `runner protocol:test` |
| P1.1 | Structured runner artifacts | Runner prints human-readable output only. | Emit machine-readable inventory, lock, task, and protocol reports. | `tools/runner/runner.py`, `protocol/agentplane/v0/*.schema.json` | JSON artifacts emitted under `artifacts/workspace/<run-id>/` |
| P1.2 | Executable protocol fixtures | `protocol/protocol.md` is still a placeholder. | Wire concrete fixtures into `runner protocol:test`. | `protocol/protocol.md`, `protocol/fixtures/*`, `tools/runner/runner.py` | fixture run passes locally and in CI |
| P1.3 | Single dependency truth | TritRPC pinning is split across prose, submodule config, and workspace docs. | Normalize dependency truth into manifest + lock; treat prose as summary only. | `manifest/workspace.toml`, `manifest/workspace.lock.json`, `.gitmodules`, `docs/INTEGRATION_STATUS.md` | lock verification covers pinned third-party refs |
| P1.4 | UI/workbench subordination | UI has dedicated checks and a stronger preflight than the workspace spine. | UI must consume runner artifacts and remain downstream of the spine. | `.github/workflows/validate.yml`, `apps/ui-workbench/*`, `tools/ui-preflight.sh` | workspace-spine checks run before `ui-check` |

## First patch set
1. Add `lock-verify` to `tools/runner/runner.py`.
2. Add structured artifact emission for inventory and task runs.
3. Add a stub `protocol:test` command so the CI surface exists before fixture expansion.
4. Freeze the role enum and make invalid roles fail fast.
5. Promote workspace-spine validation in CI.

## Artifact kinds to standardize
- `WorkspaceInventoryArtifact`
- `LockVerificationArtifact`
- `TaskRunArtifact`
- `ProtocolCompatibilityArtifact`

## Notes
- `sociosphere` should remain the canonical workspace controller.
- `agentplane` should consume normalized deployment/evidence packets from this repo rather than re-discover workspace state itself.
