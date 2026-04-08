# mdheller Contribution Survey — Oct 5 2025 → Apr 5 2026

**Purpose:** Foundational research for the controlled glossary and ontology spec.
Covers all repositories across SocioProphet, SociOS-Linux, and SourceOS-Linux where
user **mdheller** has contributed (commits, PRs, issues) in the past six months.

**Methodology:** GitHub API search for PRs (`author:mdheller org:<org> created:>2025-10-05`),
issues, and commit history per repo. Executed 2026-04-05.

**Activity totals:**
- 123 PRs across 15 SocioProphet repos
- 8 PRs across 4 SociOS-Linux repos
- 2 PRs across 2 SourceOS-Linux repos
- 73 issues across 11 SocioProphet repos

---

## Organization: SocioProphet

### 1. SocioProphet/sociosphere

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/sociosphere> |
| Language | Python, TOML, JSON |
| Topics | `layer-prophet-platform` · `layer-protocol` · `role-governance-controller` |
| Activity | 5 PRs merged; most recent commit `3e764a9` (2026-04-04) |

**Purpose & role:** The canonical *workspace controller*. Holds the multi-repo manifest
(`manifest/workspace.toml`), lock (`manifest/workspace.lock.json`), a Python runner
(`tools/runner/runner.py`) for deterministic fetch/build/test, and the shared
`protocol/` fixtures that define adapter compatibility.

**Key interfaces & contracts:**
- **Manifest schema** (`manifest/workspace.toml`): `name`, `url`, `ref/rev`,
  `role` (component | adapter | third_party | docs), `local_path`, `entry`,
  `required_capabilities`.
  Named entries: `prophet_cli` (Go component), `sourceos_a2a_mcp_bootstrap`,
  `socioprophet-web`, `human_digital_twin`, `ontogenesis`,
  `cc` (adapter: `container_exec`, `fs_ops`, `deps_inventory`),
  `configs` (adapter: `policy`, `defaults`).
- **Runner CLI:** `python3 tools/runner/runner.py list|fetch|run build --all`
- **Protocol fixtures** in `protocol/`: shared adapter compatibility vectors.
- Outputs: build artifacts, test results, lock-file updates, inventory reports.

**Sociosphere integration status:** This IS sociosphere — the authoritative coordinator.

---

### 2. SocioProphet/TriTRPC

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/TriTRPC> |
| Language | Python (reference), Rust, Go |
| Topics | `ternary` · `rpc` · `protocol` · `deterministic-encoding` · `fixtures` · `rust` · `go` · `avro` · `aead` · `agentic-transport` · `braided-semantics` |
| Activity | 8 PRs merged; 1 open issue |

**Purpose & role:** The **canonical wire protocol** for the entire ecosystem. TritRPC v1
provides deterministic, ternary-native RPC framing with authenticated envelopes.
All service contracts across SocioProphet repos reference it as their wire format.
v1 is stable; vNext adds braided semantic cadence and compact control words.

**Key interfaces & contracts:**
- **Envelope framing:** `SERVICE + METHOD` routing header, AUX structures, payload
  (Avro Path-A or ternary Path-B), AEAD lane (XChaCha20-Poly1305, 24-byte nonce).
- **Encoding:** TritPack243 (5 trits/byte), TLEB3 length encoding.
- **Fixture contract:** `fixtures/*.txt` + `*.nonces` — Rust and Go must reproduce
  identical bytes to the Python reference.
- **CLI:** `cargo run -p tritrpc_v1 --bin trpc -- pack` (Rust);
  `./trpc verify --fixtures …` (Go).
- Inputs: service name, method name, JSON payload, 32-byte key, 24-byte nonce hex.
- Outputs: authenticated binary frame; fixture verification status.
- Deps: `cryptography` (Python), XChaCha20-Poly1305, Avro.

**Sociosphere integration status:** Pinned as submodule in `third_party/`.
Referenced by: `socioprophet-standards-storage`, `human-digital-twin`,
`prophet-platform/rpc/`, `slash-topics`, `sourceos-a2a-mcp-bootstrap`.

---

### 3. SocioProphet/socioprophet (org monorepo)

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/socioprophet> |
| Language | HTML/JS (Firebase), TypeScript, Nix |
| Activity | 13 PRs merged (highest single-repo count); 2 issues |

**Purpose & role:** The org-level monorepo that unifies **AgentOS** (layered agent stack:
interfaces, policies, tool registry, Linux integration runbook) and the **Agentplane
control plane** (fleet-shaped: bundles → validate → place → run → evidence → replay).

**Key interfaces & contracts:**
- **Tool registry:** `registry/agentos-tool-registry.yaml` — compliance + inventory
  source of truth; validated by
  `python3 scripts/validate_registry.py registry/agentos-tool-registry.yaml config/base_image_tools.yaml`.
- **Bundle validator:** `python3 agentplane/scripts/validate_bundle.py agentplane/bundles/example-agent/bundle.json`.
- **Firebase deployment:** `.firebaserc` (multi-project), `firebase.json`.
- Layout: `agentos/`, `agentplane/`, `registry/`, `inventory/`, `workspaces/`,
  `scripts/`, `functions/`, `ops/`, `docs/`.

**Sociosphere integration status:** Directly referenced as the runtime + governance
surface. Cross-referenced with standalone `agentplane` repo.

---

### 4. SocioProphet/agentplane (standalone)

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/agentplane> |
| Language | Shell, Nix, JSON Schema |
| Activity | 5 PRs + 5 direct commits in period; most recent 2026-04-05 |

**Purpose & role:** The **fleet-shaped execution control plane**. The unit of deployment
is a "bundle" (VM modules, rendered config, policy intent, smoke tests, metadata).
Runners execute bundles (qemu-local today; microvm/fleet later). Provides the full
evidence trail via typed artifact schemas.

**Key interfaces & contracts (all in `schemas/`):**
- `bundle.schema.v0.1.json` — defines bundle fields.
- `run-artifact.schema.v0.1.json` — execution evidence after each run.
- `replay-artifact.schema.v0.1.json` — deterministic re-execution record.
- `session-artifact.schema.v0.1.json` — agent-plane runtime receipt (added PR #7, 2026-04-05).
- `promotion-artifact.schema.v0.1.json` — review and promotion flow.
- `reversal-artifact.schema.v0.1.json` — rollback flow.
- `bundle.schema.patch.json` — agent-plane runtime field patch.
- **Control matrix import lane:** `policy/imports/control-matrix/` (PR #10, commit `823f5da`).
- **GAKW hybrid warm trace** example in `examples/` (PR #9, commit `87260e4`).

**Sociosphere integration status:** "sociosphere bridge" explicitly noted in commit
for PR #6 (`da11905`). Schema family aligned with `sourceos-spec`.

---

### 5. SocioProphet/socioprophet-standards-storage

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/socioprophet-standards-storage> |
| Language | Python, YAML, JSON, JSON-LD, Avro, Parquet/Arrow, RDF/SPARQL |
| Topics | `avro` · `arrow` · `parquet` · `json-ld` · `rdf` · `sparql` · `tritrpc` · `opensearch` · `postgres` · `vector-search` · `graph-database` · `observability` · `governance` |
| Activity | 6 PRs merged |

**Purpose & role:** **Storage + data-contract standards** for the SocioProphet platform.
Defines normative standards (MUST/SHOULD/MAY) for 7 storage contexts (event stream,
incident state, artifacts, search, vectors, graphs, metrics), data contracts, service
interfaces, and a 30-workload benchmark methodology.

**Key interfaces & contracts:**
- **Data contracts:** Avro schemas for event streams; Arrow/Parquet for analytics;
  JSON-LD for provenance overlays.
- **RPC surface:** TritRPC (`rpc/`) — typed service contracts.
- **Benchmark harness:** 30 workloads (latency/throughput/cost/recovery), YAML drivers
  in `benchmarks/workloads/`.
- **Graph layer:** RDF/SPARQL + property graph + AtomSpace-style hypergraph.
- Storage portfolio: Postgres (SOR), OpenSearch (text), optional vector/graph.

**Sociosphere integration status:** Cross-references TriTRPC, `prophet-platform`, and
`sociosphere` workspace governance.

---

### 6. SocioProphet/human-digital-twin

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/human-digital-twin> |
| Language | Python, OPA/Rego, JSON Schema, YAML |
| Topics | `human-digital-twin` · `omega-protocol` · `zero-trust` · `privacy` · `consent` · `provenance` · `tritrpc` · `opa` · `rego` · `fhir` · `digital-identity` |
| Activity | 2 PRs merged |

**Purpose & role:** The **Ω (Omega) Protocol Kit** — defines a minimal, reproducible
"human API" surface for evaluating, promoting, and exporting human-centric artifacts
(observations, consented exports, capability proofs) under zero-trust constraints.
Core: 7-state promotion lattice:
`ABSENT → SEEDED → NORMALIZED → LINKED → TRUSTED → ACTIONABLE → DELIVERED`.

**Key interfaces & contracts:**
- **Service contract:** `human_digital_twin/api/trpc/devine.trpc.yaml` — TritRPC surface.
- **Ω engine:** `human_digital_twin/api/services/eval/omega.py` — 3 membership scores:
  `m_cbd` (coherence/boundedness/de-dup), `m_cgt` (consent/governance/trust),
  `m_nhy` (delivery/usefulness). All in [0,1].
- **Schema:** `human_digital_twin/api/schemas/kfs-eval.json` — Ω-evaluable extension.
- **Policies:** `human_digital_twin/api/policies/opa/*.rego` — OPA/Rego export + repair.
- **CapD:** `capd/*.json` — capability descriptor.
- UDS shim runtime: `/tmp/devine_intel.sock`, JSON RPC over Unix socket.
- Inputs: `{rpc, prev, kfs: {m_cbd, m_cgt, m_nhy}}`.
- Outputs: promotion decision, repair plan, evidence export.

**Sociosphere integration status:** Pinned in `manifest/workspace.toml` as component
`human_digital_twin`. TritRPC wire format is the declared next integration step.

---

### 7. SocioProphet/gaia-world-model

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/gaia-world-model> |
| Language | Turtle/RDF (primary), Python |
| Topics | `ontology` · `semantic-web` · `digital-twin` · `earth-science` · `geospatial` · `knowledge-commons` · `provenance` · `reproducibility` · `tritrpc` |
| Activity | 5 issues filed; last commit 2026-04-04 |

**Purpose & role:** A **modular Earth digital twin ontology + action framework**.
Provenance-tracked integration spine for Earth-relevant ontologies, datasets, and tooling.
Implements observe → audit → plan → actuate semantics.

**Key interfaces & contracts:**
- **Curation Vault:** `gaia/cv/origins.csv` (upstream URLs + commit SHAs);
  `manifests/*.njson` (license evidence + Merkle roots);
  `checklist.csv` (file-level hashes). Large artifacts in Git LFS.
- **Ontology entrypoints:** `gaia/ontology/canonical/` — SHACL validation, graph closure.
- **Actions:** observe/audit/plan/actuate with explicit semantics and guardrails.
- Inputs: upstream ontology sources (pinned SHA), dataset manifests.
- Outputs: provenance-tracked knowledge graph, validation reports, release tags.

**Sociosphere integration status:** Ecosystem integration documented in
`docs/COMMONS_AND_STACK.md`. Listed in TriTRPC topics as downstream consumer.

---

### 8. SocioProphet/hyperswarm-agent-composable-cluster-scaleup

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/hyperswarm-agent-composable-cluster-scaleup> |
| Language | Python |
| Topics | `hyperswarm` · `kubernetes` · `k8s` · `kubespray` · `krew` · `reproducibility` · `supply-chain` · `governance` · `sociosphere` · `tritrpc` |
| Activity | 3 PRs merged |

**Purpose & role:** A **reproducible, policy-forward wrapper** that pins upstream cluster
scale-up primitives (kubespray, krew) for SocioProphet's cluster expansion workflows.
Does not vendor upstream code; pins versions and fetches into `third_party/`.

**Key interfaces & contracts:**
- `make fetch` — fetches pinned upstreams (kubespray, krew).
- `make validate` — validates repo gate conditions.
- Truth hierarchy declared in `README.md`: `prophet-platform` → `sociosphere` →
  `TriTRPC` → `socioprophet-standards-storage`.
- Inputs: version pins in manifest; upstream archives.
- Outputs: validated fetch artifacts in `third_party/`.

**Sociosphere integration status:** Declared integration with all 4 canonical
SocioProphet repos.

---

### 9. SocioProphet/prophet-platform

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/prophet-platform> |
| Language | Go (primary), Kustomize, Argo CD, JSON Schema |
| Activity | Last commit 2026-04-05 |

**Purpose & role:** The **platform/infrastructure management hub** — thin platform
monorepo for shipping platform code and infra wiring. Standards live in dedicated repos;
this repo deploys and operates.

**Key interfaces & contracts:**
- **TritRPC contracts:** `rpc/` — wire contracts used by apps and tooling.
- **Validation gate:** `make validate`.
- **Infra wiring:** Argo CD application sets in `infra/k8s/`.
- **MCP surface:** `mcp/` directory.
- **Schemas:** `schemas/`, `contracts/`.
- Layout: `apps/`, `infra/`, `docs/`, `rpc/`, `schemas/`, `tools/`, `contracts/`, `adr/`, `mcp/`.

---

### 10. SocioProphet/slash-topics

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/slash-topics> |
| Language | Python, JSON Schema |
| Activity | 1 PR merged; 11 issues |

**Purpose & role:** Governed, signed, replayable "scopes" for search and knowledge
surfaces — 2025-grade commons infrastructure inspired by Blekko-era `/topic` scoping.
Topic packs are signed artifacts; policy membranes are enforceable gates; deterministic
receipts enable audit/replay; TritRPC-aligned.

**Key interfaces & contracts:**
- **Topic pack schema:** `specs/*.json` — normative JSON Schema for topic definitions.
- **Policy membranes:** `policies/` — governance bundles.
- **TritRPC alignment** for cross-language deterministic receipts.
- Inputs: topic scope definitions, signed packs.
- Outputs: validated packs, receipts, policy decisions.

---

### 11. SocioProphet/Heller-Winters-Theorem

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/Heller-Winters-Theorem> |
| Language | Python |
| Activity | 21 issues (highest issue count of any single repo in period) |

**Purpose & role:** Canonical repository for the Heller–Winters Theorem — formal
writeups and notes. The 21 issues are the primary contribution vehicle, tracking research
tasks, proofs, or formal specification work.

**Sociosphere integration status:** Research/theory layer; relationship to implementation
stack not yet documented in public files.

---

### 12. SocioProphet/ontogenesis

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/ontogenesis> |
| Language | Python, OWL/Turtle, SKOS, SHACL, SPARQL, JSON-LD |
| Activity | 1 PR merged |

**Purpose & role:** The **Human Digital Twin Ontology** (v0.3.0).
Base IRI: `https://socioprophet.dev/ont/ontogenesis#`.
Provides the formal semantic layer (OWL, SKOS, SHACL) for the HDT protocol kit.

**Key interfaces & contracts:**
- **Core ontology:** `ontogenesis.ttl` — OWL classes and properties.
- **SHACL shapes:** `shapes/*.ttl` — validation constraints on HDT instances.
- **SPARQL tests:** `tests/*.rq` — invariant checks (should return 0 rows).
- **Interop mappings:** PROV, FHIR, IEML in `mappings/*.ttl`.
- **CapD:** `capd/*.json` — capability descriptor.
- Validation: `make validate`.

**Sociosphere integration status:** Pinned in `manifest/workspace.toml` as component
`ontogenesis`. Companion to `human-digital-twin`.

---

### 13. SocioProphet/mcp-a2a-zero-trust

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/mcp-a2a-zero-trust> |
| Language | Python, JSON Schema, YAML |
| Topics | `layer-agentos-socios` · `layer-protocol` · `role-bridge` |

**Purpose & role:** A **zero-trust MCP/A2A (Model Context Protocol / Agent-to-Agent)
protocol adapter** providing authenticated inter-agent communication with a ledger-backed
audit trail. Role: `bridge` between agentos and the protocol layer.

**Key interfaces & contracts:**
- MCP server definitions in `mcp/`.
- Zero-trust authentication for A2A agent communication.
- `ledger/` — audit trail for inter-agent calls.
- `schemas/` — typed JSON Schema contracts for messages.

---

### 14. SocioProphet/sourceos-a2a-mcp-bootstrap

| Field | Value |
|---|---|
| URL | <https://github.com/SocioProphet/sourceos-a2a-mcp-bootstrap> |
| Language | Python, YAML |
| Topics | `layer-agentos-socios` · `layer-prophet-platform` · `layer-protocol` · `role-bridge` |

**Purpose & role:** A **v2.2 bootstrap bridge** connecting SourceOS A2A agent carriers
to MCP via TritRPC Unix Domain Socket connections.

**Key interfaces & contracts:**
- `.mcp/servers.json` → UDS TritRPC socket specs (carrier endpoint definitions).
- `make a2a-dry` — local carriers/status via Prophet (dry run).
- `make a2a-live` — opens PR live (requires `GITHUB_TOKEN` + Vault secrets).
- `make ci-local` — carrier verify locally.
- Inputs: Vault secrets, `GITHUB_TOKEN`, carrier specs.
- Outputs: A2A PR, carrier verification reports.

**Sociosphere integration status:** Pinned in `manifest/workspace.toml` as component
`sourceos_a2a_mcp_bootstrap`. Role-bridge between SourceOS (SociOS-Linux) and the
SocioProphet agent stack.

---

### 15. Other SocioProphet repos (1 PR each)

| Repo | Language | Note |
|---|---|---|
| cairnpath-mesh | Python | Mesh-layer for cairnpath routing (created 2026-03-25) |
| semantic-serdes | Python | Semantic serialization/deserialization utilities (created 2026-03-25) |
| identity-is-prime-reference | Python | Reference impl for "identity is prime" (created 2026-03-26) |
| lampstand | Python | SourceOS-layer utility (`layer-sourceos` topic) |
| global-devsecops-intelligence | — | DevSecOps intelligence tooling |
| new-hope | — | Topics: `layer-divine-intelligence`, `layer-prophet-platform` |

---

## Organization: SociOS-Linux

### 16. SociOS-Linux/socios

| Field | Value |
|---|---|
| URL | <https://github.com/SociOS-Linux/socios> |
| Language | Markdown (no primary code language) |
| Topics | `author-mdheller` · `governance-core` · `layer-sourceos` · `para-area` |
| Activity | 5 PRs merged (most active SociOS-Linux repo) |

**Purpose & role:** The **opt-in community automation commons** for SourceOS — CI/CD
automation, update pipelines, policy-checked build pipelines, catalogs/registries with
digest pins and attestations, optional AI automation. Critical constraint:
*"SourceOS must operate without socios. Enrollment is always explicit and gated
(Proof-of-Life + signed intent)."*

**Key interfaces & contracts:**
- Enrollment gate: Proof-of-Life + signed intent (`docs/OPT_IN.md`).
- Policy-checked build pipelines.
- Catalog/registry with digest pins and attestations.
- Inputs: signed enrollment intent, source packages.
- Outputs: CI/CD automation results, build attestations, catalogs.

**Sociosphere integration status:** Acts as the opt-in automation bridge between the
SourceOS base and the SocioProphet/AgentOS agent layer.

---

### 17. SociOS-Linux/workstation-contracts

| Field | Value |
|---|---|
| URL | <https://github.com/SociOS-Linux/workstation-contracts> |
| Language | Python, JSON Schema, Makefile |
| Topics | `ci` · `contracts` · `devtools` · `governance-core` · `json-schema` · `layer-agentos-socios` · `layer-protocol` · `layer-sourceos` · `linux` · `reproducible-builds` · `supply-chain` |
| Activity | 1 PR merged |

**Purpose & role:** The **contract + conformance layer** for workstation/CI lanes.
Defines the stable interface between contract authors, the runner/orchestrator
(execution plane), policy enforcement (allow/deny), and the artifact supply chain.
Truth lane: linux-amd64-container with pinned digest.

**Key interfaces & contracts:**
- **Contract schema** (`schemas/`): JSON Schema for workstation/CI lane contracts.
- **Validator:** `python3 tools/validate_contract.py` or `make validate`.
- **Downstream flow:** Load contract JSON → validate → if policy allows → execute lanes →
  emit evidence (digest, deps inventory, OS fingerprint, logs).
- Deps: Python `jsonschema`.

**Sociosphere integration status:** Topics show alignment with `layer-agentos-socios`
and `layer-protocol` — the SociOS-Linux-side contract surface feeding the AgentOS
execution plane.

---

### 18. SociOS-Linux/imagelab

| Field | Value |
|---|---|
| URL | <https://github.com/SociOS-Linux/imagelab> |
| Language | Python |
| Topics | `layer-divine-intelligence` · `layer-hmi` · `layer-prophet-platform` · `role-modality-lab` |
| Activity | 1 PR; last commit 2026-04-05 |

**Purpose & role:** Linux-native image processing capability repo for SourceOS.
Part of the "modality lab" cluster (alongside `ocrlab`, `speechlab`, `videolab`).
Acts as the image-modality admission validator for agent-plane schema wiring.

**Key interfaces & contracts:** The `sourceos-spec` PR #1 follow-up queue explicitly
references: *"Add validator/admission wiring in SociOS-Linux/imagelab"* — it will
consume schema contracts from `sourceos-spec`.

---

### 19. SociOS-Linux/agentos-starter

| Field | Value |
|---|---|
| URL | <https://github.com/SociOS-Linux/agentos-starter> |
| Language | Python |
| Topics | `governance-core` · `para-area` |
| Activity | 1 PR (repo created 2026-03-25) |

**Purpose & role:** **Bootstrap skeleton** for AgentOS interfaces, policy, Linux
integration, and registry scaffolding. The SociOS-Linux side of the AgentOS platform.

**Key interfaces & contracts:** Per `sourceos-spec` PR #1 body, this repo exposes
three core AgentOS interface contracts: **`MemoryAPI`**, **`Orchestrator`**, **`Executor`**.

---

## Organization: SourceOS-Linux

### 20. SourceOS-Linux/sourceos-spec

| Field | Value |
|---|---|
| URL | <https://github.com/SourceOS-Linux/sourceos-spec> |
| Language | JSON Schema, YAML (OpenAPI + AsyncAPI), Python |
| Activity | PR #1 merged 2026-04-05; PR #2 open 2026-04-04 |

**Purpose & role:** The **SourceOS/SociOS typed contracts starter kit (v2)** — a
comprehensive object-family spec following the Open Metadata Types taxonomy, now
extended with the **agent-plane schema family** (53 schemas total, merged PR #1).

**Key interfaces & contracts:**

*Governance:*
`Policy.json`, `PolicyCondition.json` (language: `jsonlogic|cel|rego|cedar`),
`PolicyDecision.json`, `PolicyBinding.json`, `Rule.json`, `CapabilityToken.json`,
`Obligation.json`.

*Agent-plane (new, PR #1):*
`ExecutionDecision.json`, `AgentSession.json`, `ExecutionSurface.json`,
`SkillManifest.json`, `MemoryEntry.json`, `SessionReceipt.json`,
`SessionReview.json`, `ExperimentFlag.json`, `RolloutPolicy.json`,
`TelemetryEvent.json`, `FrustrationSignal.json`, `ReleaseReceipt.json`.

*Data/assets:*
`Dataset.json`, `DataSphere.json`, `Connector.json`, `PhysicalAsset.json`,
`DataRef.json`, `SchemaDefinition.json`, `EntityField.json`, `Field.json`,
`ValidValues.json`.

*Governance metadata:*
`GlossaryTerm.json`, `Agreement.json`, `Party.json`, `ProvenanceRecord.json`,
`TagAssignment.json`, `AuthorityLink.json`.

*Workflow:*
`WorkflowSpec.json`, `WorkflowNode.json`, `WorkflowEdge.json`,
`WorkloadSpec.json`, `RunRecord.json`.

*Collaboration:* `Comment.json`, `Rating.json`, `Community.json`.

*Observability:*
`QualityMetric.json`, `ProfileStats.json`, `ObjectContext.json`,
`SubjectContext.json`, `MappingSpec.json`, `MappingEvidence.json`,
`EventEnvelope.json`, `Exception.json`, `Trigger.json`, `Link.json`,
`ObjectSelector.json`, `SubjectSelector.json`.

*API surface:*
`openapi.yaml`, `openapi.agent-plane.patch.yaml`,
`asyncapi.yaml`, `asyncapi.agent-plane.patch.yaml`.

*Semantic overlay:* `semantic/context.jsonld`, `semantic/hydra.jsonld`.

*Examples (PR #2, open):*
`examples/skill-manifests/coding-agent.SkillManifest.example.json`,
`examples/skill-manifests/review-pr.SkillManifest.example.json`.

**Integration target chain (from PR #1 follow-up queue):**
1. Wire into OpenAPI / AsyncAPI
2. Patch `SociOS-Linux/agentos-starter` interfaces (`MemoryAPI`, `Orchestrator`, `Executor`)
3. Extend `SocioProphet/agentplane` bundle / artifact schemas
4. Add validator/admission wiring in `SociOS-Linux/imagelab`
5. Normalize `SourceOS-Linux/openclaw` runtime surfaces

---

### 21. SourceOS-Linux/openclaw

| Field | Value |
|---|---|
| URL | <https://github.com/SourceOS-Linux/openclaw> |
| Language | TypeScript/JavaScript (pnpm workspace), Nix, Docker, Swift |
| Activity | PR #1 open (draft) 2026-04-04 |

**Purpose & role:** A **personal AI assistant** running on the user's devices, bridging
multiple messaging channels (WhatsApp, Telegram, Slack, Discord, Signal, iMessage,
Teams, Matrix, and more) with AI backends (Claude, GPT). This org hosts a fork/mirror
being aligned to `sourceos-spec` agent-plane contracts.

**Key interfaces & contracts:**
- **SKILL.md runtime surfaces:** PTY requirements, workdir boundaries, background
  session tracking, worktree review lanes, review immutability.
- **SkillManifest** (being added via PR #2 in sourceos-spec): captures PTY requirements,
  background session tracking, sandbox-default policy posture, protected control paths
  (`coding-agent`); review-only worktree, no-push-to-main guardrail,
  artifact persistence (`review-pr`).
- **Channel adapters:** `extensions/` — per-platform adapters.
- **pnpm workspace:** `pnpm-workspace.yaml`, `pnpm-lock.yaml`.

**Sociosphere integration status:** Early-stage. PR #1 makes SKILL.md runtime surfaces
legible to `sourceos-spec` without yet changing OpenClaw's active runtime behavior.

---

## Cross-Cutting Integration Topology

```
sociosphere (workspace controller, Python)
  ├── components: prophet_cli (Go), sourceos_a2a_mcp_bootstrap,
  │               socioprophet-web, human_digital_twin, ontogenesis
  ├── adapters:   cc (container_exec/fs_ops/deps_inventory)
  │               configs (policy/defaults)
  └── third_party: TriTRPC (pinned submodule)

socioprophet (org monorepo, Firebase/Node/Nix)
  ├── agentos/ (AgentOS stack + tool registry)
  └── agentplane/ (stub, mirrors standalone agentplane)

agentplane (standalone control plane, Shell/Nix)
  ├── schemas: bundle, run-artifact, replay-artifact, session-artifact,
  │            promotion-artifact, reversal-artifact, bundle.schema.patch
  ├── policy/imports/control-matrix/
  └── integration bridge → sociosphere, sourceos-spec

TriTRPC (wire protocol, Rust/Go/Python)
  └── consumed by: socioprophet-standards-storage, human-digital-twin,
                   prophet-platform/rpc/, slash-topics,
                   sourceos-a2a-mcp-bootstrap

sourceos-spec (typed contracts, JSON Schema / OpenAPI / AsyncAPI)
  └── integration targets:
        agentos-starter (MemoryAPI, Orchestrator, Executor)
        agentplane (bundle/artifact schemas)
        imagelab (admission wiring)
        openclaw (runtime normalization)

workstation-contracts (SociOS-Linux) ──→ agentos-socios execution plane
socios (SociOS-Linux) ──→ SourceOS CI/CD automation commons (opt-in)
sourceos-a2a-mcp-bootstrap ──→ bridges SourceOS ↔ SocioProphet MCP/TritRPC
```

---

## Terms for Controlled Glossary / Ontology Spec

### Layer taxonomy (from GitHub topic tags)

| Tag | Layer |
|---|---|
| `layer-sourceos` | Base OS + CI foundation |
| `layer-agentos-socios` | AgentOS / agent execution |
| `layer-prophet-platform` | Prophet Platform (apps + infra) |
| `layer-divine-intelligence` | AI / ML / modality stack |
| `layer-hmi` | Human-machine interface |
| `layer-aleph` | Knowledge commons (Aleph surface) |
| `layer-protocol` | Wire protocol + contracts |

### Role taxonomy (from topic tags and manifest)

| Tag / manifest role | Component |
|---|---|
| `role-governance-controller` | sociosphere |
| `role-bridge` | sourceos-a2a-mcp-bootstrap, mcp-a2a-zero-trust |
| `role-modality-lab` | imagelab, ocrlab, speechlab, videolab |
| `role-human-machine-interface` | cloudshell-fog |
| `component` | prophet_cli, human_digital_twin, ontogenesis, … |
| `adapter` | cc, configs |
| `third_party` | TriTRPC |

### Core protocol terms (TritRPC)

- **TritPack243** — 5 trits per byte; tail marker for 1-4 trailing trits
- **TLEB3** — length encoding: base-9 digits as tritlets packed by TritPack243
- **Path-A** — Avro Binary Encoding payload
- **Path-B** — ternary-native payload (toy subset)
- **AEAD envelope** — XChaCha20-Poly1305, 24-byte nonce, authenticated frame

### Agent-plane schema terms (sourceos-spec `schemas/`)

`ExecutionDecision`, `AgentSession`, `ExecutionSurface`, `SkillManifest`,
`MemoryEntry`, `SessionReceipt`, `SessionReview`, `ExperimentFlag`,
`RolloutPolicy`, `TelemetryEvent`, `FrustrationSignal`, `ReleaseReceipt`

### HDT / Ω Protocol terms

- **Ω (Omega) evaluation lattice** — 7-state promotion:
  `ABSENT → SEEDED → NORMALIZED → LINKED → TRUSTED → ACTIONABLE → DELIVERED`
- **m_cbd** — coherence / boundedness / de-dup score ∈ [0,1]
- **m_cgt** — consent / governance / trust score ∈ [0,1]
- **m_nhy** — delivery / usefulness score ∈ [0,1]
- **CapD** — capability descriptor (cross-platform packaging)
- **repair pushout** — triggered when inputs violate invariants

### Governance metadata terms (sourceos-spec)

`GlossaryTerm`, `Agreement`, `Party`, `ProvenanceRecord`,
`PolicyCondition` (languages: `jsonlogic | cel | rego | cedar`),
`CapabilityToken`, `AuthorityLink`

### Workspace management terms

`bundle` (unit of deployment), `manifest role` (component | adapter | third_party | docs),
`lock file` (exact revision pins), `task contract` (Makefile/justfile/Taskfile tasks),
`fixture` (canonical byte-level compatibility vector), `evidence artifact`,
`replay artifact`, `GAKW hybrid warm trace`
