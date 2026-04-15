# sociosphere

Platform meta-workspace controller for the SocioProphet ecosystem.

Sociosphere owns the canonical workspace manifest + lock, runner semantics,
protocol fixtures, and deterministic multi-repo materialization for platform
build and validation lanes.

## Governance references

- [Repository topology and dependency rules](docs/TOPOLOGY.md) — canonical source for repo roles, directionality, and the submodule update playbook.
- [Naming and versioning policy](docs/NAMING_VERSIONING.md) — single source of truth for repo naming, SemVer discipline, and submodule pin-bump rules.

## Canonical scope

Sociosphere is responsible for:

- Declaring workspace repositories and roles in `manifest/workspace.toml`.
- Pinning exact revisions in `manifest/workspace.lock.json`.
- Materializing and validating the workspace with `tools/runner/runner.py`.
- Enforcing topology and dependency-direction policies via `tools/check_topology.py`.
- Maintaining cross-repo governance and registry metadata in `registry/` + `governance/`.

Sociosphere is **not** the place for feature implementation inside downstream
component repositories.

## Canonical entry points

- Documentation index: `docs/README.md`
- Architecture baseline: `docs/architecture/overview.md`
- Scope/current state/backlog: `docs/SCOPE_PURPOSE_STATUS_BACKLOG.md`
- Integration ledger: `docs/INTEGRATION_STATUS.md`
- Namespace ownership map: `governance/CANONICAL_SOURCES.yaml`

## Repository intelligence assets

### Registry layer

| File | Description |
|---|---|
| `registry/canonical-repos.yaml` | Canonical repo inventory and metadata |
| `registry/repository-ontology.yaml` | Semantic identity, roles, and topic bindings |
| `registry/dependency-graph.yaml` | Dependency edges and impact reasoning |
| `registry/change-propagation-rules.yaml` | Change cascade and notification rules |
| `registry/devops-automation.yaml` | CI/CD automation policies |
| `registry/deduplication-map.yaml` | Duplicate consolidation tracker |

### Engine layer

| Module | Description |
|---|---|
| `engines/ontology_engine.py` | Controlled vocabulary and topic extraction |
| `engines/propagation_engine.py` | Cascading update computation |
| `engines/devops_orchestrator.py` | Build/test/deploy orchestration |
| `engines/metrics_collector.py` | Runtime and coverage metrics |

### CLI tools

```bash
# Registry and ontology maintenance
python cli/rebuild-registry.py
python cli/analyze-ontology.py [repo-name ...]
python cli/validate-deps.py

# Success and dedup reporting
python cli/measure-success.py
python cli/dedup-report.py
```

### Webhook entrypoint

```bash
WEBHOOK_SECRET=<shared-secret> python webhooks/github_handler.py --port 8080
```

## Quickstart (workspace runner)

```bash
python3 tools/runner/runner.py list
python3 tools/runner/runner.py fetch
python3 tools/runner/runner.py lock-verify
python3 tools/runner/runner.py validate-policy
python3 tools/runner/runner.py validate-trust
python3 tools/runner/runner.py trust-report
python3 tools/runner/runner.py run test --all
```

## Local overrides

The runner supports `manifest/overrides.toml` for local development overrides.
The file is optional and should remain gitignored.

A minimal example:

```toml
[[repos]]
name = "agentplane"
local_path = "components/agentplane-local"

[[repos]]
name = "mcp-a2a-zero-trust"
local_path = "components/mcp_a2a_zero_trust_local"
```

At runtime, `runner.py` merges override repo entries by `name` on top of the canonical
workspace manifest. Source fields like `local_path`, `url`, `ref`, and `rev` may be
overridden locally without editing the committed manifest.

## Documentation de-duplication policy

To avoid conflicting documentation:

1. Keep exactly **one canonical source per active topic**.
2. Keep historical branch/PR narratives for provenance, but mark them archival.
3. If docs disagree, canonical current-state docs win over archival summaries.
