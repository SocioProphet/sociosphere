# Codex Execution Lane Semantics

## Purpose

This document defines the explicit status semantics for the **Codex** execution lane in the
SocioProphet agent work register (`examples/model-fabric-agent-work-register.example.json`).
It distinguishes Codex states from Copilot states and clarifies what constitutes delivery
versus engagement evidence.

---

## Trigger forms

| Task type | Trigger | Expected output |
|---|---|---|
| **Review** | `@codex review` | Codex posts findings as a GitHub comment on the issue or PR. |
| **Implementation** | `@codex Please take this...` | Codex attempts an implementation; delivery is NOT confirmed until a GitHub artifact is verifiable. |

---

## Codex lane statuses

| Status | Meaning |
|---|---|
| `codex_dispatched` | Codex has been triggered on the issue; no Codex response observed yet. |
| `codex_engaged` | Codex has acknowledged or replied to the task; no deliverable artifact produced yet. |
| `codex_findings_posted` | Codex posted review findings or analysis as a comment. **Engagement evidence only, not delivery.** |
| `codex_pr_open` | Codex has opened a verifiable GitHub PR. Delivery is pending merge. |
| `codex_pr_merged` | Codex PR has been merged into the target branch. **Delivery confirmed.** |
| `codex_unverified_output` | Codex posted output (comment, design, or analysis) but no GitHub PR, branch, commit, or merge is verifiable. **Engagement evidence only, not delivery.** |

---

## Delivery note

> **A Codex comment alone is NOT delivery.**
>
> Delivery requires a verifiable GitHub artifact: a merged PR, an open PR, a branch, or a commit.
>
> `codex_findings_posted` and `codex_unverified_output` are **engagement evidence** only.
> They demonstrate that Codex responded to a trigger but do not count as verified delivery
> unless backed by a GitHub PR, branch, commit, or merge that can be independently confirmed.

---

## Copilot lane (for contrast)

Copilot delivery uses the standard `status` field (`open`, `in-progress`, `blocked`, `closed`).
Copilot delivery is verified when a GitHub PR opened by `copilot-swe-agent[bot]` is merged.
Copilot lane items do **not** use `codexStatus`.

---

## Register field rules

- All items with `assignedLane: Codex` **must** include a `codexStatus` field.
- `codexStatus` must be one of the six values above.
- Copilot lane items must **not** include `codexStatus`.
- The validator (`tools/validate_model_fabric_work_register.py`) enforces these rules.

---

## Observed evidence (as of 2026-04-30)

| Issue | Lane | codexStatus | Notes |
|---|---|---|---|
| `functional-model-surfaces#5` | Codex (review) | `codex_findings_posted` | `@codex review` triggered; findings posted as GitHub comment. |
| `sociosphere#224` | Codex (implementation) | `codex_unverified_output` | `@codex Please take this...` triggered; detailed comment produced but no verifiable GitHub PR, branch, or commit found at verification time. Copilot used as fallback materialization. |
