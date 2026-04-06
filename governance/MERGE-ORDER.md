# MERGE-ORDER.md — Safe merge order for pending SocioProphet PRs
# Generated: 2026-04-06
# This document defines the dependency-safe merge sequence for all open draft PRs.
# Reference: status/pr-register.yaml and registry/dependency-graph.yaml

## Guiding Principles

1. **Standards before implementation** — ADRs and standards must land before code that implements them.
2. **Schemas before consumers** — Shared schema definitions before anything that reads/writes them.
3. **Specs before fixtures** — Protocol specs before reference fixtures.
4. **No cascading conflicts** — Each PR in a cluster must target the previous one's merged result, not `main`.
5. **Words are contracts** — PR titles and bodies must be converted into executable acceptance checks before merge.

---

## Pre-wave Refresh Checklist (required before every wave)

1. Refresh `status/pr-register.yaml` from current PR state and update:
   - `metadata.snapshot_date`
   - `metadata.total_open_prs`
   - state counters (`ready_to_merge`, `needs_review`, `needs_triage`, `draft_active`)
2. Record the refresh commit SHA in `status/ecosystem-status.yaml` under `merge_execution.last_snapshot_commit`.
3. Enforce a wave freeze window:
   - No branch retargeting/rebasing outside designated wave integrator.
   - No merge execution if snapshot is older than 24 hours.
4. Abort the wave if snapshot and live PR states differ materially.

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

### Companion PR atomicity gate (required)

Companion PR pairs must follow atomic review semantics:

- Pair: `sociosphere#19` ↔ `socioprophet#257`
- Required before merge:
  1. Shared terminology compatibility note posted on both PRs.
  2. Review sign-off completed for both PRs.
  3. If either PR changes materially after review, re-request review on both.
  4. Merge both in same wave window or defer both.

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

### FIPS chain validation checklist (required)

Before any merge in this cluster:

1. Verify each PR base target equals the previous PR branch in the chain.
2. Verify diff is incremental versus immediate predecessor (no independent main-target rewrite).
3. Mark `status/pr-register.yaml.fips_triage.chain_validation.pr_<num>.validated`.
4. Block merge if any PR still targets `main` incorrectly.

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

## Intent preservation and supersession controls

### Superseded PR closure protocol

Before closing superseded PRs, complete `status/supersession-ledger.yaml` mapping each superseded PR intent to retained artifacts.

### Post-merge intent audit protocol

At the end of each wave:

1. Generate `status/intent-audit-YYYY-MM-DD.md`.
2. For every merged PR, mark each intent checklist item as satisfied/partial/missed.
3. Create backlog tasks for any partial/missed item in `workbench/backlog/INTEGRATED_BACKLOG.md`.
4. Link audit file from `status/ecosystem-status.yaml.merge_execution.latest_intent_audit`.

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
