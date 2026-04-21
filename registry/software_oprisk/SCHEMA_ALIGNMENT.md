# Schema Alignment

This note documents how the normalized registry outputs in `registry/software_oprisk/` align to the typed contract lane.

## Current typed contracts

The current machine-readable contract surfaces live in `SourceOS-Linux/sourceos-spec` and now include:

- `SoftwareOperationalIncident`
- `UpstreamWatchItem`
- `ReserveScenarioReport`

## Registry output mapping

### `outage_corpus*.jsonl`
Each record SHOULD align to `SoftwareOperationalIncident`.

### `upstream_watch*.jsonl`
Each record SHOULD align to `UpstreamWatchItem`.

### future reserve outputs
Any reserve, scenario, or avoided-loss outputs SHOULD align to `ReserveScenarioReport` or a successor contract in the same family.

## Current validation posture

The first validation layer in this repository is intentionally lightweight.
It checks:

- required keys by normalized record type;
- URN-prefix discipline;
- minimum list-shape expectations for `sourceRefs` and `signals`.

Full schema validation remains a follow-on step and SHOULD eventually bind directly to the canonical typed contract artifacts in `SourceOS-Linux/sourceos-spec`.
