# Prophet Platform Fabric MLOps TS Suite registration tranche

## Purpose

This document captures the workspace-controller changes required to register `SocioProphet/prophet-platform-fabric-mlops-ts-suite` cleanly inside `sociosphere` without increasing controller drift or collapsing its role into `tritfabric`.

## Why a tranche is needed

`prophet-platform-fabric-mlops-ts-suite` now exists as an active Prophet Platform deployment suite for:

- multi-cluster Kubernetes fabric baselines
- optional MLOps ecosystem add-ons
- Ray/KubeRay-aligned training + serving workflows
- time-series model family packaging and workflow templates

`Sociosphere` should register it, but the controller should do that with explicit role separation:

1. pin intended repo identity and boundary
2. register it as a managed canonical repository in the workspace manifest
3. refresh the workspace lock
4. update canonical registry metadata
5. update namespace ownership where needed

## Intended repo role

- canonical repo id: `prophet_platform_fabric_mlops_ts_suite`
- repository full name: `SocioProphet/prophet-platform-fabric-mlops-ts-suite`
- primary role: `component`
- status: `active`
- control-plane classification: platform fabric / mlops / time-series suite repo

## Reconciliation rule with TritFabric

These repos are adjacent but not duplicates:

- `tritfabric` remains the consolidated fabric / bridge / runtime-and-governance working tree.
- `prophet-platform-fabric-mlops-ts-suite` is the deployable Prophet Platform fabric + MLOps suite lane.

The workspace controller should therefore register both and preserve the distinction.

## Required follow-on file edits

### 1. `manifest/workspace.toml`
- add `prophet_platform_fabric_mlops_ts_suite` as a remote canonical repo entry
- choose local materialization only after the workspace controller decides whether the suite should live under `components/` or remain remote-only by default

### 2. `manifest/workspace.lock.json`
- pin `prophet-platform-fabric-mlops-ts-suite` once fetched
- ensure the lock records the exact revision used for workspace validation

### 3. `registry/canonical-repos.yaml`
- add `prophet-platform-fabric-mlops-ts-suite`
- classify it distinctly from `tritfabric`

### 4. `governance/CANONICAL_SOURCES.yaml`
- add namespace ownership once the relevant platform fabric / mlops / time-series namespaces are frozen

## Merge policy

This tranche is intentionally documentation-first because the current connector surface is better suited to additive file creation than tracked-file overwrite. The actual manifest/lock/registry edits should follow in the next controller-normalization PR or direct repo-native patch application.
