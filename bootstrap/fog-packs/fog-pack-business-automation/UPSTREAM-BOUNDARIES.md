# fog-pack-business-automation upstream boundaries

This note travels with the `fog-pack-business-automation` bootstrap seed.

## `fog-pack-business-automation` owns
- business automation pack packaging, BOM, profiles, and release notes for this pack
- workflow, case, decisioning, HITL, approval queues, and document-action composition
- pack-local manifests, overlays, conformance, and packaging
- automation-pack docs and ADRs

## `fog-pack-business-automation` does not own
- shared runtime envelope / receipt / proof-consumer / durablegraph canon from `SocioProphet/agentplane`
- shared protocol slices, transport methods, and wire fixtures from `SocioProphet/TriTRPC`
- shared workflow/workspace governance canon from `SocioProphet/sociosphere`

## Import rule
Prefer dependency references, upstream pins, and compatibility notes over copying shared runtime, shared protocol, or shared workspace canon into this pack.
