# Rescued SocioProphet Platform Integration Backlog

Date: 2026-05-13
Status: captured as backlog/spec material
Control issue: https://github.com/SocioProphet/sociosphere/issues/333

## Interpretation

This note records a rescued chat artifact describing SocioProphet platform UI and integration work. The artifact is valuable because it identifies missing product-integration surfaces, but it must not be treated as evidence that those features are implemented.

The recovered material repeatedly describes a sophisticated Vue shell and later acknowledges that the shell remains mock/stubbed unless connected to live services. SocioSphere therefore records this as a backlog and protocol capture, not as a completion claim.

## Placement rule

- Product Vue UI work belongs in `SocioProphet/socioprophet`.
- The UI lineage should preserve the `mdheller/socioprophet-web` origin.
- Lattice/runtime placement is routed to `SocioProphet/lattice-forge` because no `SocioProphet/prophet-lattice` repository was found at capture time.
- SocioSphere owns protocol, fixture, fanout, validation, and release-readiness rules, not downstream feature implementation.

## Delta captured from rescued work

The recovered artifact contributes the following backlog surfaces:

1. Browser-native knowledge capture.
2. Cryptographic sealing of captured material.
3. Memex-style clips with attribution.
4. Polyplexus-style micro-publication workflow.
5. OVAL/Socratic educational dialogue runtime.
6. Parent oversight without micromanagement.
7. edX/Tutor-style course ingestion.
8. Adaptive learning paths and assessment.
9. Agent configuration workbench with multimodal knowledge attachment.
10. Agent schema/type editor for input, output, and state.
11. SkillsTree-style training/evaluation bindings.
12. Compute marketplace / execution placement surface.
13. Real Life Mirror telemetry panel.
14. Agent evolution triggers with creator approval.
15. Neo4j Bloom / Watson Knowledge Studio / WebProtege-grade ontology workbench.
16. 3D graph universe explorer.
17. UI runtime adapter doctrine: mock boundary, live adapter, fixture, test, owner.
18. Regional mesh/backbone management UI.
19. Knowledge propagation, curation, and bias-mitigation commons layer.
20. Quantum backend routing UX for PennyLane/Qiskit if retained.

## Runtime truthfulness rule

A UI surface must not be called live, working, or fully functional unless it has at least:

- an owning service repository,
- a typed frontend adapter,
- a fixture payload,
- an error/degraded-state model,
- an authorization/capability profile where needed,
- an integration test or replay fixture.

This rule is formalized in `protocol/ui-runtime-adapter/v0/`.

## Fanout

- UI / Vue runtime adapter layer: https://github.com/SocioProphet/socioprophet/issues/323
- AgentPlane runtime contracts: https://github.com/SocioProphet/agentplane/issues/159
- MCP/A2A session and capability grants: https://github.com/SocioProphet/mcp-a2a-zero-trust/issues/6
- Alexandrian Academy educational dialogue runtime: https://github.com/SocioProphet/alexandrian-academy/issues/18
- Ontogenesis ontology validation and promotion contract: https://github.com/SocioProphet/ontogenesis/issues/88
- Lattice/runtime placement assessment: https://github.com/SocioProphet/lattice-forge/issues/16
- Knowledge capture / cryptographic sealing / micro-publication standards: https://github.com/SocioProphet/socioprophet-standards-knowledge/issues/79
- Agent configuration workbench schemas: https://github.com/SocioProphet/socioprophet-agent-standards/issues/23

## Control-plane artifacts added

- `protocol/ui-runtime-adapter/v0/README.md`
- `protocol/ui-runtime-adapter/v0/fixtures/rescued-platform-ui.features.v0.json`
- `docs/notes/rescued-socioprophet-platform-integration-2026-05-13.md`
