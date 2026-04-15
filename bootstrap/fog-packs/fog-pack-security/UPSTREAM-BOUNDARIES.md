# fog-pack-security upstream boundaries

This note travels with the `fog-pack-security` bootstrap seed.

## `fog-pack-security` owns
- security pack packaging, BOM, profiles, and release notes for this pack
- detections, response, evidence, break-glass, and identity-enforcement composition
- pack-local manifests, overlays, conformance, and packaging
- security-pack docs and ADRs

## `fog-pack-security` does not own
- shared cross-pack governance canon from `SocioProphet/sociosphere`
- shared protocol canon from `SocioProphet/TriTRPC`
- generic cert / secret / trust primitive canon already anchored in existing repos
- shared runtime canon from `SocioProphet/agentplane`

## Import rule
Prefer dependency references, upstream pins, and compatibility notes over copying shared governance, shared protocol, shared runtime, or generic trust/cert primitive canon into this pack.
