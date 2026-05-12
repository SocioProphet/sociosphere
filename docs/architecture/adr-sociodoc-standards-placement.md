# ADR: SocioDoc Standards Placement and Blast Radius

## Status

Proposed.

## Context

SocioDoc is the canonical document intermediate representation for SocioProphet document intelligence, provenance, policy, publication, and digital commons governance. It is not merely a Markdown convention, storage layout, rendering format, or platform feature. It is a cross-repository contract that must be authoritative, testable, and adoptable without requiring private conversational context.

Sociosphere is the SocioProphet workspace controller. It owns the canonical workspace manifest, lock, runner semantics, cross-repo registry metadata, source-exposure governance, adversarial hardening critique, and validation lanes. Sociosphere therefore owns orchestration and enforcement for SocioDoc adoption, but it should not own every normative SocioDoc semantic.

The existing workspace topology already separates standards authority across platform, storage, and knowledge standards repositories. SocioDoc should follow that topology instead of creating a duplicate catch-all standards repository.

## Decision

SocioDoc SHALL be split across four coordinated authority surfaces:

1. **Core SocioDoc semantics** SHALL live in `SocioProphet/socioprophet-standards-knowledge`.
2. **SocioDoc storage, hashing, object layout, indexing, and persistence profile** SHALL live in `SocioProphet/socioprophet-standards-storage`.
3. **SocioDoc platform, agent, runtime, publishing, and document-intelligence adoption profile** SHALL live in `SocioProphet/prophet-platform-standards`.
4. **SocioDoc workspace enforcement, validation lanes, adoption registry, upstream mapping, and blast-radius tracking** SHALL live in `SocioProphet/sociosphere`.

The governing rule is:

```text
standards repos define the law
sociosphere enforces the law
platform and component repos consume the law
```

## Canonical Namespace Ownership

The following namespace ownership should be reflected in `governance/CANONICAL_SOURCES.yaml` in a follow-up change:

```yaml
standards/sociodoc:
  canonical_repo: socioprophet-standards-knowledge
  note: "Core SocioDoc document IR semantics: sections, blocks, entities, claims, citations, provenance, policy, and conformance levels."

standards/sociodoc/storage:
  canonical_repo: socioprophet-standards-storage
  upstream_standard: socioprophet-standards-knowledge
  note: "Storage profile for SocioDoc object layout, content addressing, index records, hash manifests, and retention metadata."

standards/sociodoc/platform-adoption:
  canonical_repo: prophet-platform-standards
  upstream_standard: socioprophet-standards-knowledge
  note: "Platform adoption profile for agents, document pipelines, publication readiness, policy gates, and runtime integration."

workspace/sociodoc-validation:
  canonical_repo: sociosphere
  upstream_standard: socioprophet-standards-knowledge
  note: "Workspace validation lanes, adoption registry, upstream mapping, and blast-radius reports for SocioDoc conformance."
```

## Rationale

### Knowledge standards own core meaning

SocioDoc core semantics concern document meaning: sections, blocks, entities, claims, citations, provenance, policy, source spans, conformance levels, and graph/intelligence projection. These are knowledge-representation concerns. They belong in `socioprophet-standards-knowledge`.

### Storage standards own persistence semantics

SocioDoc documents must eventually be stored, hashed, indexed, retained, and retrieved deterministically. Those rules are storage concerns. They belong in `socioprophet-standards-storage`, but they must treat the core SocioDoc model as upstream authority.

### Platform standards own runtime adoption

Agents, CLIs, SDKs, APIs, publishing workflows, and document-intelligence services need an adoption profile. That is a platform concern. It belongs in `prophet-platform-standards`, with SocioDoc core semantics treated as upstream authority.

### Sociosphere owns orchestration and enforcement

Sociosphere owns workspace-level manifesting, registry metadata, topology checks, runner semantics, validation lanes, source-exposure governance, and change-propagation rules. Sociosphere should enforce SocioDoc adoption and track blast radius, but it should not become the semantic authority for the SocioDoc model.

## Blast Radius

SocioDoc has a broad blast radius because it touches authoring, storage, intelligence extraction, publishing, provenance, policy, identity, graph projection, source-exposure checks, and CI validation.

### Tier 0 — Standards authority

Affected repositories:

- `SocioProphet/socioprophet-standards-knowledge`
- `SocioProphet/socioprophet-standards-storage`
- `SocioProphet/prophet-platform-standards`
- `SocioProphet/sociosphere`

Primary risks:

- Duplicate authority.
- Schema drift.
- Conflicting validators.
- Unclear canonical ownership.

Controls:

- One canonical owner per namespace.
- Upstream/downstream relationships recorded explicitly.
- Sociosphere validates adoption but does not redefine core semantics.

### Tier 1 — Workspace orchestration

Affected surfaces in `sociosphere`:

- `manifest/workspace.toml`
- `manifest/workspace.lock.json`
- `registry/canonical-repos.yaml`
- `registry/dependency-graph.yaml`
- `registry/change-propagation-rules.yaml`
- `governance/CANONICAL_SOURCES.yaml`
- `tools/runner/runner.py`
- `tools/check_topology.py`

Primary risks:

- Workspace manifest and lock drift.
- Missing propagation rules.
- Broken validation lanes.
- Silent downstream non-adoption.

Controls:

- Add SocioDoc adoption registry.
- Add SocioDoc upstream mapping.
- Add SocioDoc validation commands.
- Add change-propagation rules before broad enforcement.

### Tier 2 — Knowledge and documentation

Likely affected repositories:

- `SocioProphet/knowledge-graph`
- `SocioProphet/graph-explorer`
- `SocioProphet/data-pipeline`
- `SocioProphet/event-bus`
- `SocioProphet/semantic-search-bi`
- `SocioProphet/gaia-world-model`
- `SocioProphet/regis-entity-graph`
- `SocioProphet/ontogenesis`
- `SocioProphet/alexandrian-academy`
- `SocioProphet/socioprophet-docs`
- `SocioProphet/architecture-docs`
- `SocioProphet/api-specs`
- `SocioProphet/onboarding-docs`
- `SocioProphet/runbooks`

Primary risks:

- Raw prose continues to bypass canonical IR.
- Claims, citations, and entities are extracted inconsistently.
- SocioDoc identifiers conflict with graph identifiers.
- Legacy documents are mistaken for evidence-grade documents.

Controls:

- Begin with opt-in pilot adoption.
- Grandfather legacy documents as Level 0.
- Require SocioDoc metadata only for new governed documents at first.
- Define graph projection after the core model stabilizes.

### Tier 3 — Platform, agents, SDKs, and UI

Likely affected repositories:

- `SocioProphet/prophet-platform`
- `SocioProphet/prophet-cli`
- `SocioProphet/prophet-sdk`
- `SocioProphet/prophet-ui`
- `SocioProphet/ui-workbench`
- `SocioProphet/agentplane`
- `SocioProphet/TriTRPC`
- `SocioProphet/semantic-serdes`
- `SocioProphet/workspace-runner`

Primary risks:

- Premature API churn.
- Agents emit nonconformant documents.
- CLI, SDK, and platform validators diverge.
- UI renderers treat rendered Markdown as canonical.

Controls:

- Define platform adoption after the core standard.
- Add SDK/CLI validation only after schemas and examples stabilize.
- Keep rendered formats derivative.
- Do not require runtime adoption in the initial SocioDoc standard.

### Tier 4 — Security, compliance, and source exposure

Likely affected repositories:

- `SocioProphet/mcp-a2a-zero-trust`
- `SocioProphet/zero-trust-bindings`
- `SocioProphet/fips-compliance`
- `SocioProphet/nist-800-53-controls`
- `SocioProphet/crypto-carriers`
- `SocioProphet/policy-fabric`
- `SocioProphet/global-devsecops-intelligence`
- `SocioProphet/exodus`

Primary risks:

- Generated documents expose restricted material.
- Policy metadata becomes optional.
- Source-exposure validation is bypassed.
- Provenance is too weak for evidence-grade workflows.

Controls:

- Policy and provenance are mandatory for conforming SocioDoc.
- Source-exposure gates run before publication.
- Security-sensitive documents carry visibility labels.
- Published artifacts retain source hash and IR hash.

### Tier 5 — Connectors and external ingestion

Likely affected repositories:

- `SocioProphet/connector-github`
- `SocioProphet/connector-gitlab`
- `SocioProphet/connector-jira`
- `SocioProphet/connector-slack`
- `SocioProphet/connector-kafka`

Primary risks:

- Inbound GitHub, Jira, Slack, or Kafka content is normalized inconsistently.
- Source spans are unavailable or unstable.
- External events are forced prematurely into full SocioDoc conformance.

Controls:

- Do not require connectors to emit full SocioDoc v1 initially.
- Define external-content ingestion profiles later.
- Treat connector mapping as a platform adoption concern.

## Conformance Levels

SocioDoc adoption SHALL be staged through conformance levels.

### Level 0 — Legacy document

Existing Markdown, prose, or rendered artifacts. No SocioDoc conformance is claimed. Source-exposure checks may still apply.

### Level 1 — Profiled Markdown

Markdown conforms to the SocioProphet Markdown Profile and includes required front matter.

### Level 2 — Valid SocioDoc IR

The document compiles into SocioDoc JSON and validates against the SocioDoc schema.

### Level 3 — Evidence-grade SocioDoc

Claims, citations, entities, provenance, source spans, policy fields, and reference resolution are complete.

### Level 4 — Published commons artifact

Rendered artifacts are derivative outputs linked to SocioDoc IR hash, source hash, policy state, license, and publication manifest.

## Rollout Plan

### Phase 0 — Authority and placement

- Add this ADR.
- Add canonical namespace entries.
- Add dependency graph entries.
- Add change-propagation rules.

### Phase 1 — Core standard

In `socioprophet-standards-knowledge`, create:

- `standards/sociodoc/v1/README.md`
- `standards/sociodoc/v1/sociodoc-v1.md`
- `standards/sociodoc/v1/sociodoc-v1.schema.json`
- `standards/sociodoc/v1/markdown-profile-v1.md`
- `standards/sociodoc/v1/frontmatter-v1.schema.json`
- `standards/sociodoc/v1/claim-model-v1.schema.json`
- `standards/sociodoc/v1/citation-model-v1.schema.json`
- `standards/sociodoc/v1/entity-model-v1.schema.json`
- `standards/sociodoc/v1/provenance-model-v1.schema.json`
- `standards/sociodoc/v1/examples/minimal.sociodoc.json`
- `standards/sociodoc/v1/examples/invalid-missing-provenance.sociodoc.json`
- `standards/sociodoc/v1/examples/canonical-markdown-example.md`

### Phase 2 — Storage profile

In `socioprophet-standards-storage`, create:

- `standards/sociodoc-storage/v1/README.md`
- `standards/sociodoc-storage/v1/sociodoc-storage-profile-v1.md`
- `standards/sociodoc-storage/v1/object-layout-v1.schema.json`
- `standards/sociodoc-storage/v1/hash-manifest-v1.schema.json`
- `standards/sociodoc-storage/v1/index-record-v1.schema.json`
- `standards/sociodoc-storage/v1/examples/content-addressed-layout.example.json`

### Phase 3 — Platform adoption profile

In `prophet-platform-standards`, create:

- `standards/document-intelligence/v1/README.md`
- `standards/document-intelligence/v1/sociodoc-adoption-profile-v1.md`
- `standards/document-intelligence/v1/agent-document-pipeline-v1.md`
- `standards/document-intelligence/v1/publishing-readiness-profile-v1.md`
- `standards/document-intelligence/v1/policy-gates-v1.md`

### Phase 4 — Sociosphere enforcement

In `sociosphere`, create:

- `registry/sociodoc-adoption.yaml`
- `standards/sociodoc/upstreams.yaml`
- `docs/architecture/sociodoc-blast-radius.md`
- `tools/sociodoc/validate_sociodoc.py`
- `tools/sociodoc/validate_markdown_profile.py`
- `tools/sociodoc/check_sociodoc_adoption.py`
- `tests/sociodoc/test_examples.py`

### Phase 5 — Pilot adoption

Pilot adoption SHOULD begin with:

- `SocioProphet/socioprophet-docs`
- `SocioProphet/architecture-docs`
- `SocioProphet/alexandrian-academy`
- `SocioProphet/knowledge-graph`
- `SocioProphet/regis-entity-graph`

### Phase 6 — Broad rollout

- Existing docs remain Level 0 unless migrated.
- New standards docs require Level 1.
- New generated docs require Level 2.
- Evidence-grade governance documents require Level 3.
- Public commons publications require Level 4.

## Non-Goals

This ADR does not require rewriting all existing documentation.

This ADR does not make PDF, HTML, DOCX, or EPUB canonical.

This ADR does not require every connector to emit full SocioDoc immediately.

This ADR does not merge the three standards repositories.

This ADR does not define the complete SocioDoc schema; it defines placement, authority, and blast-radius governance.

## Consequences

### Positive consequences

- Clear standards authority.
- Reduced schema drift.
- Safer multi-repo rollout.
- Testable adoption path.
- Better alignment between document intelligence, storage, policy, and publishing.

### Negative consequences

- More initial structure.
- More files across more repositories.
- Slower first implementation.
- Requires discipline to avoid redefining SocioDoc in downstream repos.

### Neutral consequences

- Sociosphere gains validation responsibility but not semantic ownership.
- Storage and platform standards gain companion profiles but remain downstream of the knowledge standard.

## Acceptance Criteria

This ADR is accepted when:

1. The canonical namespace ownership entries are added to `governance/CANONICAL_SOURCES.yaml`.
2. SocioDoc standards dependencies are represented in `registry/dependency-graph.yaml`.
3. SocioDoc change-propagation behavior is represented in `registry/change-propagation-rules.yaml`.
4. The core SocioDoc v1 skeleton exists in `socioprophet-standards-knowledge`.
5. Storage and platform adoption companion skeletons exist in their respective standards repositories.
6. Sociosphere contains an adoption registry and validation plan.

## Review Notes

The desired outcome is not a document dump. The desired outcome is an enforceable standards program: authority first, schema second, examples third, validation fourth, and broad adoption last.
