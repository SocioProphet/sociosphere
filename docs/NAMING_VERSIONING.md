# Naming + Versioning (canonical)

## 1) Repo naming (semantic identity)
- Repo names are **stable nouns** that describe what the thing *is*.
- **Never** embed versions in repo names.
  - ✅ `tritrpc`, `sociosphere`
  - ❌ `tritrpc-v1-full`, `socio-workspace-v0.1`
- If we need multiple generations, we use **branches/tags** and (rarely) a suffix only for *fundamentally different* products (e.g., `tritrpc-tools`, `tritrpc-spec`).

## 2) Versioning (SemVer)
We use Semantic Versioning tags: `vMAJOR.MINOR.PATCH`

- **MAJOR**: breaking protocol changes (wire format, required fields, decoding rules, validation rules).
- **MINOR**: backward-compatible additions (new optional fields, new examples, new tools that don’t change decoding semantics).
- **PATCH**: fixes, docs, test vectors, build/CI, metadata cleanup.

## 3) Release discipline
- `tritrpc` tags/releases are the canonical version boundary for the protocol + fixtures + reference implementations.
- `sociosphere` pins dependencies (submodules) to tags where possible.
- “Bump submodule pin” is always an explicit commit with a short rationale and a linked issue.

## 4) Dependency directionality (non-commingling rule)
- `sociosphere` may depend on `tritrpc` (submodule pinned to a tag, or commit hash if necessary).
- `tritrpc` must **not** depend on `sociosphere`.
- Notes/ideation may live in `tritrpc/docs/` (curated) or in an archive repo (uncurated), but are not runtime deps.

## 5) Submodule pin-bump rules
- Every submodule pin bump is an **explicit commit** — never a silent file change.
- Commit message format: `chore(workspace): bump <submodule> pin to <rev> (ref: #<issue>)`
- The commit must reference the upstream release, tag, or rationale.
- Pin bumps are reviewed in a PR; they are not self-merged.
- After merging, CI `topology-check` must pass with `rev` populated in the lock file.
- Follow the full procedure in [docs/TOPOLOGY.md § Submodule update playbook](TOPOLOGY.md).
