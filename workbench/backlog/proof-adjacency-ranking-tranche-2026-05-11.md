# Proof Adjacency Ranking Tranche — Integrated

Status: integrated into SocioSphere controller doctrine
Controller: SocioSphere
Date captured: 2026-05-11
Date integrated: 2026-05-11
Review issue: `SocioProphet/sociosphere#318`
Controller registry: `registry/proof-adjacency-ranking.v0.yaml`

## Purpose

This tranche reworks the ranking of adjacent Clay/math/proof-problem corridors against the actual SocioProphet proof apparatus.

The key correction is that adjacency is not only object-level adjacency. The corpus also has a strong methodological signature: image/preimage discipline, shell taxonomy, evidence-object framing, severity grading, claim-boundary CI guards, and explicit non-claim boxes. That methodological signature transfers to several active or adjacent proof corridors even when the underlying mathematical objects differ.

This tranche has been reviewed and integrated into SocioSphere controller doctrine. Lower-level runner/materialization work has resumed through the proof workspace materializer, strict adapter validator, controller gate runner, and controller output generator.

## Review result

The source tranche contained unresolved math-render placeholders from chat export. The integrated registry repairs them into explicit controller terms:

- `chi_p` finite phase characters;
- `chi_13` finite phase character;
- `mu_2` triple-point setup;
- `n mod 8` BSD root-number datum;
- Deligne level-1 unit;
- Deligne level-2 cup-product symbol;
- Bockstein carry cocycle;
- branch-killing cyclic cover;
- tame symbol;
- `Q` for Hilbert's tenth over the rationals.

No item in this tranche is a theorem claim. Default controller state remains `diagnosed` or `speculative` unless a domain repo emits gated evidence and SocioSphere records a promotion decision.

## Three adjacency axes

| Axis | Meaning | Examples |
|---|---|---|
| Object-adjacent | Same machinery or same kind of mathematical object | Beilinson, Tate, Soulé–Voisin |
| Methodology-adjacent | Same problem shape; SocioProphet discipline transfers even when objects differ | Yang–Mills, BSD, RH, abc/Szpiro/Vojta |
| Outcome-adjacent | Same kind of finite-order, torsion, comparison-isomorphism, or regulator phenomenon in another corridor | Some L-function and Galois-representation conjectures |

The canonical machine-readable form is `registry/proof-adjacency-ranking.v0.yaml`.

## What changed from the prior pass

1. Soulé–Voisin / Atiyah–Hirzebruch torsion moved to rank 1 because it is more directly attached to the existing torsion-shadow objects than Beilinson regulator work.
2. Tate for K3 is separated from Tate proper. K3 is settled, but the comparison-isomorphism technique remains highly relevant as a technique-transfer object.
3. Methodology-adjacent problems are explicitly tiered instead of dismissed. Yang–Mills, BSD, RH, and abc-family problems are not Paper I fallout, but they share the proof-apparatus discipline.

## Tier 1 — Direct object-level adjacency, computable now

### 1. Atiyah–Hirzebruch torsion / Soulé–Voisin template

Adjacency: object.

Concrete fallout: test whether chain, Catalan, and Motzkin Deligne classes produce torsion examples with structural features distinguishing them from the standard Atiyah–Hirzebruch construction.

Mode: Mode 1.

Integrated work item: `SocioProphet/Heller-Godel#19`.

### 2. Beilinson regulator on toy families

Adjacency: object.

Concrete fallout: compute regulator output for the level-2 Deligne cup product on toy families. Check for period structure, L-value adjacency, or irrationality witness as diagnostics only.

Mode: Mode 1.

Integrated work item: `SocioProphet/Heller-Godel#20`.

### 3. Tate conjecture for K3-type comparison settings

Adjacency: object + methodology.

Concrete fallout: compare the K3 comparison-isomorphism template against the SocioProphet `mu_2` triple-point setup. This is a technique-transfer diagnostic, not an attempt to reopen the settled K3 Tate case.

Mode: Mode 2.

Integrated work item: `SocioProphet/Heller-Godel#21`.

## Tier 2 — Strong object adjacency, harder bridge

### 4. Finite-level Mumford–Tate

Adjacency: object.

Concrete fallout: examine whether finite-character products satisfy constraints resembling finite-level Mumford–Tate reductions.

Expected output: likely negative or diagnostic.

### 5. Bloch–Kato Selmer-group structure

Adjacency: object.

Concrete fallout: diagnose the missing arithmetic-Galois structure required for Tamagawa, Selmer, and regulator compatibility.

Mode: Mode 3.

### 6. Fontaine–Mazur

Adjacency: object at finite level.

Concrete fallout: diagnose which residual-representation data would be needed for characteristic-zero p-adic lifts.

Mode: Mode 3.

### 7. Bloch–Beilinson filtration

Adjacency: object by language.

Concrete fallout: confirm that the current apparatus supplies analytic-side infrastructure but no Chow input.

Mode: Mode 3.

## Tier 3 — Methodology-adjacent Clay-distance programs

### 8. Yang–Mills mass gap

Adjacency: methodology.

Concrete fallout: continue theorem track, obstruction survey, claim-boundary CI, and severity grading. The active deliverable is the v0.18.1 audit/integration corridor.

Controller status: active parallel program, not Paper I fallout.

### 9. BSD

Adjacency: methodology.

Concrete fallout: continue SocioProphet BSD program under the same severity, evidence, and non-claim discipline. Possible diagnostic connection to finite-order comparison structures, but no direct Paper I object fallout is assumed.

Controller status: active parallel program, not Paper I fallout.

### 10. RH / GRH / automorphic L-function RH

Adjacency: methodology.

Concrete fallout: diagnostic only. Ask whether finite-level or comparison-isomorphism toolkit produces constraints on zeros of L-functions attached to regulator outputs. Expected result is likely trivial.

## Tier 4 — Object family match, scope mismatch

| Rank | Problem | Controller posture |
|---|---|---|
| 11 | Generalized Hodge conjecture | Object-adjacent by language, but not productive because the apparatus does not produce algebraic-cycle input. |
| 12 | Standard conjectures on algebraic cycles | Same scope issue. |
| 13 | Grothendieck period conjecture | Regulator outputs are period-adjacent; check specific Catalan/chain regulator values only after regulator pipeline exists. |
| 14 | Tate–Shafarevich finiteness | Connects to BSD program, not directly to Paper I objects. |
| 15 | Parity conjecture | Connects to BSD program, not directly to Paper I. |

## Tier 5 — Same corridor, different country

| Rank | Problem | Controller posture |
|---|---|---|
| 16 | Tate conjecture general | Technique-template adjacency only. |
| 17 | Hodge conjecture proper | Explicitly non-claimed; Paper I sits adjacent. |
| 18 | abc / Szpiro / Vojta | Methodology transfers; apparatus does not. |
| 19 | Langlands functoriality | Vocabulary adjacency; finite-level pieces only. |
| 20 | Sato–Tate generalizations | Vocabulary/statistical adjacency; finite-level pieces only. |

## Tier 6 — Out of scope for fallout

| Rank | Problem cluster | Reason |
|---|---|---|
| 21 | Goldbach / twin prime / k-tuples / Bateman–Horn / Schinzel | Additive number theory; different corridor. |
| 22 | Hilbert's tenth over Q / decidability | Logic/Diophantine; different corridor. |
| 23 | Jacobian conjecture / Zariski cancellation | Affine algebraic geometry; different corridor. |
| 24 | Smooth 4D Poincaré / Schoenflies | 4-manifold topology; different corridor. |
| 25 | Hadwiger / Erdős–Hajnal / union-closed / Frankl | Combinatorics; different corridor. |

## Complete ranked table

| Rank | Problem | Adjacency type | Fallout meaning |
|---:|---|---|---|
| 1 | Atiyah–Hirzebruch / Soulé–Voisin torsion | Object | New torsion examples from chain/Catalan/Motzkin Deligne classes |
| 2 | Beilinson regulator | Object | Regulator output on toy families; check L-value/period structure |
| 3 | Tate conjecture for K3-type comparison settings | Object + Method | Map K3 comparison-isomorphism template against `mu_2` triple-point setup |
| 4 | Finite-level Mumford–Tate | Object | Examine constraints on finite-character products |
| 5 | Bloch–Kato Selmer structure | Object | Structural diagnosis of missing arithmetic input |
| 6 | Fontaine–Mazur lifting | Object | Finite-level residual representation diagnosis |
| 7 | Bloch–Beilinson filtration | Object | Diagnostic: missing Chow input |
| 8 | Yang–Mills mass gap | Method | Parallel corridor; v0.18.1 audit/integration |
| 9 | BSD | Method | Parallel corridor; active repo program |
| 10 | RH / GRH / automorphic L-RH | Method | Diagnostic constraints on L-zeros from regulator outputs, likely trivial |
| 11 | Generalized Hodge conjecture | Object, harder than Hodge | Not productive direction |
| 12 | Standard conjectures on algebraic cycles | Object | Not productive direction |
| 13 | Grothendieck period conjecture | Object | Transcendence/period diagnostics for regulator values |
| 14 | Tate–Shafarevich finiteness | Arithmetic object-side | BSD connection |
| 15 | Parity conjecture | Arithmetic object-side | BSD connection |
| 16 | Tate conjecture general | Object | Technique-template adjacency only |
| 17 | Hodge conjecture proper | Object | Explicit non-claim; adjacent corridor |
| 18 | abc / Szpiro / Vojta | Method only | Discipline transfers; apparatus does not |
| 19 | Langlands functoriality | Vocabulary | Finite-level pieces only |
| 20 | Sato–Tate generalizations | Vocabulary | Finite-level statistical pieces |
| 21 | Goldbach / twin prime / k-tuples cluster | None | Different corridor |
| 22 | Hilbert's tenth over Q | None | Different corridor |
| 23 | Jacobian conjecture / Zariski cancellation | None | Different corridor |
| 24 | Smooth 4D Poincaré / Schoenflies | None | Different corridor |
| 25 | Hadwiger / Erdős–Hajnal / union-closed | None | Different corridor |

## Integration result

The original integration order is complete:

1. Math placeholders repaired in canonical registry.
2. Adjacency axes converted into SocioSphere proof-apparatus metadata.
3. Claim-boundary/non-claim records added for the ranked items that touch active repos through `Heller-Godel/proof-adapter.json`.
4. Mode 1/2 scoped work items created for ranks 1–3.
5. Runner/materialization work resumed through SocioSphere scripts and CI.

## Post-review implementation now resumed

The former post-review backlog is no longer blocked. The implementation surface now includes:

- `tools/materialize_proof_workspace.py` for materializing proof repos from `manifest/proof-workspace.toml`;
- `tools/validate_proof_apparatus.py --strict-adapters` for strict adapter validation;
- `tools/generate_proof_workspace_outputs.py` for claim-boundary table and claim-ledger events;
- `tools/run_proof_workspace_gates.py` for controller gate execution;
- `.github/workflows/proof-apparatus.yml` for CI wiring.
