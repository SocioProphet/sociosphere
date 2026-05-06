# Sovereign Civic Computation Estate Alignment

Version: v0.1
Status: draft control-plane alignment
Owner: SocioSphere

## Purpose

This document records the cross-estate alignment for sovereign local-first computing, citizen governance, Rregis / ACR concordance, Ontogenesis lifecycle semantics, Gaia world-model semantics, Prophet governance and simulation, SourceOS runtime custody, TriTRPC communication, AgentPlane execution, and policy/proof enforcement.

SocioSphere is the workspace control plane. It declares repositories, pins revisions, materializes the multi-repo workspace, validates topology, hosts shared standards, and records cross-repo governance. Downstream feature implementation remains in the owning repositories.

## Control-plane rule

SocioSphere coordinates; domain repositories implement.

This means:

- SocioSphere owns the estate map, registry metadata, dependency direction, validation lanes, and conformance reporting.
- Ontogenesis owns lifecycle and ontology semantics.
- Rregis / regis-entity-graph owns entity, evidence, concordance, and relationship identity semantics.
- SourceOS owns local-first runtime, boot, sync, shell, local custody, and citizen-node behavior.
- Prophet Platform owns governance workflow, policy simulation, decision orchestration, and review/appeal surfaces.
- Gaia owns civic, ecological, commons, jurisdiction, and world-model ontology surfaces.
- Policy Fabric owns executable policy packs, validation evidence, and policy-as-code gates.
- TriTRPC / AgentPlane / MCP surfaces own protocol, capability, delegation, proof-carrying request, and agent execution boundaries.

## Canonical repo alignment

| Capability | Canonical repo | SocioSphere responsibility |
|---|---|---|
| Workspace control plane | `SocioProphet/sociosphere` | Manifest, lock, topology, registry, conformance, source-exposure governance |
| Ontology lifecycle semantics | `SocioProphet/ontogenesis` | Track as component; validate that lifecycle specs/shapes/examples remain present |
| Entity graph / ACR | `SocioProphet/regis-entity-graph` | Track as identity component; require entity/evidence/concordance contract surface |
| SourceOS substrate | `SocioProphet/source-os` and SourceOS-Linux repos | Track runtime/OS surface; require local-first doctrine and sync/consent contracts |
| SourceOS spec | `SourceOS-Linux/sourceos-spec` | Track external org canonical spec; require alignment with SourceOS doctrine |
| SourceOS boot | `SourceOS-Linux/sourceos-boot` | Track boot/proof/recovery surface |
| SourceOS sync | `SourceOS-Linux/sourceos-syncd` | Track local-first sync and consent receipt enforcement |
| Prophet platform | `SocioProphet/prophet-platform` | Track governance workflow, simulation, review queues, appeals |
| Gaia ontology | `SocioProphet/prophet-domain-gaia-ontology` | Track world-model ontology alignment |
| Gaia curation vault | `SocioProphet/prophet-domain-gaia-curation-vault` | Track curated dataset provenance surface |
| Policy as code | `SocioProphet/policy-fabric` | Track executable policy packs and validation evidence |
| Protocol / RPC | `SocioProphet/tritrpc` | Track protocol fixtures and reference semantics |
| Agent plane | `SocioProphet/agentplane` | Track agent runtime / capability boundary when present in workspace |
| MCP/A2A zero-trust | `SocioProphet/mcp-a2a-zero-trust` | Track adapter boundary and zero-trust proof-carrying handoffs |
| Trust registry | `SocioProphet/trust-registry` | Track trust registry administration and service contracts |
| DID resolver | `SocioProphet/did-resolver` | Track decentralized identifier resolution |
| VC issuer/verifier | `SocioProphet/vc-issuer`, `SocioProphet/vc-verifier` | Track credential issuance and verification surfaces |
| Identity-is-prime | `SocioProphet/identity-is-prime-reference` | Track identity primitive reference semantics |
| DevSecOps intelligence | `SocioProphet/global-devsecops-intelligence` | Track typed telemetry and operational reasoning surface |

## Architecture lanes

### Lane 1: Entity and evidence concordance

Home: `SocioProphet/regis-entity-graph`

Required contracts:

- `CanonicalEntity`
- `SourceRecord`
- `ConcordanceLink`
- `EvidenceClaim`
- `DecisionLedgerEntry`
- `EnergyLedgerEntry`
- `PromotionPolicy`
- `RelationshipFormationHook`

SocioSphere validation expectation:

- repo declares identity role
- examples exist for source record, canonical entity, concordance link, decision ledger, and merge/split event
- decision ledger entries include policy version and replay metadata

### Lane 2: Ontogenesis lifecycle semantics

Home: `SocioProphet/ontogenesis`

Required contracts and shapes:

- `GenesisEvent`
- `LifecycleState`
- `ValidityInterval`
- `DerivationPath`
- `EntityFormationRecord`
- `RelationshipFormationRecord`
- `ValueFlowEvent`
- `GovernanceAct`
- `ParticipationRole`
- `OntogenicRule`

SocioSphere validation expectation:

- lifecycle specs are indexed under docs/specs
- SHACL gates exist for formation, validity, replay, and authority transitions
- examples validate through the Ontogenesis verification pipeline

### Lane 3: Sovereign local-first runtime

Homes: `SocioProphet/source-os`, `SourceOS-Linux/sourceos-spec`, `SourceOS-Linux/sourceos-syncd`, `SourceOS-Linux/sourceos-boot`

Required contracts:

- `ConsentReceipt`
- `SyncIntent`
- `LocalVaultRecord`
- `LocalProofArtifact`
- `DeviceClaim`
- `BootProofClaim`
- `CitizenNodeExport`

SocioSphere validation expectation:

- local-first doctrine exists in canonical SourceOS docs
- sync operations reference consent or lawful/public-interest policy basis
- boot/recovery claims can bind to proof artifacts

### Lane 4: Citizen governance and policy simulation

Homes: `SocioProphet/prophet-platform`, `SocioProphet/policy-fabric`

Required contracts:

- `GovernanceDecision`
- `ReviewTask`
- `AppealRecord`
- `PolicyPack`
- `PolicyDecision`
- `PolicySimulationRun`
- `DecisionImpactReport`

SocioSphere validation expectation:

- high-stakes governance flows have review/appeal fixtures
- policy changes include diff reports
- policy simulation can consume entity, evidence, and lifecycle state

### Lane 5: Agent and protocol capability governance

Homes: `SocioProphet/tritrpc`, `SocioProphet/agentplane`, `SocioProphet/mcp-a2a-zero-trust`

Required contracts:

- `ProofCarryingRequest`
- `CapabilityGrant`
- `DelegationGrant`
- `AgentIdentity`
- `CapabilityScope`
- `NonEscapeClaim`

SocioSphere validation expectation:

- protocol fixtures exist
- capability boundaries are explicit
- agents use delegated capabilities, not ambient access
- proof-carrying requests can reference consent, policy, validity interval, and proof artifact

### Lane 6: Gaia world model and commons semantics

Homes: `SocioProphet/prophet-domain-gaia-ontology`, `SocioProphet/prophet-domain-gaia-curation-vault`

Required surfaces:

- citizen ontology
- commons ontology
- jurisdiction ontology
- public-service ontology
- participation ontology
- consent ontology
- curated dataset provenance and curation evidence

SocioSphere validation expectation:

- Gaia ontology remains the civic/ecological semantic authority
- curation vault maintains provenance and review state
- Ontogenesis lifecycle objects can bind to Gaia ontology objects

## Cross-estate invariants

1. Canonical coordination lives in SocioSphere.
2. Domain implementation lives in the domain repo.
3. Canonical entities, relationships, and lifecycle transitions must be replayable.
4. Citizen-local state must not be overwritten by cloud projection without sync intent plus consent or policy basis.
5. Agents must use scoped capability grants rather than ambient access.
6. High-stakes governance decisions require evidence, policy version, actor or agent context, review or appeal semantics, and replay path.
7. Ontology and contract changes must be validated through examples, shapes, schemas, or fixtures before promotion.
8. Public source exposure must comply with the Source Exposure Governance Standard.

## Initial implementation queue

### Step 1: SocioSphere control-plane registry

- Add this alignment document.
- Add or update machine-readable registry entries for the lanes above.
- Generate or maintain a conformance checklist from these lanes.

### Step 2: Rregis / ACR domain artifact

- Add ACR entity/evidence/concordance contracts in `SocioProphet/regis-entity-graph`.
- Bind ACR formation hooks to Ontogenesis lifecycle records.

### Step 3: SourceOS local-first doctrine

- Add sovereign local-first runtime doctrine in `SocioProphet/source-os` or `SourceOS-Linux/sourceos-spec`.
- Bind sync and local custody concepts to consent receipts and proof artifacts.

### Step 4: Policy and governance enforcement

- Add policy-pack gates in `SocioProphet/policy-fabric`.
- Bind Prophet governance flows to review, appeal, and policy simulation contracts.

### Step 5: Protocol and agent handoff

- Add proof-carrying request and capability-grant bindings in `SocioProphet/tritrpc`, `SocioProphet/agentplane`, and `SocioProphet/mcp-a2a-zero-trust`.

## Supersession note

Any similar alignment documents previously committed to personal or archive repositories are non-canonical unless explicitly mirrored into the organizational repositories and referenced from SocioSphere.

SocioSphere is the canonical control-plane source for this estate alignment.
