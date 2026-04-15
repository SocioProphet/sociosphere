#!/usr/bin/env bash
# create-branch-prs.sh — Create all pending branch PRs using the gh CLI.
#
# Usage:
#   gh auth login          # authenticate once if not already done
#   ./scripts/create-branch-prs.sh
#
# Requires: gh CLI (https://cli.github.com)
set -euo pipefail

REPO="SocioProphet/sociosphere"
BASE="main"

echo "Creating PRs for all pending branches in $REPO..."

gh pr create \
  --repo "$REPO" \
  --base "$BASE" \
  --head "workflow-trust/pr1-agentic-workbench-v1" \
  --title "feat: agentic workbench v1 — workflow kernel, protocol router, workspace policy" \
  --body "## Summary

Establishes the foundational agentic workbench v1 infrastructure: workflow kernel design,
updated protocol router, and workspace policy configuration.

## Changes

- \`docs/WORKFLOW_KERNEL_v0.1.md\` — Workflow-kernel objects and controller/runtime ownership split
- \`manifest/workspace.toml\` — Workspace policy block + agentplane & mcp-a2a-zero-trust repos
- \`protocol/protocol.md\` — Updated protocol router for agentic workbench v1" \
  && echo "✅ PR 1 created" || echo "⚠️  PR 1 may already exist"

gh pr create \
  --repo "$REPO" \
  --base "$BASE" \
  --head "seed-local-hybrid-smoke-v0" \
  --title "feat: add local hybrid smoke runner" \
  --body "## Summary

Adds a standalone local hybrid smoke test runner script.

## Changes

- \`tools/smoke/run_local_hybrid_smoke.py\` — New local hybrid smoke runner (103 lines)" \
  && echo "✅ PR 2 created" || echo "⚠️  PR 2 may already exist"

gh pr create \
  --repo "$REPO" \
  --base "$BASE" \
  --head "wip/ui-inventory-2026-01-09" \
  --title "feat: UI inventory, standards framework, schemas, pipelines, and conformance tooling (Jan 2026)" \
  --body "## Summary

Large feature branch (76 files, +3031/-19) adding UI inventory, standards framework,
schemas, finance/ops pipelines, DeLeX GTM intelligence program, and conformance tooling.

## Changes

- Standards: Finance (COA, posting templates, statement lines), Ops metrics, UI component inventory
- Schemas: JSON schemas for finance, ops, UI, TriRPC Avro, DeLeX GTM Intelligence
- Pipelines: Finance SQL (balance sheet, income, cash flow), Ops SQL metrics (13 files)
- Programs: programs/delex/gtm-intelligence/ taxonomy, metrics, monitoring
- Tools: Schema/finance/standards validators, UI inventory validator, conformance harness
- CI: .github/workflows/standards-validate.yml, Makefile targets
- Docs: Standards index, morloc/schema-distribution/trirpc, UI interface inventory

> ⚠️ Large PR — recommend careful review before merging." \
  && echo "✅ PR 3 created" || echo "⚠️  PR 3 may already exist"

gh pr create \
  --repo "$REPO" \
  --base "$BASE" \
  --head "codex/evaluate-and-plan-branch-integration" \
  --title "docs: branch integration plan, audit tooling, and merge governance artifacts" \
  --body "## Summary

Adds branch integration planning documents, merge governance artifacts, and an audit tool.

## Changes

- \`docs/branch-integration-plan.md\` — Integration plan document
- \`governance/merge-execution-log.md\` — Merge execution log
- \`governance/merge-wave-plan.md\` — Merge wave plan
- \`tools/branch_integration_audit.py\` — Branch audit and merge wave generator (363 lines)
- \`workbench/backlog/branch-catalog.tsv\` — Branch catalog" \
  && echo "✅ PR 4 created" || echo "⚠️  PR 4 may already exist"

echo ""
echo "Done. View open PRs at: https://github.com/$REPO/pulls"
