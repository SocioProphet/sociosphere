# ECOSYSTEM-BRIEF.md — SocioProphet ecosystem consolidated overview
# This document consolidates context from sociosphere draft PRs #12, #15, #16, #18, #19, #20, #21, #22, #23
# so that nothing is lost when those PRs are closed as superseded.

## What this PR/branch does

This branch (`copilot/research-socioprophet-ecosystem`) establishes the consolidated
registry + compliance + status layer for the full SocioProphet multi-repo workspace.
It supersedes sociosphere draft PRs #20, #21, and #23 (all competed on `registry/canonical-repos.yaml`).
Content from PRs #12, #15, #16, #18 is preserved in the registry and status documents.

---

## Structure added

```
registry/
  canonical-repos.yaml         ← 53 canonical repos with layer/role/status/tags/open_prs
  repository-ontology.yaml     ← 16 roles, 7 layers, 8 relationship types, semantic bindings
  dependency-graph.yaml        ← Topological levels + 21 directed dependency edges (no cycles)
  change-propagation-rules.yaml← 12 cascade rules (notify/ci-trigger/block)
  deduplication-map.yaml       ← 8 dedup entries (1 in-progress, 5 pending, 2 dismissed)

engines/
  ontology_engine.py           ← Role/tag/layer query engine; validates all roles/layers
  propagation_engine.py        ← BFS cascade computation; cycle detection; topological order
  status_reporter.py           ← Ecosystem dashboard + critical path + gap report

status/
  ecosystem-status.yaml        ← Live snapshot of all repos: PRs, readiness, receipt-path chain
  pr-register.yaml             ← All 81 open PRs with merge priority and merge order

telemetry/
  compliance-policy.yaml       ← Standards requirements per role/layer/priority
  compliance_checker.py        ← CLI compliance checker (exit 0 clean / exit 1 violations)

governance/
  MERGE-ORDER.md               ← 6-wave safe merge order for all open PRs
  CANONICAL_SOURCES.yaml       ← Updated with full namespace → repo mapping (50 namespaces)

manifest/
  workspace.toml               ← Expanded from 10 to 21 repos (URLs for remote repos)
  workspace.lock.json          ← Structure updated; rev/tree_hash still null pending fetch

.github/workflows/
  compliance.yml               ← New CI job: registry-validate + compliance-check

Makefile                       ← New targets: registry-validate, status, compliance-check, workspace-check
```

---

## Content preserved from superseded draft PRs

### From sociosphere PR#20 (49-repo registry)
- Dependency graph structure and propagation rules design
- Deduplication groups: speechlab, cloudshell-fog, hyperswarm, sourceos-workspace
- DevOps automation approach (absorbed into compliance-policy.yaml + CI workflow)

### From sociosphere PR#21 (23-repo registry)
- 8 cluster taxonomy (now expanded to 7 layers in repository-ontology.yaml)
- GAIA data-plane cluster with 7 repos
- DelEx governance cluster
- Phase B/C work tracking (now in deduplication-map.yaml + ecosystem-status.yaml)

### From sociosphere PR#23 (53-repo registry + engines)
- 53-repo canonical registry (this PR uses same scope)
- Engine architecture: OntologyEngine, PropagationEngine, MetricsCollector (present here)
- 10 change-propagation rules (expanded to 12)
- 64 unit tests mentioned in PR#23 — test suite to be added in follow-on PR

### From sociosphere PR#22 (automation framework)
- Rate limiter, webhook, scheduler concepts documented in compliance-policy.yaml
- Auto-merge handler logic noted in MERGE-ORDER.md (defer: risky until registry stable)
- Kubernetes/Docker deployment spec deferred — should be wired into prophet-platform-standards ADR-040 Tekton pipeline

### From sociosphere PR#18 (FIPS compliance artifacts)
- FIPS guide content referenced in compliance-policy.yaml (REQ-F01 through REQ-F04)
- Zero-trust bindings in ontologies/ directory (sociosphere-fips.ttl, sociosphere-fips-schema.jsonld) — already on main
- TriTRPC FIPS spec referenced in compliance-policy.yaml

### From sociosphere PRs #15, #16 (live-receipt path)
- Receipt path chain documented in status/ecosystem-status.yaml (receipt_path_chain section)
- 7-step chain with gap identified: step 7 (agentplane receipt builder) has no PR

### From sociosphere PR#12 (workspace spine hardening)
- runner v0.2 content: lock-verify command to be added to tools/runner/runner.py in follow-on
- Workspace hardening contract documented in docs/WORKSPACE_HARDENING_MATRIX.md (existing on branch)

---

## Known remaining gaps (for follow-on PRs)

1. **Test suite** — 64 unit tests mentioned in PR#23 not yet written; add in follow-on
2. **runner lock-verify** — Add `lock-verify` command to `tools/runner/runner.py` (from PR#12)
3. **Registry live resolution** — `runner fetch` to populate `rev`/`tree_hash` in lock file
4. **agentplane receipt builder** — No PR exists; needs to be created after Wave 4 merges
5. **gaia-world-model** — 5 open issues, 0 PRs; needs architectural PR in Phase B
6. **FIPS triage** — 10 FIPS PRs in socioprophet-standards-storage need chaining (see MERGE-ORDER.md)
