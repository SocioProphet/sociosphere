# fog-pack-network-automation upstream boundaries

This note travels with the `fog-pack-network-automation` bootstrap seed.

## `fog-pack-network-automation` owns
- network-automation pack packaging, BOM, profiles, and release notes for this pack
- topology, intents, edge-site automation, and network-policy composition
- pack-local manifests, overlays, conformance, and packaging
- network-automation-pack docs and ADRs

## `fog-pack-network-automation` does not own
- shared cross-pack governance canon from `SocioProphet/sociosphere`
- shared protocol canon from `SocioProphet/TriTRPC`
- generic hybrid-cloud or cluster-registry canon already anchored in existing repos
- shared runtime canon from `SocioProphet/agentplane`

## Import rule
Prefer dependency references, upstream pins, and compatibility notes over copying shared governance, shared protocol, shared runtime, or generic hybrid-cloud canon into this pack.
