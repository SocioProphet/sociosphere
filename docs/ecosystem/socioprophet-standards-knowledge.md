# Repository Analysis — SocioProphet/socioprophet-standards-knowledge

**GitHub:** https://github.com/SocioProphet/socioprophet-standards-knowledge  
**Role in ecosystem:** Knowledge context standards  
**Last analysed:** 2026-04-08

---

## 1. Repository Purpose & Identity

### What it does
Defines the Knowledge Context standards layer — specifying micro-publications,
meriotopographic relations, masking/tokenization/IR/vector operations, office/editor
integration, and agent-first + human validation gates, building on storage standards as
upstream invariants.

### Core responsibilities
- `docs/standards/000-knowledge-platform-standards.md` — knowledge platform overview.
- `docs/standards/001-upstream-dependencies.md` — documents which storage standard invariants
  apply here.
- `docs/standards/020-meriotopographics.md` — meriotopographic relation standards
  (part/whole/topology relationships in knowledge structures).
- `docs/standards/030-tritrpc-binding.md` — TritRPC binding spec for knowledge context
  operations.
- `docs/standards/031-schema-context-id-registry.md` — schema/context ID registry for
  knowledge objects.
- `docs/standards/032-tritrpc-knowledge-fixtures.md` — canonical TritRPC fixtures for
  knowledge operations.
- `rpc/` — RPC definitions for knowledge services.
- `schemas/` — Avro/JSON-LD schemas for knowledge objects.
- `benchmarks/` + `fixtures/` — performance and conformance testing.

### What systems depend on it
- Implementations of knowledge context operations in the platform
  (IR/vector retrieval, editor integration, agent validation gates).
- Any service encoding knowledge context schema/context IDs.

### What it depends on
- **socioprophet-standards-storage** — explicitly upstream:
  standard 001 (`001-upstream-dependencies.md`) lists which storage invariants this repo
  inherits.
- **TriTRPC** — standard 030 defines the TritRPC binding for knowledge services; fixtures in
  standard 032 must match TriTRPC canonical vectors.

### Key files
- `README.md` — one-paragraph description; upstream pointer
- `docs/standards/001-upstream-dependencies.md` — upstream dependency declarations
- `docs/standards/020-meriotopographics.md` — meriotopographic relation model
- `docs/standards/030-tritrpc-binding.md` — TritRPC binding for knowledge APIs
- `docs/standards/031-schema-context-id-registry.md` — schema/context ID registry
- `docs/standards/032-tritrpc-knowledge-fixtures.md` — canonical knowledge fixtures
- `Makefile` — build/test entry point

---

## 2. Controlled Vocabulary & Ontology

### Key terms
| Term | Definition | Source |
|---|---|---|
| **Micro-publications** | Small, citable knowledge units — comparable to micro-formats in publishing | `README.md` |
| **Meriotopographics** | Mereological + topological relations: part/whole, containment, boundary, adjacency between knowledge structures | `docs/standards/020-meriotopographics.md` |
| **TritRPC binding** | Specification of how knowledge services expose their API over TritRPC (schema/context IDs, method signatures) | `docs/standards/030-tritrpc-binding.md` |
| **Schema/context ID registry** | Canonical registry of numeric IDs for knowledge object schemas | `docs/standards/031-schema-context-id-registry.md` |
| **Knowledge fixtures** | Canonical test vectors for knowledge context TritRPC operations | `docs/standards/032-tritrpc-knowledge-fixtures.md` |
| **Masking** | Privacy-preserving field masking for knowledge objects | `README.md` |
| **Tokenization** | Privacy-preserving tokenization of sensitive knowledge fields | `README.md` |
| **IR** | Information retrieval operations over knowledge context | `README.md` |
| **Agent-first** | AI agents as primary producers/consumers of knowledge context | `README.md` |
| **Human validation gate** | Checkpoint requiring human review before knowledge is published | `README.md` |

### Domain-specific language
- Schema/context IDs are **stable once allocated** — IDs in the registry must never be
  reused.
- Knowledge fixtures must **exactly match** TritRPC canonical vectors (standard 032 inherits
  the determinism guarantee from TriTRPC).
- Meriotopographic relations define **structural relationships** between knowledge objects —
  not just flat tags.
- The repo's scope is deliberately **narrow**: it extends storage standards; it does not
  re-define them.

### Semantic bindings to other repos
- **← socioprophet-standards-storage**: explicit upstream (standard 001 inherits invariants).
- **→ TriTRPC**: TritRPC binding (standard 030) + fixture standard (032).
- **↔ new-hope**: new-hope defines Carrier/Protocol objects that align with knowledge context
  objects defined here.

---

## 3. Topic Modeling

| Topic | Keywords | Weight |
|---|---|---|
| Knowledge representation | micro-publications, meriotopographics, part/whole, topology | dominant |
| TritRPC knowledge API | binding, schema context ID, fixtures, canonical vectors | dominant |
| Privacy / masking | tokenization, masking, PII redaction, data minimization | high |
| Retrieval / search | IR, vector, embeddings | high |
| Agent-human validation | agent-first, human validation gate | medium |
| Editor integration | office/editor, micro-publication workflow | medium |
| Standards hierarchy | upstream dependencies, invariants, conformance | medium |

---

## 4. Dependency Graph

### Direct dependencies
- `socioprophet-standards-storage` (normative upstream; standard 001)
- `TriTRPC` (binding spec + fixtures; standards 030, 032)

### Dependent systems
- Platform knowledge retrieval services
- Editor integration services
- Agent reasoning layer (consumes knowledge context)

### Cross-repo impact when standards-knowledge changes
- Storage standard upstream change → standards-knowledge must re-check inherited invariants
  (standard 001).
- TriTRPC version change → TritRPC binding (standard 030) and fixtures (standard 032) must be
  re-verified.

---

## 5. Change Impact Rules

| What changed | Downstream repos affected | DevOps actions | Governance gates |
|---|---|---|---|
| `docs/standards/020-meriotopographics.md` | Knowledge structure consumers | Rebuild + re-validate meriotopographic operations | ADR + review |
| `docs/standards/030-tritrpc-binding.md` | All TritRPC knowledge service implementations | Fixture re-verification; rebuild | TritRPC binding ADR |
| `docs/standards/031-schema-context-id-registry.md` | Any code encoding schema/context IDs | Rebuild + re-verify ID allocations | Registry governance — IDs must not be reused |
| `schemas/` | Knowledge object consumers | Schema migration | Schema registry review |
| `fixtures/` | Conformance test implementations | Re-run all conformance tests | Standards ADR |
| Upstream storage standard change | This repo must re-check inherited invariants | Compliance re-check run | Coordinated ADR with standards-storage |
