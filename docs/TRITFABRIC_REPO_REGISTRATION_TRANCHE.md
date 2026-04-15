# TritFabric registration tranche

## Purpose

This document captures the workspace-controller changes required to register `SocioProphet/tritfabric` cleanly inside `sociosphere` without increasing existing controller drift.

## Why a tranche is needed

`tritfabric` now exists as the canonical consolidated fabric repo for Atlas runtime work, protocol-first gates, and cross-boundary integration planning.

`Sociosphere` should register it, but the controller should do that in a disciplined order:

1. pin intended repo identity and boundary
2. add the remote canonical repo entry in `manifest/workspace.toml`
3. refresh `manifest/workspace.lock.json`
4. update `registry/canonical-repos.yaml`
5. update `governance/CANONICAL_SOURCES.yaml` where namespace ownership becomes explicit

## Intended repo role

- canonical repo id: `tritfabric`
- repository full name: `SocioProphet/tritfabric`
- primary role: `component`
- status: `active`
- control-plane classification: consolidated fabric repo; not workspace controller; not generic standards canon; not final runtime-only distro repo

## Boundary summary

TritFabric should be registered in `sociosphere` as:
- a managed canonical repository,
- governed by workspace policy and topology rules,
- adjacent to `tritrpc`, `agentplane`, `prophet-platform`, and standards repos,
- with downstream runtime exports flowing into `socios` / SourceOS-facing lanes.

## Required follow-on file edits

### 1. `manifest/workspace.toml`
- add `tritfabric` as a remote canonical repo entry
- choose local materialization only after the workspace controller decides the correct lane (`components/` vs remote-only)

### 2. `manifest/workspace.lock.json`
- pin `tritfabric` once fetched
- ensure the lock records the commit used for workspace validation

### 3. `registry/canonical-repos.yaml`
- add `tritfabric`
- classify it as the canonical consolidated fabric repo in the SocioProphet lane

### 4. `governance/CANONICAL_SOURCES.yaml`
- add namespace ownership once the relevant protocol / fabric namespaces are frozen

## Merge policy

This tranche is intentionally documentation-first because the current connector surface is better suited to additive file creation than tracked-file overwrite. The actual manifest/lock/registry edits should follow immediately in the next controller-normalization PR or direct repo-native patch application.
