# Repo topology (canonical)

## Core repos
- **sociosphere**: workspace/orchestrator + integration surface (manifests, tooling, platform composition).
- **tritrpc**: protocol spec + fixtures + reference implementations (Go/Rust/Python).

## Notes / archival
- **tritrpc-notes-archive**: raw historical drafts (RTF/HTML/etc). Optional; may be archived/read-only.
- Curated narrative belongs in `tritrpc/docs/` as Markdown.

## Rules
1) Directionality: `sociosphere -> tritrpc` allowed; `tritrpc -> sociosphere` forbidden.
2) Repo identity is stable; versions are tags/releases.
3) Submodule pins are explicit + reviewed, not floating.

## Repository hygiene requirements
- `.DS_Store`, `__MACOSX/`, and `._*` (macOS cruft) files must never be committed.
  CI will fail if any such files are detected (see `.github/workflows/validate.yml`).
- Submodule pin sanity: all submodule entries in `.gitmodules` must be present and pinned
  to an exact revision in `manifest/workspace.lock.json`.
- The `.gitignore` already excludes `.DS_Store` and `Thumbs.db`; this CI check is an
  additional backstop for files that were committed before the ignore rule was added.

## Submodule update playbook
To bump a submodule pin (e.g., `third_party/tritrpc`):

1. Fetch the new tag or commit SHA from the upstream repo.
2. Update `manifest/workspace.toml`: set `rev = "<new-sha>"` for the relevant entry.
3. Update `manifest/workspace.lock.json`: set `"rev": "<new-sha>"` and `"retrieved_at"` timestamp.
4. Run `git submodule update --init third_party/tritrpc` to checkout the new commit.
5. Stage and commit with a message like:
   `chore(workspace): bump tritrpc pin to <sha> (ref: #<issue>)`
6. Open a PR linking to the upstream release/tag and the issue that motivated the bump.
7. CI topology-check (`python tools/check_topology.py`) will verify the pin is consistent.

See also: [Naming and versioning policy](NAMING_VERSIONING.md).
