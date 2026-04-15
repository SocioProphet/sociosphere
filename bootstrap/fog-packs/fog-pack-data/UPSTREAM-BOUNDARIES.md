# fog-pack-data upstream boundaries

This note travels with the `fog-pack-data` bootstrap seed.

## `fog-pack-data` owns
- Fog Stack for Data release contract, lock, BOM, profiles
- Fog Base / Lake / Catalog / Knowledge / Trust composition
- pack-local manifests, overlays, conformance, and packaging
- data-pack docs and ADRs

## `fog-pack-data` does not own
- shared workflow/workspace governance canon from `SocioProphet/sociosphere`
- shared runtime envelope / receipt / proof-consumer / durablegraph canon from `SocioProphet/agentplane`
- shared protocol slices, transport methods, and wire fixture canon from `SocioProphet/TriTRPC`

## Import rule
Prefer dependency references, upstream pins, and compatibility notes over copying shared-foundation material into this pack.

## Immediate implication
When `SocioProphet/fog-pack-data` is created, import only the pack-local distro content from this bootstrap subtree.
