# Proof Apparatus Workspace Acceptance (v0)

## Acceptance target

The proof apparatus workspace passes when SocioSphere can coordinate the five proof repositories as a governed proof workspace without taking ownership of domain mathematics, silently promoting claims, losing provenance, or bypassing repo-local tests.

## Gates

### A. Controller ownership

- [ ] SocioSphere contains the canonical proof workspace manifest.
- [ ] Proof repositories are typed as domain engines, not as controller peers.
- [ ] Cross-repo orchestration order is declared outside the domain repos.
- [ ] The controller boundary states that SocioSphere routes, records, and gates claims, but does not manufacture theorem status.

### B. Repo adapter contract

- [ ] Each proof repo can declare `ProofClaim`, `ProofGate`, `ProofTest`, `ClaimBoundary`, and `NonClaim` objects.
- [ ] Missing repo adapters fail closed into `diagnosed` status, not `proved` status.
- [ ] Adapter output includes repo, ref, artifact digest, command, and fixture locator.
- [ ] Adapter output can be replayed from a frozen workspace snapshot.

### C. Evidence ledger

- [ ] Every nontrivial claim update emits an `EvidenceEvent`.
- [ ] Every artifact used in promotion has a digest.
- [ ] Severity levels are restricted to `E0` through `E7`.
- [ ] Promotion records preserve the previous state and reason for change.
- [ ] Demotion and quarantine are first-class outcomes.

### D. Proof tests and checks

- [ ] Repo-local proof tests run through workspace policy.
- [ ] Tests can be grouped into named gates.
- [ ] A failed gate blocks promotion.
- [ ] A skipped gate is visible in the claim-boundary table.
- [ ] Cross-repo gates can consume evidence from more than one proof repo.

### E. Claim-boundary discipline

- [ ] Every output has a claim-boundary table.
- [ ] Every non-claim is explicit.
- [ ] Technique-transfer notes are separated from theorem claims.
- [ ] Settled external mathematical results are marked as references, not targets.
- [ ] Obstruction typing is used when a bridge is missing.

### F. Failure-wall typing

- [ ] Missing certificates are typed as `certificate_wall`.
- [ ] Missing scale/asymptotic estimates are typed as `counting_wall`.
- [ ] Missing projection preservation is typed as `shell_map_preservation_wall`.
- [ ] Missing quotient or descent compatibility is typed as `quotient_wall`.
- [ ] Missing object construction is typed as `preimage_wall`.
- [ ] Missing limit/continuum passage is typed as `continuum_reconstruction_wall`.

### G. EMVI integration

- [ ] Proof claim capture can be represented as a collection item.
- [ ] Proof test execution becomes an `ActionSpec` before running.
- [ ] Output capture preserves command, repo, ref, and fixture context.
- [ ] Workspace snapshots can be exported with proof claim and evidence metadata.
- [ ] Ledger inspection can recover what executed, what was captured, and what was promoted.

## Failure conditions

The proof apparatus workspace fails if any of the following occur:

- SocioSphere becomes a hidden theorem-authoring repo rather than a controller.
- A domain repo's speculative material is promoted without a gate.
- A proof test bypasses workspace policy.
- A claim update has no artifact digest.
- A cross-repo synthesis loses the repo/ref provenance of its inputs.
- A missing bridge is described rhetorically rather than assigned a failure-wall type.
