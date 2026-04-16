# Software Operational Risk Registry Lane

This directory is the normalized landing zone for software operational risk harvesters and watchlist outputs.

## Purpose

The first goal of this lane is simple:

1. collect official outage-history and upstream-state signals,
2. normalize them into typed, machine-readable records,
3. preserve them in a registry path that other governance, topology, and trust-reporting lanes can consume.

## Initial outputs

- `status_sources.yaml` — named provider and status-history source registry
- `outage_corpus.seed.jsonl` — illustrative normalized incident records
- `upstream_watch.seed.jsonl` — illustrative normalized watchlist records

## Contract alignment

The normalized objects in this lane are intended to align with the software operational risk schema work proposed in:

- `SourceOS-Linux/sourceos-spec` PR #24 — `SoftwareOperationalIncident` and `UpstreamWatchItem`
- `SocioProphet/socioprophet-standards-storage` PR #72 — normative governance framework and outage corpus method

## Planned integration

This lane is expected to feed:

- workspace trust reports,
- dependency / topology reasoning,
- concentration and upstream-drift KRIs,
- and later financial modeling / reserve dashboards.
