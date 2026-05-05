# Evidence Fabric Validation Runbook

## Status

Bootstrap validation runbook for the evidence-fabric registry slices.

## Purpose

This document provides the current validation entrypoints for the evidence-fabric repo-family and surface-integration registry files.

A later follow-up should wire these commands into `make validate` once an update-existing-file path is used safely.

## Validation commands

Run from the Sociosphere repository root:

```bash
python3 tools/validate_evidence_fabric_repos.py
python3 tools/validate_evidence_fabric_surface_integrations.py
```

Expected output:

```text
OK: evidence fabric repo registry is valid
OK: evidence fabric surface integrations are valid
```

## Files covered

- `registry/evidence-fabric-repos.yaml`
- `registry/evidence-fabric-surface-integrations.yaml`

## What is checked

The repo-family validator checks:

- all planned evidence repos are present,
- each planned repo has ownership, status, role, purpose, and layer metadata,
- all repos remain marked `planned` until created,
- architecture invariants are present,
- phase-1 acceptance gates are defined.

The surface-integration validator checks:

- Exodus Dashboard coverage,
- Sociosphere workspace coverage,
- email ingest coverage,
- cloud-drive ingest coverage,
- local-file ingest coverage,
- SourceOS office shell coverage,
- browser and terminal capture coverage,
- notes and mobile-device export coverage,
- search and knowledge projection coverage,
- proof-pack export coverage,
- Exodus acceleration metrics,
- minimum user workflow steps.

## Follow-on

Add a `validate-evidence-fabric` Makefile target and include it in the top-level `validate` or `workspace-check` target after this registry slice lands.
