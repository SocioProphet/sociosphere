# SourceOS substrate control-plane integration

This document records the canonical landing map for the Fedora Asahi + Nix control-plane work so the workspace controller can register and materialize it without collapsing substrate, standards, and runtime concerns into a single repo.

## Purpose

We are introducing a workstation/edge substrate lane with these properties:

- Fedora Asahi host baseline on Apple Silicon
- Nix + flakes + Home Manager control plane over the host
- staged promotion before host activation
- rollback at multiple layers (Nix generations, container digests, filesystem snapshots)
- evidence-bearing execution and replay for stage/prod transitions
- typed contracts for boot surfaces, storage surfaces, mounts, and staged deployments

Sociosphere is **not** the implementation home for these features. Its job is to:

1. register the canonical repositories,
2. encode dependency direction,
3. materialize the workspace,
4. enforce topology and trust policy.

## Canonical landing map

### 1. Substrate implementation

**Canonical repo:** `SociOS-Linux/SourceOS`

Owns:

- Fedora Asahi substrate policy
- Nix bootstrap and flake layout
- Home Manager and service modules
- storage/mount class implementation
- staged update / promote / rollback mechanics
- Asahi-specific boot / EFI surface operational guidance

### 2. Typed contracts

**Canonical repo:** `SourceOS-Linux/sourceos-spec`

Owns machine-readable contracts for:

- `BootSurface`
- `StorageSurface`
- `MountBinding`
- `StagedDeployment`

These contracts are normative inputs for workstation lanes and execution evidence.

### 3. Workstation/CI conformance

**Canonical repo:** `SociOS-Linux/workstation-contracts`

Owns:

- workstation lane schema for the Fedora Asahi + Nix control-plane lane
- contract validation for the lane
- truth-lane examples and conformance expectations

### 4. Stage / run / evidence / replay

**Canonical repo:** `SocioProphet/agentplane`

Owns:

- stage bundle definition
- stage VM module + smoke tests
- placement / run / replay artifacts for the substrate lane

### 5. Standards authority

**Canonical repos:**

- `SocioProphet/prophet-platform-standards` — rollout / DevSecOps / observability standards
- `SocioProphet/socioprophet-standards-storage` — storage / snapshot / mount doctrine

## Dependency direction

The intended dependency direction is:

```text
sociosphere
  -> SourceOS
  -> sourceos-spec
  -> workstation-contracts
  -> agentplane
  -> prophet-platform-standards
  -> socioprophet-standards-storage
```

The inverse direction is forbidden. In particular:

- `SourceOS` must not depend on `sociosphere` runtime internals.
- `sourceos-spec` must not depend on substrate implementation details.
- `workstation-contracts` defines conformance and must not become the runtime implementation.
- `agentplane` may consume contracts and substrate bundle inputs but does not own the substrate.

## Pending workspace-controller actions

These are the follow-on edits that should be made once registry normalization work is complete:

1. add canonical repo entries for:
   - `SociOS-Linux/SourceOS`
   - `SourceOS-Linux/sourceos-spec`
   - `SociOS-Linux/workstation-contracts`
2. add dependency edges from `sociosphere` to those repos
3. add canonical namespace mappings for the SourceOS substrate and workstation lane
4. deconflict `source-os` vs `SourceOS` naming in registry and deduplication tracking

## Why this note exists before manifest edits

Current registry files carry duplicated content blocks and mixed historical/current material. Until those files are normalized, this note is the stable capture point for the intended landing map and dependency direction.

## Immediate next patches expected in downstream repos

- `SourceOS`: substrate architecture and operational docs + flake scaffold
- `sourceos-spec`: new boot/storage/staging schemas
- `workstation-contracts`: workstation contract schema v0.2 for Nix-backed lanes
- `agentplane`: sourceos-asahi stage bundle and integration notes

## Acceptance condition for workspace integration

Sociosphere integration is complete when:

- the canonical repo inventory contains the three Linux-side repos above,
- the dependency graph reflects the allowed direction,
- the workspace manifest can materialize those repos,
- topology checks pass without introducing reverse dependencies.
