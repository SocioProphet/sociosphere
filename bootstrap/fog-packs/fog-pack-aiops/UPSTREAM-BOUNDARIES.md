# fog-pack-aiops upstream boundaries

This note travels with the `fog-pack-aiops` bootstrap seed.

## `fog-pack-aiops` owns
- aiops pack packaging, BOM, profiles, and release notes for this pack
- telemetry, incidents, alerts, runbooks, and ops-graph composition
- pack-local manifests, overlays, conformance, and packaging
- aiops-pack docs and ADRs

## `fog-pack-aiops` does not own
- shared runtime envelope / receipt / proof-consumer / durablegraph canon from `SocioProphet/agentplane`
- shared workspace/workflow governance canon from `SocioProphet/sociosphere`
- shared telemetry foundation already anchored in `SocioProphet/prom-system`
- shared protocol slices, transport methods, and wire fixtures from `SocioProphet/TriTRPC`

## Import rule
Prefer dependency references, upstream pins, and compatibility notes over copying shared runtime, shared telemetry, shared protocol, or shared workspace canon into this pack.
