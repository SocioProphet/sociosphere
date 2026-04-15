# Controlled Glossary

Authoritative term definitions for all concepts managed within the SocioProphet
workspace controller ecosystem. Terms here are referenced from ontology files
(`ontologies/sociosphere.jsonld`, `ontologies/sociosphere.ttl`) and from the
formal contract specification.

---

## Repo roles

| Term | Definition |
|---|---|
| **component** | A self-contained service or application that provides a discrete feature or capability. May be composed by the workspace but is independently deployable. |
| **adapter** | A boundary-translation layer that bridges two systems or protocols. Adapters are thin and must not contain domain logic. |
| **tool** | A utility or automation script consumed by the workspace controller itself (not by downstream components). |
| **protocol** | A formal wire-format specification and/or reference implementation. Not a service; consumed as a library or submodule. |
| **execution-plane** | A runtime environment or agent orchestrator that hosts and schedules components. |
| **library** | A reusable code module with a stable API, consumed as a dependency. |
| **ontology** | A structured vocabulary and knowledge graph that defines concepts, relationships, and constraints across the ecosystem. |
| **topic-pack** | A curated collection of topics (namespace slashes, tag sets) used for routing, classification, and discovery. |
| **security** | A module that enforces identity, access control, zero-trust, or cryptographic guarantees. |
| **standards** | A normative specification document or schema that governs interoperability. |
| **replay** | A module that records, replays, or audits interactions for correctness and governance. |
| **docs** | Documentation-only content; no runtime artifact. |

---

## Workspace and manifest concepts

| Term | Definition |
|---|---|
| **workspace** | The top-level coordination unit managed by `sociosphere`. Defined in `manifest/workspace.toml`. |
| **manifest** | The TOML file (`manifest/workspace.toml`) declaring all repos, roles, and metadata. |
| **lock file** | `manifest/workspace.lock.json` — the deterministic snapshot of all resolved `rev` SHAs for every manifest entry. |
| **submodule** | A Git submodule that pins a dependency at an exact commit SHA, used for protocol and third-party repos. |
| **pin** | The act of recording an exact `rev` (commit SHA) for a dependency so builds are reproducible. |
| **pin bump** | An explicit, reviewed commit that advances a dependency's pinned `rev` to a newer commit or tag. |
| **materialization** | The process of checking out all workspace repos at their pinned revisions into the local directory tree. |
| **lock-verify** | The CI step that confirms every manifest entry with a `url` has a corresponding, non-null `rev` in the lock file. |
| **topology check** | The CI step that enforces directionality rules: `sociosphere → tritrpc` is allowed; `tritrpc → sociosphere` is forbidden. |

---

## Dependency and contract concepts

| Term | Definition |
|---|---|
| **upstream** | A dependency that this repo consumes. Changes upstream may require downstream adaptation. |
| **downstream** | A consumer of this repo's output. Breaking changes here cascade downstream. |
| **upstream contract** | The interface (API surface, data schema, wire format) that an upstream repo publishes and this repo relies on. |
| **downstream contract** | The interface this repo publishes for downstream consumers. |
| **directionality** | The rule that dependency edges must flow from workspace-level to protocol-level, never the reverse. |
| **commingling** | The prohibited pattern of mixing concerns across the workspace ↔ protocol boundary. |

---

## Protocol / TriTRPC concepts

| Term | Definition |
|---|---|
| **TriTRPC** | A three-valued RPC protocol that encodes trust using trit (−1/0/+1) signals rather than binary true/false. |
| **trit** | A three-valued signal: negative (−1), neutral (0), or positive (+1). The fundamental unit of trust in TriTRPC. |
| **trust encoding** | The rules for composing trit values across a computation graph to produce a composite trust assertion. |
| **trit-to-trust mapping** | The normative specification for converting trit sequences to human-readable trust labels for agent-plane participants. See `docs/notes/trit-to-trust.md` for consolidation status. |

---

## Governance and provenance concepts

| Term | Definition |
|---|---|
| **provenance** | A traceable record of where an artifact came from, who produced it, and when. |
| **canonical source** | The single authoritative file or repository for a given fact, document, or definition. When sources conflict, the canonical source wins. |
| **namespace ownership** | The mapping from a namespace (e.g., a URL path prefix or topic prefix) to the repo responsible for maintaining it. See `governance/CANONICAL_SOURCES.yaml`. |
| **supply-chain policy** | Rules governing which external dependencies may be introduced and how they must be audited. |

---

## CI / automation concepts

| Term | Definition |
|---|---|
| **hygiene check** | CI step that rejects macOS cruft files (`.DS_Store`, `__MACOSX/`, `._*`) and verifies submodule pin sanity. Implemented in `tools/check_hygiene.sh`. |
| **compliance check** | CI step that validates repo metadata and governance requirements. Implemented in `telemetry/compliance_checker.py`. |
| **registry validation** | CI step that checks ontology roles and dependency-graph cycles. Implemented in `engines/ontology_engine.py`. |

---

*To add a term, open a PR editing this file and reference the relevant ontology IRI from `ontologies/sociosphere.jsonld`.*
