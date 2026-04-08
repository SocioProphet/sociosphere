# ECOSYSTEM-BRIEF (Archival)

> Status: **archival context only**.
>
> This document preserves a historical consolidation snapshot from superseded
> draft PR streams. It is retained for provenance and auditability, not as the
> normative current-state spec.

## Canonical current sources

Use these files for live truth:

- `manifest/workspace.toml` — declared repositories and roles
- `manifest/workspace.lock.json` — pinned revisions
- `registry/canonical-repos.yaml` — ecosystem registry inventory
- `docs/SCOPE_PURPOSE_STATUS_BACKLOG.md` — current scope and backlog
- `docs/INTEGRATION_STATUS.md` — current integration facts

## Historical snapshot preserved here

This archival brief originally consolidated context from sociosphere draft PRs
`#12, #15, #16, #18, #19, #20, #21, #22, #23` so that details were not lost
when those branches were superseded.

### Historical structure notes

```
registry/
  canonical-repos.yaml
  repository-ontology.yaml
  dependency-graph.yaml
  change-propagation-rules.yaml
  deduplication-map.yaml

engines/
  ontology_engine.py
  propagation_engine.py
  status_reporter.py

status/
  ecosystem-status.yaml
  pr-register.yaml

telemetry/
  compliance-policy.yaml
  compliance_checker.py

governance/
  MERGE-ORDER.md
  CANONICAL_SOURCES.yaml

manifest/
  workspace.toml
  workspace.lock.json
```

### Historical content capture (high level)

- Registry topology and propagation rule design from the PR#20/#21/#23 stream.
- Deduplication groups and phased consolidation planning.
- Automation framework ideas (rate limiting, webhook/scheduler orchestration).
- FIPS-related references and cross-links to ontology/spec artifacts.
- Receipt-path and workspace hardening notes from PR#12/#15/#16.

### Historical unresolved items (at time of snapshot)

1. Test-suite parity claims not yet fully implemented.
2. Additional runner hardening and lock workflows pending follow-on updates.
3. Registry live-resolution and receipt-builder work still open.

## Conflict handling

If this document conflicts with canonical current sources, canonical sources
win.
