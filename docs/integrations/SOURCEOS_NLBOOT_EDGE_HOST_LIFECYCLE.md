# SourceOS / nlboot Edge Host Lifecycle Governance

Status: v0 governance contract
Owner surface: SocioSphere

## Purpose

This document defines the minimum lifecycle information SocioSphere must know before an edge host participates in GAIA, OFIF, MeshRush, Agentplane, Sherlock, or Lattice workflows.

SourceOS and nlboot remain the host lifecycle authorities. KubeEdge is optional and, when selected, runs on top of a governed host.

## Required binding

A governed edge host must bind:

- edge node ID;
- site, fleet, and workspace refs;
- device claim ref;
- host identity ref;
- attestation ref;
- SourceOS release set ref;
- nlboot boot release set ref;
- recovery policy ref;
- rollback plan ref;
- enrollment state;
- validation timestamp;
- policy bundle refs;
- evidence refs;
- optional KubeEdge role/version/topology refs.

## Accepted states

- `planned`
- `enrolled`
- `validated`
- `active`
- `degraded`
- `quarantined`
- `retired`

## Optional KubeEdge fields

When KubeEdge is selected, the binding must include:

- role: `edgecore`, `cloudcore`, or `both`;
- version;
- topology ref;
- autonomy policy ref;
- workload policy ref;
- partition behavior.

## Rejection criteria

Reject host readiness when any required lifecycle field is missing.

Reject optional KubeEdge readiness when KubeEdge is selected but role, version, topology, autonomy policy, or workload policy is missing.

## Non-goals

- Do not make KubeEdge mandatory.
- Do not let KubeEdge replace SourceOS/nlboot lifecycle authority.
- Do not infer Smart Spaces repo placement from this governance binding.
- Do not admit runtime assets to Lattice from host enrollment alone.

## First implementation target

Add a schema, fixture, validator, and CI for an `EdgeHostLifecycleBinding` record.
