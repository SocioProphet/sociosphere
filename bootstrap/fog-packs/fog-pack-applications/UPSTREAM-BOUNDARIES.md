# fog-pack-applications upstream boundaries

This note travels with the `fog-pack-applications` bootstrap seed.

## `fog-pack-applications` owns
- applications pack packaging, BOM, profiles, and release notes for this pack
- starter portals, thin app surfaces, pack-local UI kits, and example applications
- pack-local manifests, overlays, conformance, and packaging
- applications-pack docs and ADRs

## `fog-pack-applications` does not own
- shared outward product/docs/web canon from `SocioProphet/socioprophet`
- shared runtime canon from `SocioProphet/agentplane`
- shared protocol canon from `SocioProphet/TriTRPC`
- cross-pack governance canon from `SocioProphet/sociosphere`

## Import rule
Prefer dependency references, upstream pins, and compatibility notes over copying shared docs/product surface, shared runtime, shared protocol, or cross-pack governance canon into this pack.
