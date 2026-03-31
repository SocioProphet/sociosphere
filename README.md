# sociosphere (v0.1)

Platform meta-workspace controller.

Sociosphere is the meta-workspace controller for the broader SocioProphet platform. It owns the canonical manifest + lock, runner semantics, protocol fixtures, and deterministic multi-repo materialization for platform build lanes.

## Topology position

- **Role:** platform workspace controller and cross-repo assembly surface.
- **Connects to:**
  - `SociOS-Linux/agentos-spine` — current Linux-side integration/workspace spine for AgentOS / SourceOS assembly
  - `SourceOS-Linux/sourceos-spec` — canonical typed contracts, JSON-LD contexts, and shared vocabulary
  - `SociOS-Linux/workstation-contracts` — workstation/CI contract and conformance lane
  - `SociOS-Linux/SourceOS` — immutable OS substrate consumed by Linux-side build and integration lanes
  - `SociOS-Linux/socios` — opt-in automation commons, never a prerequisite for SourceOS
  - `SocioProphet/socioprophet` — umbrella public surface and integration presentation
  - `SociOS-Linux/socioslinux-web` — Linux-specific public docs surface
- **Not this repo:**
  - Linux image builder
  - immutable OS substrate
  - canonical typed-contract registry
  - public site
- **Semantic direction:** this repo should eventually publish a repo-level ontology / JSON-LD descriptor that points at the shared SourceOS/SociOS vocabulary defined in `sourceos-spec`.

- Manifest: `manifest/workspace.toml`
- Lock: `manifest/workspace.lock.json`
- Runner (Python): `tools/runner/runner.py`
- Protocol + fixtures: `protocol/`

## Scope and backlog

See `docs/SCOPE_PURPOSE_STATUS_BACKLOG.md` for scope, current state, and the rolling backlog.

## Quickstart

```bash
python3 tools/runner/runner.py list
python3 tools/runner/runner.py fetch
python3 tools/runner/runner.py run build --all
python3 tools/runner/runner.py run test --all
```

## Local overrides

Create `manifest/overrides.toml` (gitignored) to point a component to a local path.
