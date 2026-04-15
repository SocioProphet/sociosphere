# Prophet Platform Fabric MLOps TS Suite registration tranche

## Purpose

This document captures the workspace-controller changes required to register `SocioProphet/prophet-platform-fabric-mlops-ts-suite` cleanly inside `sociosphere` without increasing controller drift or collapsing its boundary with `tritfabric`.

## Why a tranche is needed

`prophet-platform-fabric-mlops-ts-suite` now exists as an active deployment/baseline repo for the Prophet Platform fabric lane, covering multi-cluster Kubernetes fabric, optional MLOps add-ons, and time-series suite delivery.

`Sociosphere` should register it, but should do so in a disciplined order:

1. pin intended identity and boundary
2. add the remote canonical repo entry in `manifest/workspace.toml`
3. refresh `manifest/workspace.lock.json`
4. update `registry/canonical-repos.yaml`
5. update `governance/CANONICAL_SOURCES.yaml` where namespace ownership becomes explicit

## Intended repo role

- canonical repo id: `prophet_platform_fabric_mlops_ts_suite`
- repository full name: `SocioProphet/prophet-platform-fabric-mlops-ts-suite`
- primary role: `component`
- status: `active`
- control-plane classification: platform fabric / MLOps / time-series suite repo; not workspace controller; not generic standards canon; not replacement for `tritfabric`

## Boundary summary

This repository should be registered in `sociosphere` as:
- a managed canonical repository,
- governed by workspace policy and topology rules,
- adjacent to `tritfabric`, `prophet-platform`, `tritrpc`, and standards repos,
- carrying deployable cluster fabric baselines and MLOps/time-series suite material,
- while constitutional fabric/bridge semantics remain anchored in `tritfabric`.

## Required follow-on file edits

### 1. `manifest/workspace.toml`
- add `prophet-platform-fabric-mlops-ts-suite` as a remote canonical repo entry
- choose local materialization only after the workspace controller decides the correct lane (`components/` vs remote-only)

### 2. `manifest/workspace.lock.json`
- pin `prophet-platform-fabric-mlops-ts-suite` once fetched
- ensure the lock records the commit used for workspace validation

### 3. `registry/canonical-repos.yaml`
- add `prophet-platform-fabric-mlops-ts-suite`
- classify it as the Prophet Platform deployment / MLOps / time-series suite lane

### 4. `governance/CANONICAL_SOURCES.yaml`
- add namespace ownership once the relevant deployment profile, suite, and fabric namespaces are frozen

## Merge policy

This tranche is intentionally documentation-first because the current connector surface is better suited to additive file creation than tracked-file overwrite. The actual manifest/lock/registry edits should follow immediately in the next controller-normalization PR or direct repo-native patch application.
