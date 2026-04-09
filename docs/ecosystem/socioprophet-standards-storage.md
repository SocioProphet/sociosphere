# Repository Analysis — SocioProphet/socioprophet-standards-storage

**GitHub:** https://github.com/SocioProphet/socioprophet-standards-storage  
**Role in ecosystem:** Standards authority — storage, data contracts, benchmarking  
**Last analysed:** 2026-04-08

---

## 1. Repository Purpose & Identity

### What it does
The normative standards and measurement authority for interoperable storage, data contracts,
and benchmarking across the SocioProphet incident intelligence / ChatOps platform. Defines
MUST/SHOULD/MAY requirements for storage contexts, data formats, service interfaces,
observability, security, and graph layers.

### Core responsibilities
- Define 7 storage contexts (event stream, incident state, artifacts, search, vectors,
  graphs, metrics) — `docs/standards/010-storage-contexts.md`.
- Mandate data contracts: Avro (events), Arrow + Parquet (analytics), JSON-LD
  (semantic/provenance) — `docs/standards/020-data-formats.md`.
- Standardize service interfaces: TritRPC for RPC; event bus topics for async —
  `docs/standards/030-service-interfaces-tritrpc.md`.
- Specify execution: Apache Beam (batch/stream), Ray (training/serving/placement).
- Define storage portfolio: Postgres (system-of-record), OpenSearch (text), vector/graph
  stores (workload-triggered) — `docs/standards/060-storage-decision-guidance.md`.
- Provide a 30-workload benchmark harness with latency/throughput/cost/recovery dimensions —
  `benchmarks/workloads/`.
- Maintain ADR collection for architectural decisions — `adr/`.
- Cross-reference graph layer: RDF/SPARQL, property graph, AtomSpace-style hypergraph —
  `docs/standards/070-graph-rdf-hypergraph.md`.
- Serve as upstream invariant provider for `socioprophet-standards-knowledge` —
  `docs/standards/080-knowledge-context.md`.

### What systems depend on it
- **socioprophet-standards-knowledge** — explicitly upstream:
  "Upstream platform invariants live in: SocioProphet/socioprophet-standards-storage"
  (`standards-knowledge/README.md`).
- **prophet-platform** — follows the storage blueprint
  (`prophet-platform/docs/STORAGE_INTEGRATION_BLUEPRINT.md`).
- All platform services that store data.

### What it depends on
- **TriTRPC** — standard 030 mandates TritRPC for service interfaces.
- Apache Beam, Ray (execution standards).
- Postgres, OpenSearch (storage portfolio).
- OpenTelemetry — standard 040.
- JSON-LD context specification.

### Key files
- `README.md` — full description, repo map, topics, graph layer note
- `docs/standards/000-platform-standards.md` — platform-level invariants
- `docs/standards/005-design-philosophy.md`
- `docs/standards/010-storage-contexts.md` — 7 storage contexts
- `docs/standards/020-data-formats.md` — Avro, Arrow+Parquet, JSON-LD
- `docs/standards/030-service-interfaces-tritrpc.md` — TritRPC service standard
- `docs/standards/040-observability-otel.md` — OpenTelemetry
- `docs/standards/050-security-oidc-policy.md` — OIDC + OPA policy
- `docs/standards/060-storage-decision-guidance.md`
- `docs/standards/070-graph-rdf-hypergraph.md` — RDF, property graph, hypergraph
- `docs/standards/080-knowledge-context.md` — knowledge context bridge
- `benchmarks/workloads/` — 30 workload YAML definitions
- `benchmarks/harness/` — harness scaffold
- `adr/` — Architecture Decision Records

---

## 2. Controlled Vocabulary & Ontology

### Key terms
| Term | Definition | Source |
|---|---|---|
| **Storage contexts** | 7 named domains: event stream, incident state, artifacts, search, vectors, graphs, metrics | `docs/standards/010-storage-contexts.md` |
| **Data contracts** | Avro schemas for events; Arrow+Parquet for analytics | `docs/standards/020-data-formats.md` |
| **JSON-LD** | Semantic/provenance overlays using linked-data context | `docs/standards/020-data-formats.md` |
| **TritRPC** | Mandated service interface protocol (standard 030) | `docs/standards/030-service-interfaces-tritrpc.md` |
| **Event bus topics** | Async flow contracts for decoupled service communication | `docs/standards/030-service-interfaces-tritrpc.md` |
| **Beam** | Apache Beam: batch/stream transform execution standard | `README.md` |
| **Ray** | Distributed training/serving/task placement standard | `README.md` |
| **Benchmark harness** | 30-workload definitions with latency/throughput/cost/recovery dimensions | `benchmarks/` |
| **MUST/SHOULD/MAY** | RFC-style normative language used throughout standards docs | `docs/standards/` |
| **Property graph** | Labeled graph model for connected data | `docs/standards/070-graph-rdf-hypergraph.md` |
| **Hypergraph** | Generalized graph (AtomSpace-style) where edges connect >2 nodes | `docs/standards/070-graph-rdf-hypergraph.md` |
| **SPARQL** | Query language for RDF graphs | `docs/standards/070-graph-rdf-hypergraph.md` |
| **AtomSpace** | OpenCog hypergraph knowledge representation model | `docs/standards/070-graph-rdf-hypergraph.md` |
| **OIDC** | OpenID Connect: identity standard (security, standard 050) | `docs/standards/050-security-oidc-policy.md` |
| **OPA** | Open Policy Agent: policy evaluation engine (standard 050) | `docs/standards/050-security-oidc-policy.md` |

### Domain-specific language
- Standards use **normative language** (MUST/SHOULD/MAY) — not guidelines.
- Storage choices are **workload-triggered**: vector/graph stores are only adopted when
  benchmarks justify them.
- The platform is treated as a set of **contexts**, not a single database.
- Benchmark workloads are **first-class artifacts**: they live in version control and gate
  storage decisions.

### Semantic bindings to other repos
- **→ TriTRPC**: standard 030 mandates TritRPC; cross-references TriTRPC repo.
- **→ standards-knowledge**: standard 080 is the bridge; this repo is the upstream invariant
  provider.
- **→ prophet-platform**: storage blueprint is the normative reference for prophet-platform's
  infra choices.

---

## 3. Topic Modeling

| Topic | Keywords | Weight |
|---|---|---|
| Storage architecture | Postgres, OpenSearch, vector-search, graph-database, 7 contexts | dominant |
| Data contracts / formats | Avro, Arrow, Parquet, JSON-LD, provenance, schemas | dominant |
| Graph / knowledge layer | RDF, SPARQL, property graph, hypergraph, AtomSpace | high |
| Incident intelligence / ChatOps | incident state, event stream, artifacts, observability | high |
| Benchmarking | 30 workloads, latency, throughput, cost, recovery, harness | high |
| Service interfaces | TritRPC, event bus, async, typed RPC | high |
| Observability | OpenTelemetry, metrics, tracing | medium |
| Security | OIDC, OPA, policy, deny-by-default | medium |

---

## 4. Dependency Graph

### Direct dependencies
- TriTRPC (standard 030)
- Apache Beam, Ray (execution)
- Postgres, OpenSearch (storage)
- OpenTelemetry (observability)
- JSON-LD context specification

### Dependent systems
- `socioprophet-standards-knowledge` (upstream invariants)
- `prophet-platform` (follows storage blueprint)
- All platform services implementing these standards

### Cross-repo impact when standards-storage changes
- Standard change → every conforming service must re-evaluate compliance.
- Benchmark workload definition change → re-run benchmarks platform-wide; comparisons
  invalidated.
- TritRPC version change in standard 030 → affects all TritRPC-using services.

---

## 5. Change Impact Rules

| What changed | Downstream repos affected | DevOps actions | Governance gates |
|---|---|---|---|
| Any `docs/standards/` normative doc | ALL platform services | Standards compliance sweep | Standards ADR + version bump; broad team review |
| `benchmarks/workloads/` | Benchmark harness; historical comparisons invalidated | Re-run all 30 workload benchmarks | Benchmark ADR; results archived |
| `docs/standards/030-service-interfaces-tritrpc.md` | Every TritRPC service | Rebuild + re-validate all RPC contracts | TriTRPC upgrade ADR |
| `docs/standards/070-graph-rdf-hypergraph.md` | Graph layer implementations | Graph store re-validation | ADR for graph model change |
| `docs/standards/080-knowledge-context.md` | standards-knowledge (upstream invariants change) | standards-knowledge compliance re-check | Coordinated ADR with standards-knowledge |
| `schemas/` | Contract consumers | Schema migration | Schema registry governance |
