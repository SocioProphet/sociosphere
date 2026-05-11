# Proof Apparatus Workspace Controller

SocioSphere is the workspace controller for SocioProphet proof programs. The proof repositories provide domain evidence; SocioSphere provides orchestration, provenance, cross-validation, promotion control, failure typing, and proof-adjacency ranking metadata.

## Decision

The five proof repositories are not peer controllers. They are domain engines under a SocioSphere proof workspace.

The controlling files are:

- `manifest/proof-workspace.toml`
- `protocol/proof-apparatus-workspace/v0/README.md`
- `protocol/proof-apparatus-workspace/v0/ACCEPTANCE.md`
- `standards/proof-apparatus/README.md`
- `standards/proof-apparatus/claim-ledger.schema.json`
- `standards/proof-apparatus/proof-adapter.schema.json`
- `registry/proof-adjacency-ranking.v0.yaml`

## Architecture

The apparatus is a typed projection/preimage calculus over finite-order data on substrate-graded states, governed by a severity-graded evidence ledger and cross-validation gates.

Operationally, each claim is normalized as:

```text
(substrate, shell_level, projection, evidence)
```

SocioSphere coordinates the lifecycle of that object. The domain repo owns its local proof material; SocioSphere owns its cross-repo state.

## Repo responsibilities

| Repo | Function | Controller posture |
|---|---|---|
| `SocioProphet/bsd-proof-program` | BSD/congruent-number arithmetic engine | run arithmetic gates and emit evidence |
| `SocioProphet/Heller-Godel` | metatheory/proof-boundary engine | enforce non-claim and formal-boundary gates |
| `SocioProphet/yang-mills` | gauge-theory/mass-gap obstruction engine | type bridge failures and run finite-spacing gates |
| `SocioProphet/Heller-Winters-Theorem` | SU(2) finite-channel engine | run representation-theoretic gates |
| `SocioProphet/hphd-zeta-mirror-lattice` | zeta/RH smoothed-observable engine | run analytic-number-theory decomposition gates |

## Proof adjacency taxonomy

The proof workspace now ranks adjacent problem corridors using three positive axes plus two non-positive map axes:

| Axis | Meaning | Controller use |
|---|---|---|
| `object` | Same machinery or same kind of mathematical object. | Mode 1 computation or Mode 3 object-diagnostic. |
| `methodology` | Same problem shape; SocioProphet evidence discipline transfers even when objects differ. | Obstruction typing, non-claim discipline, severity gating, and cross-validation transfer. |
| `outcome` | Same kind of finite-order, torsion, regulator, comparison-isomorphism, or residual phenomenon in another corridor. | Diagnostic or technique-transfer lane, never theorem promotion by itself. |
| `vocabulary` | Similar mathematical vocabulary but no current apparatus reach. | Map/glossary corridor only unless new evidence appears. |
| `none` | No meaningful proof-apparatus adjacency at current scope. | Global map only; no active proof lane. |

The canonical ranking registry is `registry/proof-adjacency-ranking.v0.yaml`. The registry repairs the chat-export math placeholders into explicit terms: `chi_p`, `chi_13`, `mu_2`, `n mod 8`, Deligne level-1 units, Deligne level-2 cup-product symbols, Bockstein carry cocycles, branch-killing cyclic covers, tame symbols, and `Q` for Hilbert's tenth over the rationals.

No ranking entry is a theorem claim. Ranking metadata can only assign controller posture: `scoped`, `diagnosed`, `diagnostic`, `active_parallel_program`, `non_claim`, `technique_template_only`, `methodology_only`, `vocabulary_only`, or `map_only`.

## Clay/problem-tier alignment

The proof workspace records the apparatus reach by tier:

- Tier 1: direct object-level adjacency, computable now or after a named small expansion.
- Tier 2: strong object adjacency with a harder bridge.
- Tier 3: methodology-adjacent Clay-distance programs.
- Tier 4: object-family match with scope mismatch.
- Tier 5: same corridor, different country.
- Tier 6: out of scope for apparatus fallout.

The controller must mark these tiers as orchestration metadata. A tier assignment is not a theorem claim.

## Integrated top-three scoped tasks

The reviewed tranche promotes only the first three ranking entries into scoped work items:

| Rank | Work item | Mode | Owner | Controller posture |
|---:|---|---|---|---|
| 1 | Atiyah-Hirzebruch / Soule-Voisin torsion template | Mode 1 | `Heller-Godel` | scoped |
| 2 | Beilinson regulator on toy families | Mode 1 | `Heller-Godel` | scoped |
| 3 | Tate conjecture for K3-type comparison settings | Mode 2 | `Heller-Godel` | scoped technique-transfer diagnostic |

Yang-Mills and BSD remain active methodology-adjacent programs, not Paper I fallout. RH/GRH, Hodge proper, Tate general, Langlands, Sato-Tate, abc/Szpiro/Vojta, and the Tier 6 clusters are map, diagnostic, non-claim, or vocabulary corridors unless new domain evidence is added.

## Initial expansion queue

The first five expansions are tracked as controller-level workspace work:

1. Moduli-of-proof-classes object.
2. Selmer-character compatibility module.
3. BSD four-descent and higher-descent ladder.
4. Frobenius-trace extension under prime-even gating.
5. Yang-Mills operator-level RG/log-Sobolev module.

Items 1, 2, and 4 are controller-friendly because they mostly require new manifests, schemas, and cross-repo gates. Items 3 and 5 remain domain-heavy and should be orchestrated by SocioSphere but implemented in their domain repos.

## Required cross-repo gates

The first controller-owned gate families are:

| Gate family | Repos |
|---|---|
| claim-boundary and non-claim gate | all proof repos |
| severity-ledger conformance | all proof repos |
| artifact digest and manifest hash gate | all proof repos |
| proof-adjacency ranking conformance | all proof repos touched by ranked work |
| BSD arithmetic consistency gate | `bsd-proof-program` |
| Heller-Godel proof-boundary gate | `Heller-Godel` |
| Yang-Mills obstruction-wall gate | `yang-mills` |
| Heller-Winters finite-channel gate | `Heller-Winters-Theorem` |
| HPHD smoothed-observable gate | `hphd-zeta-mirror-lattice` |
| cross-repo projection/preimage compatibility gate | SocioSphere controller |

## Non-claim boundary

SocioSphere may state that a repo has evidence, a gate, a diagnostic, a typed obstruction, or a roadmap. It may not state that a Clay problem or major theorem is solved unless the relevant domain repo has a frozen reviewed proof artifact and the controller has recorded the promotion decision with digest, claim boundary, and non-claims.

## Implementation next move

The next implementation unit is strict proof workspace materialization:

```text
proof workspace manifest -> materialized proof repos -> strict adapter validation -> claim-boundary table -> claim-ledger events -> cross-repo gate execution
```

The proof-adjacency tranche is no longer merely queued. It has been integrated into controller doctrine and converted into scoped top-three work items.
