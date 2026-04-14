# SociOS / SourceOS Standards Index

This is the canonical index of standards. Standards define **contracts**: what MUST/SHOULD/MAY happen, and how we prove it.

## Status Legend
- **Implemented**: implemented in code/pipelines with a working reference path
- **Draft**: written, but implementation is partial or pending
- **Planned**: placeholder stub; design intent only

## Build & Release Standards

- **[SourceOS Build Plane Standard v0.1](./build-plane/README.md)** — **Draft / Implemented-in-parts**  
  Tekton lanes, Argo CD promotion model, reproducibility requirements, privileged builder isolation.

- **[Artifact & Promotion Standard v0.1](./artifact-promotion/README.md)** — **Draft**  
  Streams, naming, digest pinning, promotion repo layout, rollback, retention.

- **Toolchain Pinning Standard v0.1** — **Planned**  
  `IMAGES.lock`, digest refresh rules, “no floating tags” policy.

- **Release Versioning & Compatibility Standard v0.1** — **Planned**  
  Standard versioning, deprecation rules, compatibility matrices for protocol + artifacts.

## Protocol & Conformance Standards

- **[TriRPC v0 Conformance Standard v0.1](./conformance/trirpc-v0/README.md)** — **Implemented**  
  Golden schema fingerprint + smoke checks; used as a gate in build pipelines.

- TriRPC Protocol Versioning & Compatibility Spec v0.1 — **Planned**  
  Negotiation, error registry, capability negotiation.

## Operational Standards

- Builder Pool & Privileged Workloads Standard v0.1 — **Planned**  
  Node labels/taints, namespace policy, storage sizing, PodSecurity rules, KVM constraints.

- Observability Standard v0.1 — **Planned**  
  Correlation IDs, build metrics, logs, traces, dashboards.

## Notes

- Standards MUST be referenced by repos that implement them (README linking back to standards).
- Standards SHOULD include a reference implementation path and a test/gate when possible.
