# Proof Apparatus Workspace Protocol (v0)

SocioSphere owns the orchestration layer for SocioProphet proof programs.

The proof repositories remain the domain engines: they contain the mathematics, fixtures, computations, notebooks, papers, and repo-local tests. SocioSphere owns the cross-repo workspace contract: manifest membership, proof-slice routing, gate execution semantics, evidence-event shape, provenance expectations, and promotion/rollback policy.

This protocol extends the EMVI Proof Slice Protocol. EMVI proves that a governed workspace can coordinate browser, editor, terminal, graph, collection, snapshot, and ledger flows under one shell. The proof apparatus workspace applies the same controller discipline to mathematical claims, test gates, finite-order computations, and cross-repository evidence promotion.

## Controller boundary

SocioSphere owns:

- proof workspace manifest and repo roles
- proof claim object model
- proof gate object model
- evidence and severity ledger contracts
- cross-repo orchestration order
- deterministic replay requirements
- provenance and artifact-hash requirements
- failure-wall taxonomy
- promotion, demotion, quarantine, and archival states
- integration with workspace runner, ledger, policy, graph, and UI workbench surfaces

Domain proof repositories own:

- mathematical definitions
- repo-local scripts and fixtures
- proofs, papers, notebooks, datasets, and certificates
- repo-local CI tests
- domain-specific claim boundaries
- domain-specific non-claims and obstruction statements

SocioSphere must never silently upgrade a domain claim. It may only register, route, test, compare, promote, quarantine, or archive claims using evidence emitted by the domain repositories.

## Required object kinds

The controller recognizes these object kinds:

- `ProofProgram`
- `ProofClaim`
- `ProjectionSpec`
- `PreimageObstruction`
- `ProofGate`
- `ProofTest`
- `EvidenceEvent`
- `ArtifactDigest`
- `PromotionDecision`
- `ClaimBoundary`
- `NonClaim`
- `WorkspaceSnapshot`

## Severity ladder

The proof workspace uses the shared severity ladder:

| Level | Meaning |
|---|---|
| `E0` | definition, convention, or naming artifact |
| `E1` | executable local check or toy finite-order certificate |
| `E2` | bounded computation with manifest and reproducible input |
| `E3` | cross-check against an independent method |
| `E4` | structured theorem fragment with explicit hypotheses |
| `E5` | proof draft pending adversarial review |
| `E6` | reviewed proof artifact with frozen claim boundary |
| `E7` | speculation, roadmap, analogy, or technique-transfer note |

Promotion must be monotone with respect to evidence: a claim can move upward only when the controller records the gate that changed its status and the artifact digest supporting that movement.

## Failure-wall taxonomy

Every blocked bridge is typed, not glossed. The initial wall vocabulary is:

- `certificate_wall`
- `counting_wall`
- `shell_map_preservation_wall`
- `quotient_wall`
- `preimage_wall`
- `continuum_reconstruction_wall`
- `integer_chern_wall`
- `height_bound_wall`
- `set_theoretic_wall`
- `combinatorial_extremal_wall`

A wall record must name the missing object, the repo that owns the nearest evidence, and the smallest executable gate that would reduce the wall.

## Clay/proof apparatus workspace repos

The initial proof workspace is declared in `manifest/proof-workspace.toml`.

| Repo | Controller role |
|---|---|
| `SocioProphet/bsd-proof-program` | BSD/congruent-number arithmetic engine |
| `SocioProphet/Heller-Godel` | metatheory, incompleteness, proof-boundary engine |
| `SocioProphet/yang-mills` | gauge-theory and mass-gap obstruction engine |
| `SocioProphet/Heller-Winters-Theorem` | SU(2) finite-channel representation-theoretic engine |
| `SocioProphet/hphd-zeta-mirror-lattice` | zeta/RH smoothed-observable and mirror-lattice engine |

## Minimum controller flow

1. Register the proof repos from `manifest/proof-workspace.toml`.
2. Load each repo's proof adapter or fallback repo metadata.
3. Collect declared claims, gates, fixtures, non-claims, and artifact digests.
4. Normalize claims into the proof-apparatus object model.
5. Run repo-local proof tests through policy-mediated workspace execution.
6. Record `EvidenceEvent` and `ArtifactDigest` outputs.
7. Apply cross-validation gates where two or more repos touch the same substrate, shell, projection, or evidence type.
8. Emit a `PromotionDecision` or `PreimageObstruction`.
9. Freeze a `WorkspaceSnapshot`.
10. Publish a human-readable claim-boundary table.

## Cross-validation lanes

The first cross-validation lanes are:

- BSD C5-style arithmetic consistency gates.
- Yang-Mills Gram, symmetry-equality, null-model, and obstruction-wall gates.
- Heller-Winters finite-channel product and Wigner-convention gates.
- Heller-Godel proof-boundary and non-claim gates.
- HPHD zeta/RH smoothed-observable decomposition gates.
- Shared provenance gates: manifest hash, fixture hash, command trace, output digest, and claim-boundary table.

## Non-claim discipline

The controller distinguishes four states that must not be conflated:

- `proved`: claim is within a frozen theorem boundary.
- `checked`: claim has executable support but is not a theorem.
- `diagnosed`: obstruction is typed and localized.
- `speculative`: claim is a roadmap item, analogy, or technique-transfer note.

The default state for new cross-repo synthesis is `diagnosed` or `speculative`, never `proved`.

## Implementation status

This v0 protocol is the control-plane contract. It does not yet implement all runner hooks. The immediate implementation target is a proof adapter that can read repo-local claim/gate manifests, run declared tests, and emit evidence events conforming to the proof apparatus ledger schema.
