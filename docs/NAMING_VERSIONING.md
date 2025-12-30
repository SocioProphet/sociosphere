# Naming, Semantics, and Versioning (Platform Repos)

This document defines how we name repositories, folders, modules, and releases so we preserve semantic clarity, avoid accidental commingling, and keep dependency graphs clean.

## 1) Core principle: repo identity encodes *domain*, not *version*
- **Repo names must be stable** and reflect what the thing *is* (e.g. `tritrpc`, `sociosphere`).
- **Versions live in tags/releases**, not repo names.
- Example:
  - ✅ `SocioProphet/tritrpc` with tags `v0.1.1`, `v0.1.2`, …
  - ❌ `SocioProphet/tritrpc-v1-full` (bakes an implementation snapshot and version semantics into identity)

## 2) Separation policy: core vs. workspace vs. notes
We maintain three distinct classes of repositories:

### 2.1 Core protocol / kernel projects (dependency roots)
- Purpose: normative specs, reference implementations, test vectors, conformance tooling.
- Rules:
  - Keep **tight scope** and stable APIs.
  - No workspace-specific glue unless it is a reusable SDK/tool.
  - Prefer `spec/` + `reference/` + `fixtures/` + `tools/`.
- Example: `tritrpc`.

### 2.2 Workspace / integration projects (composition layers)
- Purpose: assemble multiple components, pin versions, wire deployments.
- Rules:
  - May use submodules or vendoring only when pinned.
  - Must record the “bill of materials” (BOM) in a manifest.
- Example: `sociosphere`.

### 2.3 Notes / drafts / narrative archives (non-normative)
- Purpose: historical exploration, design notes, drafts.
- Rules:
  - **Never** required as a build dependency.
  - May be archived.
  - If important, extract canonical content into core repos as Markdown summaries.
- Example: `tritrpc-notes-archive` (formerly `trit-to-trust`).

## 3) Versioning standard: SemVer + tags + release notes
We use SemVer tags: `vMAJOR.MINOR.PATCH`.

- **PATCH**: bugfixes, docs corrections, test vector additions that do not change wire format.
- **MINOR**: backwards-compatible feature additions (new optional fields, new helpers, new tools).
- **MAJOR**: breaking changes (wire format, decoding rules, required fields).

### 3.1 Tagging rules
- Every repo release is a **Git tag** `vX.Y.Z`.
- Workspace pins must reference tags (or an immutable commit hash when unavoidable).
- Don’t “float” main/master as a dependency.

## 4) Dependency hygiene: how we avoid commingling
- `sociosphere` may depend on `tritrpc` via **submodule pinned to a tag** (preferred), or a specific commit hash.
- `tritrpc` must not depend on `sociosphere`.
- Notes archives must not be submodules unless explicitly pulled for research, and should not be transitively required.

## 5) Canonical documentation locations
- Normative protocol spec: `tritrpc/spec/*`
- Reference implementations: `tritrpc/go/*`, `tritrpc/rust/*`, `tritrpc/reference/*`
- Historical narrative extracted into core: `tritrpc/docs/*`
- Workspace integration status + pins: `sociosphere/docs/INTEGRATION_STATUS.md` + `manifest/workspace.toml`

## 6) Immediate next actions (backlog-aligned)
P0:
- Rename notes repo to `tritrpc-notes-archive` and archive it (optional but recommended).
- Extract/normalize the highest-value notes into `tritrpc/docs/trit-to-trust.md` as Markdown (keep originals under `docs/trit-to-trust_sources/` if needed).
P1:
- Add GitHub labels (P0/P1/P2, `area:protocol`, `area:workspace`, `type:cleanup`, `type:spec`, `type:docs`).
- Create a GitHub Project to track issues cross-repo (no Jira required).
