# Prophet Platform Fabric MLOps TS Suite repo metadata

## Canonical identity

- repo id: `prophet_platform_fabric_mlops_ts_suite`
- repository full name: `SocioProphet/prophet-platform-fabric-mlops-ts-suite`
- url: `https://github.com/SocioProphet/prophet-platform-fabric-mlops-ts-suite`
- intended role: `component`
- intended layer: `platform fabric / mlops / time-series deployment suite`
- status: `active`

## Summary

This repository is the multi-cluster Prophet Platform fabric baseline for Kubernetes deployment, optional MLOps add-ons, Ray/KubeRay-aligned model operations, and time-series suite profiles.

## Adjacent repositories

- `sociosphere`
- `tritfabric`
- `prophet-platform`
- `tritrpc`
- `agentplane`
- `prophet-platform-standards`
- `socioprophet-standards-storage`

## Boundary distinction

This repo is not the same thing as `tritfabric`.

- `tritfabric` is the consolidated working tree for Atlas runtime, protocol-first gates, and cross-boundary integration planning.
- `prophet-platform-fabric-mlops-ts-suite` is the Prophet Platform deployment and MLOps suite lane for multi-cluster fabric baselines, optional serving stacks, and time-series pack delivery.

## Forbidden responsibilities

This repository should not be used as:

- the workspace controller
- the canonical generic standards registry
- the canonical protocol surface replacing `tritrpc`
- the sole constitutional home for fabric / bridge semantics already captured in `tritfabric`

## Registration note

This document exists to pin the intended metadata before the corresponding updates land in:

- `registry/canonical-repos.yaml`
- `manifest/workspace.toml`
- `manifest/workspace.lock.json`
- `governance/CANONICAL_SOURCES.yaml`
