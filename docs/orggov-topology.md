# OrgGov Estate Topology v0.1

## Purpose

OrgGov Estate Topology v0.1 makes Sociosphere the coordination and propagation authority for Organization Governance Control Plane v0.

The topology registers ownership, dependency direction, change-propagation rules, release readiness, and evidence references for the cross-repo OrgGov product loop:

```text
Objective → Workroom → Actor → Role → Policy → Asset → Action → Evidence → Review → Outcome → Score → Learning
```

## Contract files

- `schemas/orggov-topology.v0.1.schema.json`
- `registry/orggov-topology.v0.1.json`
- `tools/validate_orggov_topology.py`

## Invariants

- Every canonical repo must be listed explicitly.
- Every ownership entry must have an owner repo and downstream repos.
- Dependency and change-propagation records must reference canonical repos.
- Release readiness must identify the merged slices and remaining first-pass lanes.
- Public topology fixtures must set `provenance.nonSecret` to true.

## Cross-repo links

- Parent: `SocioProphet/prophet-platform#406`
- Sociosphere workstream: `SocioProphet/sociosphere#272`
- SourceOS remaining lane: `SourceOS-Linux/sourceos-syncd#13`
