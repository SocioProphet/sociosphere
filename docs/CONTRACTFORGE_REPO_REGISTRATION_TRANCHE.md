# ContractForge registration tranche

## Purpose

This document captures the workspace-controller changes required to register `SocioProphet/contractforge` cleanly inside `sociosphere` without increasing existing controller drift.

## Why a tranche is needed

`contractforge` now exists as the canonical repository for contract lifecycle, contractual economics, settlement semantics, adjustments, reversals, restatements, and ledger-anchored finalization.

`Sociosphere` should register it, but several controller cleanup items should be completed in the same discipline lane:

1. normalize manifest identity drift
2. normalize lock completeness
3. normalize canonical registry shape
4. then add `contractforge` as a managed canonical repo

## Intended repo role

- canonical repo id: `contractforge`
- repository full name: `SocioProphet/contractforge`
- primary role: `component`
- status: `active`
- control-plane classification: contract-domain product repo, not workspace controller, not policy repo, not generic standards repo

## Boundary summary

ContractForge should be registered in `sociosphere` as:
- a managed canonical repository,
- governed by workspace policy and topology rules,
- adjacent to `policy-fabric`, `prophet-platform`, and `socioprophet-standards-storage`,
- but not merged into any of those repos.

## Required follow-on file edits

### 1. `registry/canonical-repos.yaml`
- add `contractforge`
- normalize the file so only one registry schema remains authoritative

### 2. `manifest/workspace.toml`
- add `contractforge` as a remote canonical repo entry
- do this only after duplicate/alias drift is cleaned up in the manifest

### 3. `manifest/workspace.lock.json`
- pin `contractforge` once fetched
- continue eliminating `rev: null` for active materialized repos

### 4. `governance/CANONICAL_SOURCES.yaml`
- add contract-domain namespace ownership once the first canonical namespaces are frozen

## Recommended namespace candidates

These are candidates only and should be confirmed before canonization:
- `contracts/core`
- `contracts/lifecycle`
- `contracts/settlement`
- `contracts/adjustment`
- `contracts/commitment`

## Merge policy

This tranche is intentionally documentation-first because the current connector surface is better suited to additive file creation than tracked-file overwrite. The actual manifest/registry edits should follow immediately in the next controller-normalization PR.
