# Runtime, Content, and Orchestration Placement

## Purpose

This note records the canonical placement for recent work around container manager choice, phase-relative orchestration, governed execution, content-addressed curation, and OpenShift / Giant Swarm / Docker / Kubernetes alignment.

The goal is to keep one constitutional home per concern and avoid introducing a rival top-level object model when existing workspace, execution, and contract surfaces already exist.

## Canonical ownership split

| Concern | Canonical repo | Why |
|---|---|---|
| Workspace placement, repo boundaries, donor/disposition tracking, integration ledger | `SocioProphet/sociosphere` | This repo owns workspace topology, canonical namespace ownership, manifest/lock governance, and cross-repo composition. |
| Transport-safe route handles, attestation wire notes, replay-safe framing, deterministic fixtures | `SocioProphet/TriTRPC` | This repo owns the transport/protocol surface and deterministic interoperability lane. |
| Validate/place/run/evidence/replay, runtime adapter selection behavior, promotion/reversal/session artifacts | `SocioProphet/agentplane` | This repo owns the execution control-plane lifecycle. |
| Shared typed contracts and additive schema patches | `SourceOS-Linux/sourceos-spec` | This repo owns the machine-readable contract layer shared across SourceOS / SociOS / agent-plane consumers. |
| Host realization, profiles, images, installers, builders, Linux-facing container/runtime integration | `SociOS-Linux/source-os` and adjacent Linux repos | These repos own the Linux and Nix realization surfaces for the control-plane contract. |
| Public narrative and buyer-readable explanation | product/docs/web repos | These repos may explain the model, but they are not the canonical home for machine contracts or repo-boundary law. |

## What belongs in each lane

### 1. `sociosphere`

Keep the cross-repo placement decision here:

- which repo owns which slice
- which upstream projects are direct dependencies, wrapped dependencies, maintained-fork candidates, or reference-only donors
- how runtime/container/orchestration decisions affect workspace composition
- how cross-repo changes propagate through manifest, lock, registry, and topology policy

### 2. `TriTRPC`

Only transport-safe parts belong here:

- route handles and route-policy transport notes
- policy attestation wire notes
- replay-safe references and control-word framing
- deterministic fixture and parity material

Do **not** move platform schema canon, Linux realization, or general orchestration doctrine here.

### 3. `agentplane`

Execution semantics belong here:

- placement and executor selection
- runtime adapter choice as execution behavior
- promotion / reversal / replay / evidence topology
- governed lifecycle for bundle or workload execution
- execution-time mapping from policy/evidence requirements to runtime posture

### 4. `sourceos-spec`

Contract work belongs here only when it must be shared and typed.

Prefer composition from existing schema families before adding new top-level types:

- `WorkloadSpec`
- `DataSphere`
- `RunRecord`
- `ExecutionSurface`
- `ExecutionDecision`
- `ContentRef`
- relevant control-plane tranche types such as isolation and release profiles

If gaps remain, add the smallest possible additive schema and reference existing types rather than re-declaring their fields.

### 5. `source-os` and Linux realization repos

Concrete Linux realization belongs here:

- CRI-O vs containerd realization
- Podman / toolbox / rootless container defaults
- host profile and image wiring
- installer/bootstrap/butane/ignition realization
- SELinux / network / storage / VM-or-container runtime integration

## Practical mapping for the recent work

### Container/orchestrator phase model

- workspace-level placement doctrine → `sociosphere`
- execution-time runtime-selection behavior → `agentplane`
- shared execution/environment contract composition → `sourceos-spec`
- concrete Linux implementation → `source-os` and Linux repos

### Content-curation and governed execution coupling

- content-addressed and execution-bound schema composition → `sourceos-spec`
- run/evidence/replay behavior → `agentplane`
- workspace-level composition and donor tracking → `sociosphere`

### OpenShift / Giant Swarm / Docker / Kubernetes alignment

Treat these as donor ecosystems and runtime adapters, not schema identities.

- upstream donor/disposition notes → `sociosphere`
- transport-safe interop notes → `TriTRPC`
- runtime adapter behavior → `agentplane`
- Linux host realization → `source-os`

## Guardrails

1. Do not create a new umbrella schema when the concern can be expressed by composition of existing typed contracts.
2. Do not move execution lifecycle semantics into Linux realization repos.
3. Do not move host/container runtime realization into `TriTRPC`.
4. Do not treat public web/docs surfaces as the canonical home for protocol or schema truth.
5. Do not let vendor-specific names become first-class contract vocabulary unless a generic contract cannot express the need.

## Immediate landing plan

1. Keep this repo as the canonical workspace-level placement note.
2. Land contract-composition follow-up in `sourceos-spec`.
3. Land execution/runtime-adapter follow-up in `agentplane`.
4. Land Linux realization follow-up in `source-os` and adjacent Linux repos.
5. Link public/docs surfaces back to these canonical homes rather than duplicating them.
