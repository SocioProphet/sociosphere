# SourceOS Build Plane Standard (v0.1)

Status: **Draft / Implemented-in-parts**  
Owner: SourceOS / SociOS-Linux build-plane maintainers  
Scope: Tekton + Argo CD build, test, publish, and promote of SourceOS artifacts.

## 1. Purpose

This standard defines the **build plane contract** for SourceOS:

- How we build immutable OS artifacts (COSA / bootc lanes).
- What gates must pass before artifacts are publishable/promotable.
- What outputs are produced (OCI, OSTree, disk images, metadata).
- How builds are made reproducible and auditable (digests, SBOM, provenance).
- How promotions occur (GitOps via Argo CD) across streams/environments.

The build plane is designed to be portable across Kubernetes distributions:
- **k3s/k3, kubeadm, RKE2** are first-class.
- OKD/OpenShift may be supported, but no OpenShift-only APIs are required.

## 2. Definitions

- **Build Plane**: the orchestration layer (Tekton + Argo CD) that turns source + configs into signed artifacts and promotions.
- **Lane**: a cohesive pipeline category (e.g., `gate`, `cosa`, `bootc`, `promote`).
- **Gate**: a required verification stage that must pass before build/publish/promotion.
- **Stream**: a lifecycle channel (e.g., `next`, `testing`, `stable`).
- **Artifact**: output of a lane (OCI image digest, OSTree commit, disk image, SBOM, attestation).
- **Toolchain Pin**: immutable references (container image digests) used for build steps.

## 3. Required Lanes (Minimum)

### 3.1 Gate Lane (Required)
The build plane MUST support gating on **TriRPC v0 schema integrity**:
- `tools/conformance/trirpc-v0` in `sociosphere`
- `make check` must pass

Rationale: TriRPC schemas define an interop surface used by runners/adapters and capability IO. Drift without explicit review is unacceptable.

### 3.2 COSA Lane (Required for CoreOS-style artifacts)
Uses CoreOS Assembler (COSA) to build:
- OS images (qcow2/raw/metal/iso where configured)
- OSTree commits
- **ostree-native container** (OCI), optionally pushed to a registry

### 3.3 Promotion Lane (Required)
Promotion MUST be GitOps:
- Tekton updates a Git repo (or path) representing environment pins
- Argo CD reconciles desired state into clusters/environments

## 4. Recommended Lanes (Next)
### 4.1 bootc Lane (Recommended)
bootc produces immutable OS as container images (and optionally disk images).
This is the forward-leaning lane for “Silverblue-like” and unified image-mode outputs.

### 4.2 Kola/QEMU Test Lane (Optional, but strongly recommended)
If KVM-capable nodes exist, enable a test lane to run kola/QEMU validation.
This lane MUST be optional because not all clusters expose `/dev/kvm`.

## 5. Inputs and Outputs

### Inputs
- Config Git (for COSA lane): e.g., `socios-coreos-config`
- Source repos (for bootc lane): Containerfile + scripts
- Toolchain pins: image digests for COSA, git, python, SBOM tool, signing tools
- Secrets:
  - Git credentials (optional; public-only works without)
  - Registry credentials (required to push)
  - Signing keys (if not using keyless flow)

### Outputs (Minimum)
Every build MUST emit:
- A primary artifact reference:
  - OCI image digest (preferred), and/or OSTree commit hash
- Logs and build metadata
- SBOM (SPDX or CycloneDX) for build outputs
- Provenance attestation (signed)

## 6. Reproducibility Requirements

The build plane MUST support:
- Pinning all builder images **by digest** (no floating tags in “locked” modes).
- A human-reviewable lock file (e.g., `IMAGES.lock`) that records:
  - COSA image digest
  - git clone image digest
  - python / tooling image digests

A build is considered “reproducible-enough” when the same inputs + toolchain pins yield identical outputs or explainable, tracked differences.

## 7. Security Model

### 7.1 Privileged Builds
COSA tasks typically require privileged execution and may require KVM.

Policy:
- Privileged tasks MUST be scheduled only to a dedicated builder pool:
  - `nodeSelector: sourceos.build/pool=os-builders`
  - `taint: sourceos.build/privileged=true:NoSchedule`
  - Tekton TaskRunSpecs apply toleration ONLY to privileged tasks

### 7.2 Namespace Policy
Builder workloads SHOULD run in a dedicated namespace (e.g., `sourceos-build`),
with restricted permissions for non-privileged lanes.

### 7.3 Secrets Handling
- Secrets MUST not be committed to repos.
- Provide templates checked into repo (`*.template.yaml`) for operators.

## 8. Promotion Model (Argo CD)

- Environments/streams are declared in Git.
- Promotion updates a pinned artifact digest (not a mutable tag).
- Argo CD syncs target clusters to the pinned digest.

Minimum promotion artifacts:
- `environments/<stream>/kustomization.yaml` or similar, referencing digest pins.

## 9. Standard Pipeline Taxonomy

Suggested names (non-binding but recommended):
- `sourceos-trirpc-gate` (clone sociosphere → `make check`)
- `sourceos-cosa-build` (build CoreOS-style artifacts)
- `sourceos-build` (composed: gate → build)
- `sourceos-bootc-build` (build bootc image-mode artifacts)
- `sourceos-promote` (update env pins, open PR or commit)

## 10. Operator and Developer Quickstart

Local (developer):
- `cd sociosphere/tools/conformance/trirpc-v0 && make check`

Cluster (operator):
- Apply Tekton tasks/pipelines
- Provide builder node pool + storage
- Provide registry credentials if pushing artifacts

