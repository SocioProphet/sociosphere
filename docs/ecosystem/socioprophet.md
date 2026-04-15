# Repository Analysis — SocioProphet/socioprophet

**GitHub:** https://github.com/SocioProphet/socioprophet  
**Role in ecosystem:** Main collaborative platform  
**Last analysed:** 2026-04-08

---

## 1. Repository Purpose & Identity

### What it does
The main collaborative platform that unifies two sub-systems: **AgentOS** (a layered agent
stack: interfaces, policies, tool registry, Linux integration) and **Agentplane** (a
fleet-shaped control plane for reproducible agent execution).

### Core responsibilities
- `agentos/` — interfaces, policy, tool registry, Linux integration runbook, CI definitions.
- `agentplane/` — Nix flake, bundle schema, runner scripts.
- `registry/` — canonical tool registry (YAML + CSV); "compliance + inventory source of
  truth".
- `inventory/` — stack inventory + RACI.
- `workspaces/` — workspace controllers (socio-linux + socioprophet) as Nix-first stubs.
- `socioprophet-web/` — Firebase-backed web client; deny-by-default Firestore rules.
- Security enforcement: Firestore emulator-backed tests, Gitleaks, CodeQL.

### What systems depend on it
- Users of the SocioProphet platform (web client consumers).
- `prophet-platform` — links to `socioprophet-web` as a deployable app.
- `sociosphere` — manifest includes `socioprophet-web` as a component.

### What it depends on
- Firebase / Google Firestore (`.firebaserc`, `firebase.json`)
- Nix (`flake.nix`) for reproducible dev environments
- TriTRPC (protocol layer, referenced through agentplane sub-system)
- Webpack (web client build)

### Key files
- `README.md` — layout overview, AgentOS / agentplane unification
- `docs/architecture.md` — 3 design principles + component breakdown
- `agentos/interfaces/` — AgentOS interface definitions
- `agentos/policy/` — policy declarations
- `agentos/registry/` — tool registry
- `registry/agentos-tool-registry.yaml` — canonical tool registry (validated by
  `scripts/validate_registry.py`)
- `agentplane/bundles/` — bundle schema and example agent
- `firebase.json` + `socioprophet-web/firestore.rules` — security posture
- `flake.nix` — Nix dev environment

---

## 2. Controlled Vocabulary & Ontology

### Key terms
| Term | Definition | Source |
|---|---|---|
| **AgentOS** | Layered agent stack: interfaces, policy, tool registry, Linux integration | `README.md` |
| **Agentplane** | Fleet-shaped control plane for reproducible execution | `README.md` |
| **Tool registry** | Canonical YAML + CSV listing of agent tools; compliance + inventory source of truth | `registry/` |
| **Agentplane bundle** | "The unit of deployment/execution across your executor fleet" | `README.md` |
| **AIWG artifacts** | System-of-record from agentic working group | `README.md` |
| **Agentplane evidence artifacts** | Validation/Placement/Run artifacts from execution | `README.md` |
| **Auditable trail** | Reconciled AIWG + agentplane artifact chain | `README.md` |
| **RACI** | Responsibility, Accountability, Consulted, Informed inventory matrix | `inventory/` |
| **window.__FIREBASE_CONFIG__** | Runtime Firebase config injection (not build-time) | `docs/architecture.md` |
| **Deny-by-default** | Firestore security posture: explicit allow rules only | `docs/architecture.md` |

### Domain-specific language
- The tool registry is the **compliance source of truth** — bundles reference it, not the
  other way around.
- Firebase rules are **test-backed**: emulator rules tests must pass in CI before merge.
- Runtime config injection prevents **build-time secret taint**.
- AgentOS and agentplane are **complementary, not redundant**: AgentOS answers "what is
  allowed?", agentplane answers "where does it run and where is the evidence?".

### Semantic bindings to other repos
- **↔ agentplane** (standalone repo): socioprophet contains an agentplane sub-directory;
  defines AgentOS tool registry that agentplane bundles reference.
- **→ sociosphere**: socioprophet-web is a component in sociosphere's manifest.
- **→ prophet-platform**: prophet-platform deploys socioprophet-web as an app.

---

## 3. Topic Modeling

| Topic | Keywords | Weight |
|---|---|---|
| Agent infrastructure | AgentOS, tool registry, interfaces, policy, linux, RACI | dominant |
| Execution control plane | agentplane, bundle, validate, place, run, evidence, replay | dominant |
| Security / compliance | Firebase rules, deny-by-default, Gitleaks, CodeQL, emulator tests | high |
| Web platform | socioprophet-web, webpack, Firebase, Firestore | high |
| Reproducible environments | Nix flake, Fedora Silverblue, Lima, immutable OS | medium |
| Knowledge commons | knowledge graph, provenance, attribution, local-first, federation | medium (planned) |
| Agentic audit trail | AIWG artifacts, evidence artifacts, auditable trail | medium |

---

## 4. Dependency Graph

### Direct dependencies
- Firebase / Firestore (runtime storage + auth)
- Nix (dev environment)
- Webpack (web client build)
- TriTRPC (protocol, referenced through agentplane sub-system)

### Dependent systems
- `prophet-platform` — deploys `apps/socioprophet-web`
- `sociosphere` — lists `socioprophet-web` as managed component

### Cross-repo impact when socioprophet changes
- Tool registry changes → agentplane bundles referencing changed tools must update.
- AgentOS interface changes → all consumers of those interfaces must update.
- Firebase rules changes → security posture shift; requires emulator test pass.

---

## 5. Change Impact Rules

| What changed | Downstream repos affected | DevOps actions | Governance gates |
|---|---|---|---|
| `registry/` tool registry | agentplane (bundles referencing changed tools) | Re-validate bundles | Registry version bump; RACI review |
| `agentos/interfaces/` | Any service implementing those interfaces | Rebuild + test all AgentOS consumers | Interface versioning; ADR |
| `agentos/policy/` | Policy enforcement throughout the stack | Policy regression tests | Security review gate |
| `socioprophet-web/firestore.rules` | Socioprophet-web + any Firestore consumer | Emulator rules test + Gitleaks must pass | Security review mandatory before merge |
| `flake.nix` | Dev environment reproducibility | Nix build validation | Lock hash update |
