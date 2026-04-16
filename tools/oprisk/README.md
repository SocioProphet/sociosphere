# Software Operational Risk Tools

This directory contains the first automation helpers for the software operational risk lane.

## Current files

- `harvest_status_history.py` — normalize JSON payloads from official status-history surfaces into incident JSONL
- `record_shapes.py` — shared required-key and URN-prefix metadata for normalized record types

## Initial usage

```bash
python tools/oprisk/harvest_status_history.py openai \
  --input /path/to/openai-status-history.json \
  --output registry/software_oprisk/outage_corpus.seed.jsonl
```

## Output expectations

Normalized outputs are intended to align with the typed contracts proposed in:

- `SourceOS-Linux/sourceos-spec` PR #24 (`SoftwareOperationalIncident`, `UpstreamWatchItem`)
- `SocioProphet/socioprophet-standards-storage` PR #72 (normative governance pack)

## Next implementation steps

1. Add provider-specific fetchers and adapters.  
2. Add explicit validation against the typed schema artifacts.  
3. Feed normalized outputs into trust reports, topology reasoning, and upstream-drift KRIs.
