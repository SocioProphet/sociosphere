# Repository Analysis — SocioProphet/agentplane

**GitHub:** https://github.com/SocioProphet/agentplane  
**Role in ecosystem:** Execution control plane  
**Last analysed:** 2026-04-08

---

## 1. Repository Purpose & Identity

### What it does
The fleet-shaped control plane for reproducible agent execution. It takes bundles generated
by sociosphere, validates them, places them on executor nodes, runs them, and captures
structured evidence artifacts (Validation, Placement, Run, Replay). Designed to be
enterprise-aligned and survive any Linux install.

### Core responsibilities
- `bundles/` — bundle definitions (unit of deployment/execution; JSON with spec, policy,
  constraints).
- `runners/` — executor backends (today: `lima-process` for local VMs on macOS).
- `fleet/` — executor fleet inventory.
- `monitors/` — monitoring and control matrix
  (`monitors/generated/control-matrix/`).
- `policy/` — execution policy imports + definitions.
- `schemas/` — bundle and artifact schemas.
- `state/` — state management.
- `tests/` — test suite.
- `flake.nix` — Nix dev environment for reproducibility.
- Evidence-forward execution lifecycle: bundle → validate → place → run →
  emit `RunArtifact` + `ReplayArtifact`.

### What systems depend on it
- `sociosphere` — generates bundles that agentplane consumes (the seam is intentionally
  narrow; see `docs/sociosphere-bridge.md`).
- Agent workloads that need deterministic, evidenced execution.
- CI systems consuming `RunArtifact` + `ReplayArtifact` for audit.

### What it depends on
- **sociosphere** — generates bundles (upstream); emits workspace artifacts.
- Nix (reproducible builds).
- Lima (local VM executor backend — macOS dev).
- Fedora CoreOS / Silverblue (production fleet nodes).
- TritRPC (transport protocol for inter-service communication).

### Key files
- `README.md` — single work product overview (AgentOS + agentplane unification)
- `docs/sociosphere-bridge.md` — narrow seam spec between sociosphere and agentplane
- `docs/system-space.md` — enterprise-aligned system space strategy
- `docs/executors.md` — executor types
- `docs/instrumentation/` — instrumentation docs
- `docs/runtime-governance/` — runtime governance docs
- `bundles/README.md` — bundle directory overview
- `bundles/example-agent/` — canonical example bundle
- `flake.nix` — Nix dev environment
- `policy/` — policy definitions

---

## 2. Controlled Vocabulary & Ontology

### Key terms
| Term | Definition | Source |
|---|---|---|
| **Bundle** | Unit of deployment/execution: JSON containing spec, policy, constraints | `docs/sociosphere-bridge.md` |
| **ValidationArtifact** | Evidence that a bundle passed validation | `docs/sociosphere-bridge.md` |
| **PlacementDecision** | Which executor was selected and why | `docs/sociosphere-bridge.md` |
| **RunArtifact** | Evidence from a completed run | `docs/sociosphere-bridge.md` |
| **ReplayArtifact** | Evidence enabling deterministic replay | `docs/sociosphere-bridge.md` |
| **Executor fleet** | Set of available executor nodes | `docs/system-space.md` |
| **Lima** | macOS-based local VM; first "fleet node" in dev | `docs/system-space.md` |
| **lima-process** | Local executor backend | `docs/system-space.md` |
| **Fedora CoreOS** | Immutable container host OS for production fleet nodes | `docs/system-space.md` |
| **Fedora Silverblue** | Immutable workstation OS for developer fleet nodes | `docs/system-space.md` |
| **bootc / OCI-based OS** | Signed bootable container images (future system space evolution) | `docs/system-space.md` |
| **spec.policy.maxRunSeconds** | Bundle-owned execution timeout policy field | `docs/system-space.md` |
| **SOCIOSPHERE_WORKSPACE_INVENTORY_REF** | Environment variable carrying upstream sociosphere artifact reference | `docs/sociosphere-bridge.md` |
| **Control matrix** | Monitoring control matrix in `monitors/generated/` | `monitors/` |
| **Pointer model** | Promotion/rollback via digest/tag pointer swaps (mirrors OCI image model) | `docs/system-space.md` |
| **Non-AGPL policy** | Hard constraint: no AGPL dependencies allowed in this repo | `docs/system-space.md` |

### Domain-specific language
- agentplane is **system-space orchestration** — it answers: "Where does this run, under
  what constraints, and where is the evidence?"
- The **seam with sociosphere is narrow by design**: sociosphere emits artifacts, agentplane
  consumes them. agentplane must not rescan the workspace.
- **Evidence-forward** means every run emits Validation, Placement, Run, Replay artifacts
  before the run is considered complete.
- Timeouts are **bundle-owned** policy (`spec.policy.maxRunSeconds`), not executor defaults.

### Semantic bindings to other repos
- **← sociosphere**: sociosphere is upstream; generates bundles agentplane executes.
- **→ TritRPC**: transport protocol for evidence artifacts and service communication.
- **↔ socioprophet** (standalone): agentplane is a sub-directory of socioprophet; the
  standalone agentplane repo is the execution-plane authority.
- **↔ new-hope (indirect)**: new-hope Receptor System uses agentplane-style execution
  evidence for audit trails.

---

## 3. Topic Modeling

| Topic | Keywords | Weight |
|---|---|---|
| Bundle-based execution | bundle, validate, place, run, evidence, replay | dominant |
| Immutable OS / fleet | CoreOS, Silverblue, bootc, OCI, fleet nodes, Lima, immutable | dominant |
| Evidence-forward audit trail | ValidationArtifact, PlacementArtifact, RunArtifact, ReplayArtifact | dominant |
| Reproducible builds | Nix flake, deterministic, digest, pointer model | high |
| Execution policy | maxRunSeconds, bundle-owned policy, executor placement | high |
| Sociosphere bridge | upstream artifacts, narrow seam, bundle generation | high |
| Enterprise alignment | OpenShift, CoreOS, RHEL lineage, production readiness | medium |
| Monitoring / control | control matrix, monitors, instrumentation | medium |

---

## 4. Dependency Graph

### Direct dependencies
- `sociosphere` (bundle source, upstream workspace artifacts)
- Nix (build reproducibility)
- Lima (dev executor)
- Fedora CoreOS (production executor)
- TritRPC (transport)

### Dependent systems
- Agents / workloads that execute via agentplane
- CI systems consuming `RunArtifact` + `ReplayArtifact` for audit

### Cross-repo impact when agentplane changes
- Bundle schema change → sociosphere must update bundle generation to match.
- Artifact schema change → any system consuming artifacts must update.
- Executor backend change → replay artifacts may differ; replay tests must re-run.

---

## 5. Change Impact Rules

| What changed | Downstream repos affected | DevOps actions | Governance gates |
|---|---|---|---|
| `schemas/` bundle schema | `sociosphere` (must generate conforming bundles) | Sociosphere bundle generation update; re-validate | Bundle schema version bump; coordinated release |
| Executor backend | Run + Replay artifacts may differ | Re-run test suite; replay verification | Executor compatibility ADR |
| `policy/` | Bundle policy evaluation changes | Policy regression tests | Security/ops review |
| `flake.nix` | Dev environment reproducibility | Nix build validation; lock hash update | Lock hash review |
| Fleet topology | Placement decisions change | Fleet inventory update; placement re-test | Ops review |
| Artifact schema | All systems consuming artifacts | Schema migration | Schema registry review |
