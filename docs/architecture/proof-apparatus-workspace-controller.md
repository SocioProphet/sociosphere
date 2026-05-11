# Proof Apparatus Workspace Controller

SocioSphere is the workspace controller for SocioProphet proof programs. The proof repositories provide domain evidence; SocioSphere provides orchestration, provenance, cross-validation, promotion control, and failure typing.

## Decision

The five proof repositories are not peer controllers. They are domain engines under a SocioSphere proof workspace.

The controlling files are:

- `manifest/proof-workspace.toml`
- `protocol/proof-apparatus-workspace/v0/README.md`
- `protocol/proof-apparatus-workspace/v0/ACCEPTANCE.md`
- `standards/proof-apparatus/README.md`
- `standards/proof-apparatus/claim-ledger.schema.json`

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

## Clay/problem-tier alignment

The proof workspace records the apparatus reach by tier:

- Tier A: direct object engagement, where the apparatus computes the same kind of object the target uses.
- Tier B: technique-transfer engagement, where the apparatus supplies comparison, projection, regulator, or Selmer-style structure.
- Tier C: cross-validation engagement, where gates and ledgers give useful falsification and promotion discipline.
- Tier D: obstruction-taxonomy engagement, where the output is a typed wall, not a theorem.
- Tier E: methodology-adjacent corridors.
- Tier F: orthogonal problems retained for map completeness only.

The controller must mark these tiers as orchestration metadata. A tier assignment is not a theorem claim.

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
| BSD arithmetic consistency gate | `bsd-proof-program` |
| Heller-Godel proof-boundary gate | `Heller-Godel` |
| Yang-Mills obstruction-wall gate | `yang-mills` |
| Heller-Winters finite-channel gate | `Heller-Winters-Theorem` |
| HPHD smoothed-observable gate | `hphd-zeta-mirror-lattice` |
| cross-repo projection/preimage compatibility gate | SocioSphere controller |

## Non-claim boundary

SocioSphere may state that a repo has evidence, a gate, a diagnostic, a typed obstruction, or a roadmap. It may not state that a Clay problem or major theorem is solved unless the relevant domain repo has a frozen reviewed proof artifact and the controller has recorded the promotion decision with digest, claim boundary, and non-claims.

## Implementation next move

The next implementation unit is a proof adapter contract:

```text
proof-adapter -> ProofClaim[] + ProofGate[] + EvidenceEvent[] + ArtifactDigest[]
```

The adapter can start as a repository-local manifest reader. The runner integration can follow after every proof repo has a minimal manifest.
