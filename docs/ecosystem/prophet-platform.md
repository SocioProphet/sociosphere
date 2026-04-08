# Repository Analysis — SocioProphet/prophet-platform

**GitHub:** https://github.com/SocioProphet/prophet-platform  
**Role in ecosystem:** Core contracts / platform infrastructure hub  
**Last analysed:** 2026-04-08

---

## 1. Repository Purpose & Identity

### What it does
The platform/infrastructure management hub — a thin monorepo containing deployable services
(API, gateway, web portal), Kubernetes deployment wiring (Kustomize + Argo CD), TritRPC
contracts, and data schemas. Described in its README as a "thin platform monorepo" that ships
code while leaving standards governance to the dedicated standards repos.

### Core responsibilities
- `apps/api` — long-lived UDS service (TritRPC-based; today: `Health.Ping → Pong` exemplar).
- `apps/gateway` — HTTP/WebSocket bridge terminating at edge, relaying over TritRPC/UDS.
- `apps/socioprophet-web` — Vue 3 + Vite UI (portal).
- `infra/` — Kustomize bases + overlays, Argo CD app-of-apps.
- `rpc/` — TritRPC contracts used by apps and tooling.
- `contracts/` — event-level data contracts (JSON schemas):
  `EmbeddingComputed.v0.1.json`, `LensOutput.v0.1.json`, `TopicAssigned.v0.1.json`.
- `schemas/` — data/format schema references.
- `mcp/` — Model Context Protocol support.
- `adr/` — Architecture Decision Records.
- `docs/TRITRPC_SPEC.md` — normative TritRPC reference pinned for this platform.
- `docs/STORAGE_INTEGRATION_BLUEPRINT.md` — how storage standards apply here.

### What systems depend on it
- End-user browser access (via gateway → TritRPC → API).
- Platform operators (via Argo CD for desired-state management).
- `socioprophet-standards-storage` references prophet-platform in its storage blueprint.

### What it depends on
- **TriTRPC** — normative wire protocol; `rpc/` contains TritRPC contracts;
  `docs/TRITRPC_SPEC.md` pins the spec.
- **socioprophet-standards-storage** — storage decisions and contracts follow the standards
  defined there.
- Kubernetes + Argo CD (deployment)
- Kustomize (infra wiring)
- Vue 3 + Vite (portal UI)

### Key files
- `README.md` — layout overview and reading order
- `docs/ARCHITECTURE.md` — wire, browser access, portal, k8s, security
- `docs/TRITRPC_SPEC.md` — TritRPC normative reference
- `docs/STORAGE_INTEGRATION_BLUEPRINT.md` — storage layer blueprint
- `rpc/` — TritRPC service contracts
- `contracts/EmbeddingComputed.v0.1.json` — embedding event schema
- `contracts/LensOutput.v0.1.json` — lens output event schema
- `contracts/TopicAssigned.v0.1.json` — topic assignment event schema
- `infra/k8s/` — Kustomize overlays
- `mcp/` — Model Context Protocol

---

## 2. Controlled Vocabulary & Ontology

### Key terms
| Term | Definition | Source |
|---|---|---|
| **TritRPC over UDS** | TritRPC framing over Unix Domain Sockets; default trust boundary inside a host/node | `docs/ARCHITECTURE.md` |
| **Gateway** | HTTP/WebSocket terminator that relays requests over TritRPC to UDS-bound services | `docs/ARCHITECTURE.md` |
| **Portal** | Vue 3 + Vite UI; "no React/Carbon; lightweight, component-first" | `docs/ARCHITECTURE.md` |
| **AEAD framing** | Cryptographic integrity for TritRPC frames (XChaCha20-Poly1305) | `docs/TRITRPC_SPEC.md` |
| **Replay guards** | Protection against replayed TritRPC frames | `docs/TRITRPC_SPEC.md` |
| **App-of-apps** | Argo CD pattern managing all platform services as sub-apps | `docs/ARCHITECTURE.md` |
| **EmbeddingComputed** | Event contract: a computed embedding vector (AI output) | `contracts/EmbeddingComputed.v0.1.json` |
| **LensOutput** | Event contract: a semantic lens analysis result | `contracts/LensOutput.v0.1.json` |
| **TopicAssigned** | Event contract: a topic classification result | `contracts/TopicAssigned.v0.1.json` |
| **MCP** | Model Context Protocol — tooling support in `mcp/` | `mcp/` |
| **ADR** | Architecture Decision Record — in `adr/` | `adr/` |

### Domain-specific language
- The **gateway is strictly scoped** — it is an HTTP bridge only; it must not contain
  business logic.
- **UDS** is the trust boundary: services speak TritRPC over Unix sockets; only the gateway
  exposes a network surface.
- Event contracts (`contracts/`) are **versioned** (`v0.1`) and schema-locked.
- Platform code and infra wiring live here; **standards** stay in the dedicated standards
  repos to avoid "a standards repo accidentally becoming a monolith".

### Semantic bindings to other repos
- **→ TriTRPC**: TritRPC is the wire format; `docs/TRITRPC_SPEC.md` pins the spec version.
- **→ socioprophet-standards-storage**: storage decisions follow the standards defined there.
- **→ socioprophet-web** (from socioprophet): deploys the web UI.
- **← browser clients + Argo CD operators**: this repo is the deployment surface.

---

## 3. Topic Modeling

| Topic | Keywords | Weight |
|---|---|---|
| TritRPC transport layer | UDS, AEAD, nonce, replay guard, canonical encoding, gateway | dominant |
| Service infrastructure | API, gateway, Kustomize, Argo CD, Kubernetes, app-of-apps | dominant |
| Data contracts / events | EmbeddingComputed, LensOutput, TopicAssigned, Avro, JSON schema | high |
| Web portal | Vue 3, Vite, gateway HTTP bridge | high |
| Security | AEAD, trust boundary, UDS isolation, replay guards | high |
| AI / embedding layer | embedding, topic assignment, lens, semantic | medium |
| MCP (Model Context Protocol) | mcp/, AI tool protocol | medium |
| Storage integration | storage blueprint, Postgres, vector, graph | medium |

---

## 4. Dependency Graph

### Direct dependencies
- TriTRPC (normative protocol — `rpc/` + `docs/TRITRPC_SPEC.md`)
- socioprophet-standards-storage (storage decisions)
- Kubernetes + Argo CD (infra deployment)
- Vue 3 + Vite (UI)
- TritRPC AEAD library (XChaCha20-Poly1305)

### Dependent systems
- Browser clients (via gateway)
- Platform operators (via Argo CD)
- `socioprophet-standards-storage` references platform's storage blueprint

### Cross-repo impact when prophet-platform changes
- `rpc/` contract change → any consumer of those RPC endpoints must update.
- `contracts/*.json` schema change → all event consumers must update.
- `infra/k8s/` change → platform deployment affected; Argo CD syncs.

---

## 5. Change Impact Rules

| What changed | Downstream repos affected | DevOps actions | Governance gates |
|---|---|---|---|
| `rpc/` TritRPC contract | All service clients using those contracts | Rebuild API + gateway + clients; fixture verification | Contract versioning; backward-compat check |
| `contracts/*.json` event schema | All event consumers (EmbeddingComputed, LensOutput, TopicAssigned) | Schema migration + consumer updates | Schema registry review |
| `infra/k8s/` Kustomize | Platform deployment | Argo CD sync; staging validation | Infra review; rollback plan |
| `apps/api` | Gateway (relay) + all clients | Full CI + redeploy | API version bump |
| `docs/TRITRPC_SPEC.md` pin update | All TritRPC-consuming services | Fixture re-verification | TriTRPC version upgrade ADR |
| `mcp/` | MCP-consuming tooling | MCP integration re-test | MCP compatibility check |
