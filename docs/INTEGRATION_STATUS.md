# Integration Status

This file is the **single current-state ledger** for cross-repo integration
facts that were previously repeated in multiple sections.

## TritRPC integration (current)

- Canonical upstream: `https://github.com/SocioProphet/TriTRPC`
- Workspace entry: `manifest/workspace.toml` repo `tritrpc`
- Materialization path: `third_party/tritrpc`
- Dependency status: active workspace dependency

## Trit-to-Trust integration (current)

- Workspace dependency status: **removed**
- Notes and related content were folded into TritRPC documentation.

## Historical sequence (resolved)

1. TritRPC + Trit-to-Trust were initially tracked together.
2. Both were temporarily pinned during migration.
3. Workspace was de-commingled to keep TritRPC as the only active dependency.
4. Trit-to-Trust was retired from workspace dependency lists.

## Interpretation rule

If any other document references older Trit-to-Trust workspace dependencies,
treat that as historical context only. Current behavior is defined by
`manifest/workspace.toml` and the lock file.
