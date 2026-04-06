# Intent Audit — 2026-04-06

This report establishes the **intent-to-execution** contract for wave-based PR integration.

## Scope

- Source snapshot: `status/pr-register.yaml` dated 2026-04-06
- Execution guide: `governance/MERGE-ORDER.md`
- Supersession proof: `status/supersession-ledger.yaml`

## Review Matrix (initial baseline)

| Group | PRs | Intent source | Verification status |
|---|---|---|---|
| Wave 1 ready PRs | standards-knowledge #16-#21, mcp-a2a-zero-trust #1, socioprophet #223/#253 | PR titles + notes in register | pending |
| Wave 2 promotion/review | prophet-platform-standards #1, sociosphere #19, socioprophet #257, etc. | `intent_checklist` in register | pending |
| Wave 3 FIPS chain | standards-storage #14/#15/#16/#18/#19/#17/#20/#21/#22/#23 | `intent_checklist` + chain validation | pending |
| Wave 4/5 receipt path | TriTRPC / agentplane / slash-topics / HDT | `intent_checklist` in register | pending |

## Required closeout procedure

For each merged PR in a wave:

1. Record merge commit SHA.
2. Mark each intent checklist row as `satisfied`, `partial`, or `missed`.
3. Add evidence links to changed files.
4. Create backlog follow-up tasks for `partial`/`missed` items.

## Backlog linkage

Follow-up items must be recorded in `workbench/backlog/INTEGRATED_BACKLOG.md` under the "Intent Audit Follow-ups" section.
