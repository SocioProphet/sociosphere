# sociosphere (v0.1)

Workspace controller repo and **Phase A registry foundation** for the
SocioProphet multi-repository ecosystem.

- Manifest: `manifest/workspace.toml`
- Lock: `manifest/workspace.lock.json`
- Runner (Python): `tools/runner/runner.py`
- Protocol + fixtures: `protocol/`
- **Registry**: `registry/`
- **Engines**: `engines/`
- **CLI tools**: `cli/`

## Scope and backlog

See `docs/SCOPE_PURPOSE_STATUS_BACKLOG.md` for scope, current state, and the rolling backlog.

## Quickstart

```bash
python3 tools/runner/runner.py list
python3 tools/runner/runner.py fetch
python3 tools/runner/runner.py run build --all
python3 tools/runner/runner.py run test --all
```

## Registry Foundation (Phase A)

The `registry/` directory is the single source of truth for the 53 SocioProphet
repositories managed by this workspace.

| File | Purpose |
|---|---|
| `registry/canonical-repos.yaml` | All 53 repositories with metadata |
| `registry/repository-ontology.yaml` | Semantic role and relationship ontology |
| `registry/dependency-graph.yaml` | Directed dependency edges between repos |
| `registry/change-propagation-rules.yaml` | Rules for cascading change notifications |
| `registry/devops-automation.yaml` | Build / test / deploy pipeline definitions |
| `registry/deduplication-map.yaml` | Consolidation tracking for duplicate repos |

### Engines

Python engines in `engines/` provide programmatic access to the registry:

| Module | Purpose |
|---|---|
| `engines/ontology_engine.py` | Semantic extraction and role queries |
| `engines/propagation_engine.py` | Cascade computation and cycle detection |
| `engines/devops_orchestrator.py` | CI/CD pipeline resolution |
| `engines/metrics_collector.py` | Registry health and coverage metrics |

### CLI tools

```bash
# Rebuild and validate the full registry
python cli/rebuild-registry.py

# Analyse the repository ontology
python cli/analyze-ontology.py [--format json]

# Validate dependency graph (cycles, orphans, coverage)
python cli/validate-deps.py [--strict]

# Print health and success metrics
python cli/measure-success.py [--format json]

# Show deduplication report
python cli/dedup-report.py [--status pending|in_progress|completed|dismissed]
```

### Running the registry tests

```bash
pip install pyyaml pytest
pytest tests/ -v
```

## Local overrides

Create `manifest/overrides.toml` (gitignored) to point a component to a local path.
