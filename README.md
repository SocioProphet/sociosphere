# sociosphere (v0.1)

Workspace controller repo.

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
