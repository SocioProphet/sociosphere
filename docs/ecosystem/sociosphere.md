# Repository Analysis — SocioProphet/sociosphere

**GitHub:** https://github.com/SocioProphet/sociosphere  
**Role in ecosystem:** Workspace controller  
**Last analysed:** 2026-04-08

---

## 1. Repository Purpose & Identity

### What it does
The monorepo workspace controller. It defines a canonical manifest and lock file that pins
all other component repositories to exact revisions, and provides a Python runner to fetch,
build, and test them deterministically.

### Core responsibilities
- Maintain `manifest/workspace.toml` + `manifest/workspace.lock.json` — the single source of
  truth for repo membership, roles, and pinned revisions.
- Orchestrate tasks via `tools/runner/runner.py` (`list`, `fetch`, `run build --all`,
  `run test --all`).
- Provide `protocol/` — shared adapter contracts and fixtures that define compatibility
  language.
- Emit normalized workspace artifacts consumed by agentplane:
  `WorkspaceInventoryArtifact`, `LockVerificationArtifact`, `TaskRunArtifact`,
  `ProtocolCompatibilityArtifact`.
- Manage version pins for third-party dependencies (e.g. TriTRPC in `third_party/`).

### What systems depend on it
- **agentplane** — explicitly consumes sociosphere bundles
  (see `agentplane/docs/sociosphere-bridge.md`).
- All component repos listed in `manifest/workspace.toml` (prophet_cli,
  sourceos_a2a_mcp_bootstrap, socioprophet-web, dev-api, hdt_app, human_digital_twin,
  ontogenesis) depend on sociosphere for coordinated builds.

### What it depends on
- Python 3 (runner)
- Component repos via workspace manifest (local or remote)
- TriTRPC — pinned in `third_party/`, integration tracked in `docs/INTEGRATION_STATUS.md`

### Key files
- `README.md` — quickstart and layout overview
- `manifest/workspace.toml` — canonical workspace manifest
- `manifest/workspace.lock.json` — pinned revision lock
- `tools/runner/runner.py` — Python orchestration entry point
- `protocol/protocol.md` — adapter contract surface
- `docs/SCOPE_PURPOSE_STATUS_BACKLOG.md` — full scope, purpose, and backlog
- `docs/INTEGRATION_STATUS.md` — TriTRPC and third-party pin history
- `docs/TOPOLOGY.md` — canonical repo topology rules
- `docs/Repo_Layout_Workspace_Composition_Spec_v0.1.md` — workspace composition spec

---

## 2. Controlled Vocabulary & Ontology

### Key terms
| Term | Definition | Source |
|---|---|---|
| **Workspace manifest** | `workspace.toml` declaring all repos, their roles, and materialization paths | `manifest/workspace.toml` |
| **Workspace lock** | `workspace.lock.json` pinning exact revisions for determinism | `manifest/workspace.lock.json` |
| **Runner** | Python orchestration tool at `tools/runner/runner.py` | `README.md` |
| **Role** | Taxonomy entry for a repo: `component`, `adapter`, `third_party`, or `docs` | `manifest/workspace.toml` |
| **Required capabilities** | Adapter-level contract declarations (e.g. `container_exec`, `fs_ops`, `deps_inventory`, `policy`, `defaults`) | `manifest/workspace.toml` |
| **Protocol + fixtures** | Shared compatibility contracts in `protocol/` | `protocol/protocol.md` |
| **Materialization** | Act of fetching/placing repos at their defined local paths via the runner | `docs/Repo_Layout_Workspace_Composition_Spec_v0.1.md` |
| **Lock drift** | State where the lock file diverges from materialized state | `docs/SCOPE_PURPOSE_STATUS_BACKLOG.md` |
| **SBOM** | Software Bill of Materials; planned CycloneDX JSON output | `docs/SCOPE_PURPOSE_STATUS_BACKLOG.md` |
| **WorkspaceInventoryArtifact** | Artifact emitted by sociosphere describing repo membership | `agentplane/docs/sociosphere-bridge.md` |
| **LockVerificationArtifact** | Artifact asserting lock file is valid | `agentplane/docs/sociosphere-bridge.md` |
| **TaskRunArtifact** | Artifact recording build/test run results | `agentplane/docs/sociosphere-bridge.md` |
| **ProtocolCompatibilityArtifact** | Artifact asserting adapter protocol fixture compatibility | `agentplane/docs/sociosphere-bridge.md` |

### Domain-specific language
- Repos are **materialized** into a workspace, not cloned arbitrarily.
- Compatibility is asserted through **fixtures** (test vectors), not integration stubs.
- The runner uses **role-driven** execution: the manifest role determines which tasks apply.
- **Deterministic** reasoning: lock file pins exact revisions so all assertions evaluate
  against known inputs.

### Semantic bindings to other repos
- **→ agentplane**: sociosphere is upstream; generates bundles agentplane executes.
- **→ prophet-platform / socioprophet-web / etc.**: sociosphere orchestrates those repos as
  "components".
- **→ TriTRPC**: pins TriTRPC as a `third_party` dependency.

---

## 3. Topic Modeling

| Topic | Keywords | Weight |
|---|---|---|
| Workspace orchestration | manifest, lock, runner, fetch, build, test, determinism | dominant |
| Repo role taxonomy | component, adapter, third_party, required_capabilities, ontology | high |
| Protocol / fixtures / contracts | protocol, fixtures, adapter, compatibility | high |
| Supply-chain traceability | SBOM, CycloneDX, inventory, license_hint, revision pins | medium |
| CI / automation | lock-drift check, smoke test, structured failure reporting | medium |
| Agent execution hand-off | WorkspaceInventoryArtifact, bundle, agentplane bridge | medium |
| FIPS / security compliance | GLOSSARY-FIPS, policy defaults | low |

---

## 4. Dependency Graph

### Direct dependencies
- Python 3 runtime
- `third_party/` submodule pins (TriTRPC confirmed by `docs/INTEGRATION_STATUS.md`)
- Component repos in `manifest/workspace.toml`:
  prophet_cli (Go), sourceos_a2a_mcp_bootstrap, socioprophet-web, dev-api,
  hdt_app, human_digital_twin, ontogenesis, plus adapters `cc` and `configs`

### Dependent systems
- **agentplane** (explicitly; bridge document declares sociosphere as upstream)
- Any CI pipeline that runs `tools/runner/runner.py` workspace-wide

### Cross-repo impact when sociosphere changes
- Manifest schema change → all components must update how they declare tasks.
- Lock file change → every component is re-pinned; agentplane must re-validate bundles.
- Protocol/fixtures change → adapter contract compatibility must be re-verified across all
  adapters.

---

## 5. Change Impact Rules

| What changed | Downstream repos affected | DevOps actions | Governance gates |
|---|---|---|---|
| `manifest/workspace.toml` schema | All components | Re-run `runner list`, `runner fetch` | Manifest version bump; ADR if role taxonomy changes |
| `manifest/workspace.lock.json` update | All pinned repos + agentplane | Full `runner run build --all` + `run test --all` | Lock review; parity check with `INTEGRATION_STATUS.md` |
| `protocol/` fixtures | All adapters | Adapter contract tests | Protocol version bump; fixture regression gate |
| `tools/runner/runner.py` | All CI using runner | CI smoke test | Smoke test must pass before merge |
| `third_party/` submodule pin (e.g. TriTRPC) | Downstream integration assumptions | Rebuild dependent components | Integration note in `docs/INTEGRATION_STATUS.md` |
