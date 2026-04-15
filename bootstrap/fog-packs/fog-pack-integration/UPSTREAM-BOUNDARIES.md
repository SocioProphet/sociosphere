# fog-pack-integration upstream boundaries

This note travels with the `fog-pack-integration` bootstrap seed.

## `fog-pack-integration` owns
- Fog integration packaging, BOM, profiles, and release notes for this pack
- connectors, APIs, events, CDC, transfers, and MCP/HTTP bridge composition
- pack-local manifests, overlays, conformance, and packaging
- integration-pack docs and ADRs

## `fog-pack-integration` does not own
- shared protocol slices, transport methods, and wire fixtures from `SocioProphet/TriTRPC`
- shared workflow/workspace governance canon from `SocioProphet/sociosphere`
- shared agent runtime canon from `SocioProphet/agentplane`
- generic API contract canon already owned in `SocioProphet/api-spec`
- service-broker canon already owned in `SocioProphet/servicebroker`

## Import rule
Prefer dependency references, upstream pins, and compatibility notes over copying shared-foundation or shared-contract material into this pack.
