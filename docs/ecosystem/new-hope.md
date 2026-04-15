# Repository Analysis — SocioProphet/new-hope

**GitHub:** https://github.com/SocioProphet/new-hope  
**Role in ecosystem:** Semantic runtime (Higher-Order Semantic Runtime for agentic commons)  
**Last analysed:** 2026-04-08

---

## 1. Repository Purpose & Identity

### What it does
A Higher-Order Semantic Runtime for agentic commons (news + messaging). Defines a normative
object model — Protocol, Signal, Carrier, Receptor, Membrane, Receptor System — and uses
TritRPC as its canonical carrier wire format. Reconstructed and extended from the earlier
HOPE (Higher-Order Propagation Engine) runtime.

### Core responsibilities
- Define first-class objects: Message, Thread, Claim, Citation, Entity, Lens,
  ModerationEvent — `docs/Protocol_Pack_v0.md`.
- Specify v0.2 normative core: Protocol, Signal, Carrier, Receptor, Membrane, Receptor
  System — `docs/New_Hope_Spec_v0.2.md`.
- Map New Hope Carrier → TritRPC envelope framing —
  `docs/Carrier_Wire_Format_TritRPC.md`.
- Conformance tests: replay, provenance, membrane, ranking —
  `docs/Conformance_Tests.md`.
- Document lineage from HOPE → New Hope —
  `docs/HOPE_Evaluation.md`, `docs/Mapping_HOPE_to_NewHope.md`.
- Roadmap: canonicalization RFC, membrane decision model, test harness —
  `docs/Roadmap.md`.

### What systems depend on it
- Any agentic commons / news & messaging runtime that implements the New Hope spec.
- Platforms building moderation, citation tracking, or structured news feeds on this
  semantic layer.

### What it depends on
- **TriTRPC** — canonical wire format; `docs/Carrier_Wire_Format_TritRPC.md` maps New Hope
  Carrier onto TritRPC envelope (SERVICE, METHOD, AUX, payload, AEAD).
- **BLAKE3** (content addressing for hashing/signing carriers).
- **ed25519** (signature algorithm for provenance).
- **DID** (Decentralized Identifiers: `did:key:...`) for emitter identity.
- **OPA/Rego** (policy evaluation engine for Membrane decisions).

### Key files
- `README.md` — overview, doc index, status
- `docs/New_Hope_Spec_v0.2.md` — normative v0.2 spec (carrier wire format, core objects)
- `docs/Protocol_Pack_v0.md` — first-class objects: Message/Thread/Claim/Citation/Entity/
  Lens/ModerationEvent
- `docs/Carrier_Wire_Format_TritRPC.md` — mapping of Carrier onto TritRPC envelope
- `docs/Carrier_Wire_Format.md` — canonical Carrier wire format (JSON)
- `docs/Conformance_Tests.md` — replay/provenance/membrane/ranking tests
- `docs/HOPE_Evaluation.md` — what HOPE got right and what breaks in 2025+
- `docs/Mapping_HOPE_to_NewHope.md` — lineage mapping and deltas
- `docs/Roadmap.md` — canonicalization RFC, membrane decision model, harness
- `docs/spec/` — extended specification documents

---

## 2. Controlled Vocabulary & Ontology

### Key terms
| Term | Definition | Source |
|---|---|---|
| **Protocol** | Versioned schema: payload structure + semantic meaning + validation rules; MUST be content-addressed (hash of canonical form) | `docs/New_Hope_Spec_v0.2.md` §2.1 |
| **Signal** | An event occurrence with causality (`parents[]`, `thread_root`, `derived_from[]`); append-only | `docs/New_Hope_Spec_v0.2.md` §2.1 |
| **Carrier** | Typed message envelope: `protocol_ref` + `signal` + `payload` + `provenance` + `policy_context` | `docs/New_Hope_Spec_v0.2.md` §2.1 |
| **Receptor** | Behavior/agent module: consumes + emits Carriers; declares protocols, capabilities, determinism class, sandbox profile | `docs/New_Hope_Spec_v0.2.md` §2.1 |
| **Membrane** | Policy enforcement point between receptors: authn/authz, quotas, redaction, signing, egress controls | `docs/New_Hope_Spec_v0.2.md` §2.1 |
| **Receptor System** | Graph of receptors connected by membranes; MUST produce trace graph per hop + support replay | `docs/New_Hope_Spec_v0.2.md` §2.1 |
| **carrier_version** | Versioning field in the Carrier wire format | `docs/New_Hope_Spec_v0.2.md` §2.2 |
| **protocol_ref** | Content hash of the Protocol schema: `hash://blake3/<protocol-hash>` | `docs/New_Hope_Spec_v0.2.md` §2.2 |
| **provenance** | Emitter identity (DID), ed25519 signatures, input/transform lineage | `docs/New_Hope_Spec_v0.2.md` §2.2 |
| **policy_context** | Tenant/community/ruleset refs + labels (e.g. `public`, `needs_review`, `contains_pii:false`) | `docs/New_Hope_Spec_v0.2.md` §2.2 |
| **Determinism class** | `deterministic \| bounded_nondeterministic \| nondeterministic` — declared per Receptor | `docs/New_Hope_Spec_v0.2.md` §2.1 |
| **Membrane decision** | allow / deny / quarantine / redact / downgrade / rate-limit / block-egress | `docs/New_Hope_Spec_v0.2.md` §2.3 |
| **Trace graph** | Per-hop audit graph produced by Receptor System for every carrier | `docs/New_Hope_Spec_v0.2.md` §2.1 |
| **Replay** | Deterministic re-execution from a checkpoint | `docs/New_Hope_Spec_v0.2.md` §2.1 |
| **HOPE** | Predecessor runtime (Higher-Order Propagation Engine) | `docs/HOPE_Evaluation.md` |
| **ModerationEvent** | First-class object in the Protocol Pack | `docs/Protocol_Pack_v0.md` |
| **Lens** | Semantic view/transformation applied to content | `docs/Protocol_Pack_v0.md` |
| **did:key** | DID method for emitter identity based on public key | `docs/New_Hope_Spec_v0.2.md` §2.2 |

### Domain-specific language
- Hashing/signing MUST be performed over the **canonical bytes** of the full TritRPC frame.
- A Carrier is only valid if **all four** required fields are present: `protocol_ref`,
  `signal`, `payload`, `provenance` + `policy_context` (for publishable carriers).
- Membranes decide **per carrier, per hop** — there is no global allow/deny list.
- Receptor determinism class is a **declared contract**, not inferred at runtime.
- "Commons-grade" means the runtime must handle **multi-tenant, federated** scenarios with
  strict egress controls.

### Semantic bindings to other repos
- **→ TriTRPC**: canonical wire format; Carrier fields map directly onto TritRPC envelope
  regions.
- **↔ socioprophet-standards-knowledge**: Carrier/Protocol objects align with
  micro-publication and meriotopographic knowledge objects.
- **↔ socioprophet-standards-storage**: storage contexts (incident state, event stream) align
  with Signal/Carrier persistence requirements.
- **↔ agentplane**: Receptor System trace graph and replay model mirrors agentplane's
  evidence artifact model.

---

## 3. Topic Modeling

| Topic | Keywords | Weight |
|---|---|---|
| Semantic runtime objects | Protocol, Signal, Carrier, Receptor, Membrane, Receptor System | dominant |
| Content addressing / provenance | BLAKE3 hash, content-addressed, provenance, DID, ed25519 | dominant |
| Policy enforcement | Membrane, OPA/Rego, allow/deny/redact, quotas, egress control | dominant |
| TritRPC carrier mapping | envelope, SERVICE/METHOD, AUX, AEAD, canonical bytes | high |
| News / messaging domain | Message, Thread, Claim, Citation, Entity, ModerationEvent | high |
| Replay / audit trail | trace graph, replay, deterministic, checkpoint | high |
| Determinism classes | deterministic, bounded_nondeterministic, nondeterministic | medium |
| Federation | cross-system relay, controlled federation, multi-tenant | medium |

---

## 4. Dependency Graph

### Direct dependencies
- TriTRPC (canonical wire format)
- BLAKE3 (content hashing)
- ed25519 (signing)
- DIDs (identity)
- OPA/Rego (policy engine for Membrane)

### Dependent systems
- News/messaging commons implementations
- Moderation platforms using Membrane policy model
- Any service implementing Receptor/Carrier protocol

### Cross-repo impact when new-hope changes
- Carrier wire format change → every system serializing/deserializing Carriers must update;
  canonical byte signatures invalidated.
- Protocol Pack object change → first-class object consumers must migrate.
- Upstream TriTRPC spec change → Carrier wire mapping must be re-verified.

---

## 5. Change Impact Rules

| What changed | Downstream repos affected | DevOps actions | Governance gates |
|---|---|---|---|
| `docs/New_Hope_Spec_v0.2.md` core object model | ALL New Hope implementations | Full conformance test re-run | Spec version bump; ADR; backward-compat assessment |
| Carrier wire format | Every system serializing/deserializing Carriers | Re-verify all fixtures; AEAD re-tag | Coordinated release with TriTRPC; canonical hash update |
| TritRPC upstream change | Carrier wire mapping may drift | Re-map + re-verify canonical bytes | Upstream TriTRPC ADR must be acted on in this repo |
| Membrane policy interface | All Membrane implementations | Policy regression tests | Security review; OPA rule versioning |
| Protocol Pack object (`docs/Protocol_Pack_v0.md`) | First-class object consumers | Schema migration | Protocol versioning ADR |
| `docs/Conformance_Tests.md` | Conformance test implementations | Re-run all conformance tests | Standards ADR |
