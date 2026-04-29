# Upstream Bindings — Agent / Eval Fabric / Ray Lifecycle (Draft v0.1)

## Purpose

This note records the canonical upstream and downstream repositories currently shaping the SocioProphet agent specification, governed evaluation fabric, and Ray-aligned lifecycle stack.

The goal is to make the repo split explicit so that future work lands in the correct place and cross-repo drift is easier to detect.

## Decision summary

| Lane | Canonical repo | Current disposition | Why |
|---|---|---|---|
| Protocol / deterministic transport | `SocioProphet/TriTRPC` | **Canonical upstream** | Stable TritRPC v1, fixtures, deterministic ports, and vNext design pack belong at the protocol layer |
| Workspace controller / orchestration inventory | `SocioProphet/sociosphere` | **Canonical meta-workspace controller** | Owns manifest/lock, runner semantics, topology enforcement, integration ledger, and cross-repo registry metadata |
| Policy and governed action semantics | `SocioProphet/policy-fabric` | **Canonical policy/control repository** | Policy contracts, validation evidence, and governance workflow belong in the policy control repo |
| Runtime evaluation and competition surfaces | `SocioProphet/prophet-platform` | **Canonical executable consumer** | Eval-fabric runtime, provenance routes, readiness, receipt emission, and downstream suite execution live here |
| Standards / agent profiles / test-building-block semantics | `SocioProphet/socioprophet-agent-standards` | **Canonical standards upstream** | Evidence, control/gating/graduation, orchestration-Ray, and logical-statistical test profiles belong here |
| Ray/KubeRay deployment baseline | `SocioProphet/prophet-platform-fabric-mlops-ts-suite` | **Canonical deployment baseline** | Multi-cluster fabric and Ray Train/Serve lifecycle deployment semantics belong here |

## Current interpretation

### 1. `TriTRPC`

Use as the protocol and fixture source of truth.

Expected responsibilities:
- canonical transport semantics
- deterministic fixtures
- port parity
- vNext design exploration

Do not place workspace-control or test-suite orchestration policy here.

### 2. `sociosphere`

Use as the canonical integration and orchestration map.

Expected responsibilities:
- workspace manifests and locks
- repo role declarations
- topology rules
- integration-status notes
- registry-level bindings between upstream standards and downstream runtime repos

### 3. `policy-fabric`

Use as the governed policy/control repository.

Expected responsibilities:
- policy contracts
- validation and replay evidence for policy surfaces
- governed decision workflows

### 4. `prophet-platform`

Use as the executable consumer for the eval-fabric lane.

Expected responsibilities:
- readiness and runtime surfaces
- route, provenance, and competition endpoints
- downstream suite fixtures and tests
- evidence receipt emission
- migration/versioning execution path

### 5. `socioprophet-agent-standards`

Use as the canonical profile source for:
- evidence/provenance vocabulary
- control/gating/graduation vocabulary
- orchestration and Ray lifecycle vocabulary
- logical-statistical test-building-block vocabulary
- examples and profile manifests

### 6. `prophet-platform-fabric-mlops-ts-suite`

Use as the Ray / KubeRay deployment and lifecycle baseline.

Expected responsibilities:
- Ray Train / Serve deployment baseline
- MLOps operator composition
- production-facing cluster profile for model lifecycle work

## Integration rule

The intended direction is:

`TriTRPC` + `socioprophet-agent-standards` + `policy-fabric` + `prophet-platform-fabric-mlops-ts-suite` → inform and constrain `prophet-platform` runtime behavior, while `sociosphere` records and orchestrates the cross-repo relationship.

The reverse flow should be limited to:
- implementation feedback
- validation findings
- naming/alignment fixes

## Immediate practical use

This note should guide where to land the next classes of work:
- new runtime eval-fabric endpoints → `prophet-platform`
- new agent/gating/graduation profile language → `socioprophet-agent-standards`
- new policy contracts and governed decision artifacts → `policy-fabric`
- new Ray/KubeRay deployment baseline work → `prophet-platform-fabric-mlops-ts-suite`
- workspace-level integration maps and repo split notes → `sociosphere`

## Status

Captured in repo as an integration note. Not yet linked from the canonical integration ledger.
