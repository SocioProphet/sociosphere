# Repository Analysis — SocioProphet/TriTRPC

**GitHub:** https://github.com/SocioProphet/TriTRPC  
**Role in ecosystem:** RPC protocol — most cross-cutting dependency  
**Last analysed:** 2026-04-08

---

## 1. Repository Purpose & Identity

### What it does
The canonical repository for the TritRPC v1 RPC protocol — a deterministic, ternary-native
encoding scheme with AEAD authentication, canonical byte-for-byte fixture vectors, and
reference implementations in Rust and Go. Also contains an experimental vNext design pack.

### Core responsibilities
- Normative TritRPC v1 specification — `spec/README-full-spec.md`.
- Reference implementation — `reference/tritrpc_v1.py` — and fixture generation.
- Canonical hex fixture vectors — `fixtures/*.txt` + `*.nonces` — the interoperability
  contract between all language implementations.
- Rust port — `rust/tritrpc_v1` (`cargo test` verifies AEAD tags + fixture parity).
- Go port — `go/tritrpcv1` (`go test` performs the same validations).
- CLI tools for packing/verifying frames (`trpc` binary in both Rust and Go).
- Pre-commit hook preventing commits that drift fixture AEAD tags.
- vNext design pack — `docs/vnext/`, `reference/experimental/`.

### What systems depend on it
- **prophet-platform** — `rpc/` TritRPC contracts; `docs/TRITRPC_SPEC.md` pins the spec.
- **socioprophet-standards-storage** — standard 030 mandates TritRPC for service interfaces.
- **socioprophet-standards-knowledge** — standards 030 + 032 bind knowledge services to
  TritRPC.
- **new-hope** — `docs/Carrier_Wire_Format_TritRPC.md` maps New Hope Carrier onto TritRPC
  envelope framing.
- **sociosphere** — pins TritRPC as `third_party` dependency.
- **agentplane** — bundles reference TritRPC-based protocols.

### What it depends on
- Rust + Cargo
- Go
- Python 3 + `cryptography` library (reference implementation + fixture regeneration)
- Avro Binary Encoding (for Path-A payloads)
- XChaCha20-Poly1305 (`cryptography` package) for AEAD

### Key files
- `README.md` — full protocol overview, build/test instructions, fixture usage
- `docs/THEORY.md` — complete conceptual model (trits, TritPack243, TLEB3, envelope, AEAD)
- `spec/README-full-spec.md` — normative requirements
- `reference/tritrpc_v1.py` — Python reference implementation
- `fixtures/*.txt` + `*.nonces` — canonical fixture vectors
- `rust/tritrpc_v1/` — Rust port
- `go/tritrpcv1/` — Go port
- `docs/integration_readiness_checklist.md` — integration readiness
- `docs/audit_tritrpc_v1_parity.md` — cross-language parity audit
- `docs/trit-to-trust.md` — trust model doc
- `docs/vnext/` — vNext design pack

---

## 2. Controlled Vocabulary & Ontology

### Key terms
| Term | Definition | Source |
|---|---|---|
| **Trit** | Ternary digit with values 0, 1, or 2 | `docs/THEORY.md` §1 |
| **TritPack243** | Packs 5 trits per byte (3^5=243); tail marker for non-multiples of 5 | `docs/THEORY.md` §2 |
| **TLEB3** | Ternary Length Encoding Base-3: integers as base-9 digits expressed as tritlets, then TritPack243-packed | `docs/THEORY.md` §3 |
| **Tritlet** | 3-trit group: continuation trit + 2 payload trits | `docs/THEORY.md` §3 |
| **Path-A** | Avro Binary Encoding payload lane — main interop path | `docs/THEORY.md` §5 |
| **Path-B** | Ternary-native payload lane (toy subset fixtures) | `docs/THEORY.md` §5 |
| **Envelope** | Frame structure: SERVICE + METHOD + AUX + payload + AEAD lane | `docs/THEORY.md` §4 |
| **SERVICE / METHOD** | Routing metadata in envelope header | `docs/THEORY.md` §4 |
| **AUX** | Optional envelope region: Trace, Sig, Proof-of-Execution (PoE) | `docs/THEORY.md` §8 |
| **AEAD lane** | XChaCha20-Poly1305 authenticated encryption with 24-byte nonce | `docs/THEORY.md` §6 |
| **AAD** | Associated Authenticated Data — envelope bytes before the final tag field | `docs/THEORY.md` §6 |
| **Canonical encoding** | Deterministic byte sequence for the same semantic input | `docs/THEORY.md` §10 |
| **Fixture vectors** | Canonical hex lines in `fixtures/*.txt` — the interoperability contract | `README.md` |
| **Nonce file** | `*.nonces` paired with each fixture file for AEAD tag recomputation | `README.md` |
| **Repack check** | Verifying re-encoded envelopes produce identical fixture bytes | `README.md` |
| **vNext** | Experimental next-generation design: braided semantic cadence, compact framing | `docs/vnext/README.md` |
| **Hypergraph service** | Reference service model with AddVertex/AddEdge RPCs | `docs/THEORY.md` §9 |
| **Proof-of-Execution (PoE)** | AUX structure type for deterministic replay checkpoints | `docs/THEORY.md` §8 |

### Domain-specific language
- **Fixtures are the contract** — not documentation; not tests. Fixture vectors are the
  canonical interoperability surface. Any drift is a breaking change.
- **Determinism is non-negotiable**: every language implementation must produce identical
  bytes for the same semantic input.
- **Path-A is normative**, Path-B is a toy subset. vNext is experimental and not yet
  normative for any port.
- The pre-commit hook is a **hard gate**: it refuses commits with drifted AEAD tags.

### Semantic bindings to other repos
- **← All TritRPC consumers** (prophet-platform, standards-storage, standards-knowledge,
  new-hope, agentplane): this repo's fixtures are the interoperability contract for all of
  them.
- **→ sociosphere**: pinned as third_party dependency; integration tracked there.

---

## 3. Topic Modeling

| Topic | Keywords | Weight |
|---|---|---|
| Ternary encoding theory | trits, TritPack243, TLEB3, base-3, base-9, tail marker | dominant |
| Deterministic reproducibility | canonical encoding, fixture vectors, cross-language parity, repack | dominant |
| Envelope / framing protocol | envelope, SERVICE, METHOD, AUX, payload, AEAD lane | dominant |
| Cryptographic integrity | XChaCha20-Poly1305, AEAD, nonce, AAD | dominant |
| Multi-language implementation | Rust, Go, Python reference, parity audit | high |
| Hypergraph service model | AddVertex, AddEdge, Avro encoding, RPC | medium |
| vNext experimental design | braided semantics, compact control words, hot-path framing | medium |
| Developer tooling | CLI trpc, pre-commit hook, fixture regeneration | medium |

---

## 4. Dependency Graph

### Direct dependencies
- Rust + Cargo
- Go
- Python 3 + `cryptography` library
- Avro Binary Encoding (Path-A payloads)

### Dependent systems
- `prophet-platform` (`rpc/` contracts, `TRITRPC_SPEC.md`)
- `socioprophet-standards-storage` (standard 030)
- `socioprophet-standards-knowledge` (standards 030, 032)
- `new-hope` (`Carrier_Wire_Format_TritRPC.md`)
- `sociosphere` (`third_party/` pin + `INTEGRATION_STATUS.md`)
- Any agentplane runner backend using TritRPC transport

### Cross-repo impact when TriTRPC changes
- Fixture vector change → ALL consumers must re-verify their implementations.
- Spec change → all conforming implementations (Go, Rust, Python) must update.
- AEAD suite change → catastrophic: every authenticated frame across all repos must be
  re-verified.

---

## 5. Change Impact Rules

| What changed | Downstream repos affected | DevOps actions | Governance gates |
|---|---|---|---|
| `fixtures/*.txt` or `*.nonces` | ALL TritRPC implementations and consumers | Re-run `cargo test`, `go test`, fixture verification for every consumer | Fixture version bump; broadcast to all consumers simultaneously |
| `spec/README-full-spec.md` | All conforming implementations | Rebuild + re-test all ports | Spec version bump; ADR; tagged release |
| AEAD suite change | EVERY authenticated TritRPC deployment | Full re-key + rebuild + re-test across all repos | Security ADR; coordinated migration plan |
| `rust/` port change | CI fixture parity checks | `cargo test` + fixture verify | Port parity review; must match Python reference |
| `go/` port change | CI fixture parity checks | `go test` + fixture verify | Port parity review; must match Python reference |
| `reference/tritrpc_v1.py` change | Fixture regeneration could invalidate existing fixtures | Pre-commit hook + fixture regen verification | Reference impl ADR |
| vNext promotion to normative | All repos using v1 | Major migration; new fixture set | Major version ADR; all downstream must opt in |
