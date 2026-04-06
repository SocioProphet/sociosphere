# sociosphere (v0.2)

Workspace controller repo and **Phase A registry foundation** for the
SocioProphet multi-repository ecosystem.
Workspace controller, governance gates, and **Repository Intelligence &
DevOps Orchestration System** for the SocioProphet organisation.

- Manifest: `manifest/workspace.toml`
- Lock: `manifest/workspace.lock.json`
- Runner (Python): `tools/runner/runner.py`
- Protocol + fixtures: `protocol/`
- **Registry**: `registry/`
- **Engines**: `engines/`
- **CLI tools**: `cli/`

## Repository Intelligence System

Sociosphere now continuously understands, interconnects, and automates all
53+ SocioProphet repositories.

### Registry Layer

| File | Description |
|---|---|
| `registry/canonical-repos.yaml` | Single source of truth for all repos |
| `registry/repository-ontology.yaml` | Semantic identity, vocabulary, topic models |
| `registry/dependency-graph.yaml` | Impact analysis (if A changes, what updates?) |
| `registry/change-propagation-rules.yaml` | Automation trigger rules |
| `registry/devops-automation.yaml` | Per-repo build / test / deploy rules |
| `registry/deduplication-map.yaml` | Duplicate consolidation tracker |

### Engine Layer

| Module | Description |
|---|---|
| `engines/ontology_engine.py` | Extract controlled vocabulary and topic models |
| `engines/propagation_engine.py` | Trigger cascading updates on main-branch merges |
| `engines/devops_orchestrator.py` | Execute build / test / deploy automation |
| `engines/metrics_collector.py` | Measure and report system health |

### CLI Tools

```bash
# Scan and validate the canonical registry
python cli/rebuild-registry.py

# Extract ontologies from live repository code
python cli/analyze-ontology.py [repo-name ...]

# Verify dependency graph consistency
python cli/validate-deps.py

# Print metrics dashboard to console
python cli/measure-success.py

# Show deduplication progress and blockers
python cli/dedup-report.py
```

### Webhooks

Deploy `webhooks/github_handler.py` to receive GitHub push events and
automatically trigger the propagation engine:

```bash
WEBHOOK_SECRET=<shared-secret> python webhooks/github_handler.py --port 8080
```

### Metrics

Runtime metrics are written to the `metrics/` directory.  Use
`cli/measure-success.py` to see the current dashboard.

---

## Iterative Workflow

Each sprint:

1. **Measure** — `python cli/measure-success.py`
2. **Identify gaps** — `python cli/validate-deps.py`, `python cli/dedup-report.py`
3. **Execute** — Phase A (build registry) → Phase B (refine) → Phase C (deduplicate)
4. **Repeat**

---

## Scope and backlog

See `docs/SCOPE_PURPOSE_STATUS_BACKLOG.md` for scope, current state, and the rolling backlog.

## Quickstart (workspace runner)

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

## Registry

The `registry/` directory is the sociosphere canonical repository registry. It is the single source of truth for all SocioProphet repositories tracked by this workspace controller.

| File | Purpose |
|------|---------|
| `registry/canonical-repos.yaml` | All tracked repos with layer, purpose, status, owners, notes |
| `registry/repository-ontology.yaml` | Controlled vocabulary and semantic bindings per repo |
| `registry/dependency-graph.yaml` | Inter-repo dependency edges (depends_on / dependents) |
| `registry/deduplication-map.yaml` | Overlap scan markers and consolidation candidates |

**Phase A (current):** 23 new repos added from SocioProphet org snapshot — all marked as "newly added, awaiting analysis":
- prophet-core-ops-brief, prophet-core-ledger, prophet-core-scaffolder, prophet-core-libs, prophet-core-contracts (Prophet Core cluster)
- prophet-core-infra, prophet-core-policy, prophet-core-query, prophet-core-catalog, prophet-core-ingest, prophet-domain-gaia-ontology, prophet-domain-gaia-curation-vault (GAIA data-plane cluster)
- delivery-excellence, delivery-excellence-automation, delivery-excellence-innersource, delivery-excellence-bounties, delivery-excellence-boards (DelEx governance cluster)
- sourceos-a2a-mcp-bootstrap (SourceOS/A2A bootstrap)
- workspace-inventory (workspace catalog)
- alexandrian-academy, regis-entity-graph (knowledge/semantic)
- Heller-Winters-Theorem (research/theory)
- tritrpc-notes-archive (archive)

**Phase B (next):** Extract actual ontologies, topics (LSA/LSI/LDA), and dependency edges from each repo's code and docs.

**Phase C (future):** Consolidate prophet-core-*, GAIA, DelEx, and SourceOS clusters; resolve deduplication markers.
