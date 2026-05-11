# Proof Apparatus Standard

This standard defines the governed object model for proof programs that use typed projection/preimage calculus over finite-order data on substrate-graded states.

The standard exists so SocioSphere can orchestrate proof tests, evidence capture, cross-validation, and claim promotion across multiple mathematics repositories without collapsing their different domains into one undifferentiated proof narrative.

## Files

| File | Purpose |
|---|---|
| `README.md` | Human-readable proof apparatus standard |
| `claim-ledger.schema.json` | Controller-side evidence, promotion, obstruction, and snapshot event schema |
| `proof-adapter.schema.json` | Domain-repository manifest schema for exposing claims, gates, non-claims, and obstruction walls to SocioSphere |

## Apparatus shape

A proof apparatus record has four primary coordinates:

```text
(substrate, shell_level, projection, evidence)
```

The coordinates mean:

- `substrate`: the mathematical or computational ground where the object lives.
- `shell_level`: the level of coarse/fine structure being observed.
- `projection`: the map from a richer object to a finite, typed, or computable shadow.
- `evidence`: the artifact, computation, theorem fragment, or review state that supports the current claim.

Finite-order data are allowed to be evidence. They are not automatically allowed to be preimages. The standard requires explicit bridge records for every attempted lift from finite-order data to a richer object.

## Claim lifecycle

The standard uses these claim states:

| State | Meaning |
|---|---|
| `draft` | claim exists but has no executable evidence |
| `checked` | claim passed a local gate |
| `cross_checked` | claim passed at least one independent or cross-repo gate |
| `diagnosed` | claim is blocked by a typed obstruction |
| `quarantined` | claim conflicts with a gate or provenance rule |
| `promoted` | claim moved upward under a recorded promotion decision |
| `archived` | claim is retained for provenance but no longer active |

## Required claim fields

A claim record must include:

- stable claim id
- repository owner/name
- domain
- substrate
- shell level
- projection type
- evidence severity
- claim statement
- claim boundary
- non-claims
- proof gates
- artifact digests
- obstruction walls
- promotion history

## Required gate fields

A gate record must include:

- stable gate id
- owning repo
- command or check description
- fixtures
- expected output
- pass/fail/skip status
- digest of inputs
- digest of outputs
- policy outcome
- timestamp or snapshot id
- severity movement, if any

## Required output discipline

Every proof-facing output must include:

1. What is claimed.
2. What is not claimed.
3. Which repo owns the local evidence.
4. Which SocioSphere gate recorded the state.
5. Which artifact digests support the state.
6. Which failure wall blocks the next bridge, if blocked.
7. Whether the output is theorem, computation, diagnosis, or roadmap.

## Promotion rule

No claim may be promoted by prose alone. Promotion requires:

- a named gate,
- a prior state,
- a new state,
- a concrete artifact digest,
- a severity delta,
- a claim-boundary update,
- and a controller-visible promotion decision.

## Relationship to QES

QES supplies event, run, and evidence discipline for reproducible evaluation pipelines. The proof apparatus standard specializes that discipline for mathematical proof programs by adding claim boundaries, non-claims, projection/preimage typing, failure-wall vocabulary, and theorem-promotion rules.
