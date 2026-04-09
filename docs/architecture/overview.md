# Architecture Overview

## What sociosphere is

`sociosphere` is the **workspace controller** for the SocioProphet platform. It is the single meta-repo that:

1. **Declares** every component, adapter, governance, third-party, and docs repo via `manifest/workspace.toml`.
2. **Pins** exact revisions for all remote repos in `manifest/workspace.lock.json`.
3. **Materialises** the workspace reproducibly via `tools/runner/runner.py fetch`.
4. **Verifies** integrity with `runner lock-verify` (run on every push/PR in CI).
5. **Enforces** dependency-direction rules via `tools/check_topology.py`.
6. **Hosts** shared protocol specs, fixtures, and standards (`protocol/`, `standards/`).

## Dependency graph (high level)

```
sociosphere (workspace controller)
├── components/          ← product services & CLIs (fetched from remote repos)
│   ├── prophet_cli      (SocioProphet/prophet-platform)
│   ├── agentplane       (SocioProphet/agentplane)
│   ├── new_hope         (SocioProphet/new-hope)
│   ├── slash_topics     (SocioProphet/slash-topics)
│   ├── human_digital_twin (SocioProphet/human-digital-twin)
│   ├── ontogenesis      (SocioProphet/ontogenesis)
│   ├── socioprophet_web (SocioProphet/socioprophet)
│   └── sourceos_a2a_mcp_bootstrap
├── adapters/            ← execution-primitive backends
│   ├── mcp_a2a_zero_trust (SocioProphet/mcp-a2a-zero-trust)
│   └── delivery_excellence_automation
├── governance/          ← scope, ADRs, KPIs/OKRs
│   └── delivery_excellence (SocioProphet/delivery-excellence)
├── third_party/         ← pinned external dependencies
│   ├── tritrpc          (SocioProphet/TriTRPC — pinned by submodule + lock)
│   └── gaia_world_model (SocioProphet/gaia-world-model)
├── tools/               ← workspace-level tooling
│   └── workspace_inventory
└── docs/                ← documentation sites
    └── socioprophet_docs
```

**Directionality rule:** `sociosphere → {components, adapters, third_party}` is allowed.
The reverse (`tritrpc → sociosphere`, any component importing sociosphere) is **forbidden**.
Enforced by `tools/check_topology.py`.

## Key files

| Path | Purpose |
|------|---------|
| `manifest/workspace.toml` | Canonical repo list with URLs, roles, license hints |
| `manifest/workspace.lock.json` | Pinned revisions for all remote repos |
| `tools/runner/runner.py` | Workspace CLI: list / fetch / lock-verify / lock-update / inventory / run |
| `tools/check_topology.py` | Dependency-direction enforcement |
| `governance/CANONICAL_SOURCES.yaml` | Namespace → repo ownership registry |
| `protocol/` | Shared adapter contracts and fixture specs |
| `standards/` | QES, metrics, training schemas |
| `.github/workflows/validate.yml` | CI: runner smoke test + lock-verify + standards validation |

## Execution spine (E-levels)

| Level | Status | What it covers |
|-------|--------|---------------|
| E0 | ✅ | Manifest + lock populated; `lock-verify` in CI |
| E1 | 🔶 partial | Task discovery in runner; fixtures not yet wired |
| E2 | 🔶 partial | `inventory` command exists; SBOM not yet emitted |
| E3 | ❌ todo | Adapter contract tests not yet running in CI |

See `docs/Priorities_E.md` for the full E-level definitions.

