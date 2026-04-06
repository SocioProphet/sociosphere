# MERGE-ORDER.md — Safe merge order for pending SocioProphet PRs
# Generated: 2026-04-06
# This document defines the dependency-safe merge sequence for all open draft PRs.
# Reference: status/pr-register.yaml and registry/dependency-graph.yaml

## Guiding Principles

1. **Standards before implementation** — ADRs and standards must land before code that implements them.
2. **Schemas before consumers** — Shared schema definitions before anything that reads/writes them.
3. **Specs before fixtures** — Protocol specs before reference fixtures.
4. **No cascading conflicts** — Each PR in a cluster must target the previous one's merged result, not `main`.

---

## Pre-wave Refresh Checklist

Run this checklist **before each wave** (Wave 1, Wave 2, etc.) to avoid stale sequencing and moving-branch conflicts.

1. Refresh `status/pr-register.yaml` from live repository and PR state (open/closed, draft/ready, mergeability) immediately before wave planning/execution.
2. Stamp a new `metadata.snapshot_date` in the register and recompute summary counters, including `total_open_prs`, `ready_to_merge`, `needs_review`, and any other derived status totals used by merge planning.
3. Declare a temporary per-wave freeze window: no retargeting, rebasing, or base-branch motion outside the designated wave integrator until the wave is completed or explicitly aborted.
4. Execute wave merges only against the refreshed snapshot commit hash recorded in `status/ecosystem-status.yaml`; if the hash differs from the active working state, refresh first and restart wave preparation.
5. Abort wave start when the snapshot is stale: if snapshot age exceeds 24 hours from `metadata.snapshot_date`, stop and refresh status artifacts before any merge actions.

---

## Wave 1 — Immediate (no blockers, no conflicts)

These PRs are non-draft, non-conflicting, and safe to merge right now.

| # | Repo | PR | Title |
|---|------|----|-------|
| 1 | `socioprophet-standards-knowledge` | #16 | Docs: root README |
| 2 | `socioprophet-standards-knowledge` | #17 | Docs: docs/standards README |
| 3 | `socioprophet-standards-knowledge` | #18 | Docs: schemas README |
| 4 | `socioprophet-standards-knowledge` | #19 | Docs: schemas/avro README |
| 5 | `socioprophet-standards-knowledge` | #20 | Docs: schemas/jsonld README |
| 6 | `socioprophet-standards-knowledge` | #21 | Docs: schemas/jsonschema README |
| 7 | `mcp-a2a-zero-trust` | #1 | Issue standards: DoD + Acceptance |
| 8 | `socioprophet` | #223 | docs: ignore vitepress dist/cache |
| 9 | `socioprophet` | #253 | CodeQL + gitleaks security workflows |

---

## Wave 2 — After review quorum (promote from draft, then merge)

| # | Repo | PR | Title | Prerequisite |
|---|------|----|-------|-------------|
| 1 | `prophet-platform-standards` | #1 | Complete DevSecOps/CI/CD/Observability standards | none |
| 2 | `sociosphere` | this branch | Consolidated registry + compliance tooling | none |
| 3 | `sociosphere` | #19 | Workspace OS/agent-plane boundary doc | Review with socioprophet#257 |
| 4 | `socioprophet` | #257 | liberty-by-design doctrine | Review with sociosphere#19 |

After wave 2 lands, close sociosphere PRs #20, #21, #23 as superseded by the consolidated registry.

---

## Wave 3 — Standards-storage FIPS cluster (triage first)

**Action required before any FIPS PR can merge**:
1. Rebase each FIPS PR onto the previous one in the chain (not onto `main` independently).
2. The correct chain is: `main` → #14 → #15 → #16 → #18 → #19 → #17 → #20 → #21 → #22 → #23.

| # | Repo | PR | Title | Base |
|---|------|----|-------|------|
| 1 | `socioprophet-standards-storage` | #14 | FIPS authority docs | `main` |
| 2 | `socioprophet-standards-storage` | #15 | Data layer FIPS | `#14` branch |
| 3 | `socioprophet-standards-storage` | #16 | Orchestration layer FIPS | `#15` branch |
| 4 | `socioprophet-standards-storage` | #18 | P2P/Distributed FIPS | `#16` branch |
| 5 | `socioprophet-standards-storage` | #19 | ML/AI FIPS | `#18` branch |
| 6 | `socioprophet-standards-storage` | #17 | FIPS cross-link | `#19` branch |
| 7 | `socioprophet-standards-storage` | #20 | Semantic layer FIPS | `#17` branch |
| 8 | `socioprophet-standards-storage` | #21 | FIPS governance docs | `#20` branch |
| 9 | `socioprophet-standards-storage` | #22 | FIPS activation rollout | `#21` branch |
| 10 | `socioprophet-standards-storage` | #23 | FIPS Week 1 activation plan | `#22` branch |

Also in wave 3:
- `socioprophet-standards-storage` #5 (ADR-040 twin economy) — standalone, merge after #14
- `socioprophet-standards-storage` #13 (shared schemas) — prerequisite for Wave 4

---

## Wave 4 — Slice work (depends on Wave 3 #13)

| # | Repo | PR | Title | Prerequisite |
|---|------|----|-------|-------------|
| 1 | `agentplane` | #11 | AOKC order-to-bundle bridge | Wave 3 complete |
| 2 | `agentplane` | #12 | Local-hybrid slice layout | standards-storage #13 |
| 3 | `TriTRPC` | #11 | Promote 2026-03-25 requirements winner | Wave 2 (review first for overlap) |
| 4 | `TriTRPC` | #12 | v4.1 governance + telemetry scaffolding | none (additive) |
| 5 | `TriTRPC` | #16 | Receipt transport binding spec | Wave 3 complete |
| 6 | `TriTRPC` | #17 | Transport event examples | TriTRPC #16 |
| 7 | `TriTRPC` | #19 | AOKC descriptor/order transport notes | agentplane #12 |
| 8 | `TriTRPC` | #20 | Seed local-hybrid slice v0 | agentplane #12 |
| 9 | `TriTRPC` | #18 | Atlas policy authority-chain | remove .write_probe.txt first |

---

## Wave 5 — Receipt path completion

| # | Repo | PR | Title | Prerequisite |
|---|------|----|-------|-------------|
| 1 | `slash-topics` | #14 | Topic-pack provenance + receipt binding | TriTRPC #16 |
| 2 | `human-digital-twin` | #4 | Policy/approval event schema + consent binding | agentplane #12 |
| 3 | `socioprophet-standards-knowledge` | #22 | AOKC knowledge taxonomy | Wave 3 complete |
| 4 | `agentplane` | *(new PR needed)* | Receipt builder | slash-topics#14 + HDT#4 |

---

## Wave 6 — Promotion overlays and secondary work

| # | Repo | PR | Title | Notes |
|---|------|----|-------|-------|
| 1 | `semantic-serdes` | #1 | Promote 2026-03-25 winner | Review for canonical fit |
| 2 | `ontogenesis` | #1 | Promote 2026-03-25 winner | Review for canonical fit |
| 3 | `cairnpath-mesh` | #1 | Twin economy Cairn reconciliation | Verify base branch target |
| 4 | `socioprophet` | #256 | AOKC runtime bootstrap | After Wave 4 |
| 5 | `socioprophet` | #255 | AOKC repo alignment note | After Wave 4 |

---

## Stale Dependabot Cleanup

Close `socioprophet` PRs #137, #138, #139, #145, #149, #150, #151, #155, #157, #158 — all superseded by newer group bump PRs.

Evaluate `socioprophet` PR #211 and `socioprophet-docs` PRs #73, #111, #112, #113, #119 for security relevance.

---

## Single-Branch Status Per Repo

The following repos need to be consolidated to `main` as their only long-lived branch (after their PRs merge):

| Repo | Action |
|------|--------|
| `sociosphere` | Merge this branch → close #20/#21/#23 as superseded |
| `socioprophet-standards-storage` | After FIPS cluster merges (Wave 3), delete all feature branches |
| `socioprophet-standards-knowledge` | After Wave 1 merges, delete all feature branches |
| `TriTRPC` | After Wave 4 merges, delete all feature branches |
| `agentplane` | After Wave 4 merges, delete all feature branches |
| `prophet-platform-standards` | After Wave 2 merges, delete feature branch |
| `slash-topics` | After Wave 5 merges, delete feature branch |
| `human-digital-twin` | After Wave 5 merges, delete feature branch |
| `mcp-a2a-zero-trust` | After Wave 1 merges, delete feature branch |
| `cairnpath-mesh` | After Wave 6 merges, reconcile base branch |

**Exempt**: `socioprophet/socioprophet` — multi-branch product repo, intentionally exempt.
