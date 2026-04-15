# SourceOS Canonical Root Normalization — 2026-04-15

## Decision

Canonical runtime root for the SourceOS product line is:

- `SociOS-Linux/SourceOS`

The lowercase variant is not a peer runtime root.

- `SociOS-Linux/source-os` is a migration alias / merge source / redirect candidate only.

## Why this decision is locked

- Product naming coherence: `SourceOS` is the branded canonical root.
- Prevents dual-root drift in automation, manifests, CI, and docs.
- Aligns runtime naming to the public-facing product identity.

## Required governance follow-up

Patch the existing canonical governance files to reflect this decision:

1. `registry/deduplication-map.yaml`
   - resolve `sourceos_workspace`
   - set canonical home to `SociOS-Linux/SourceOS`
   - mark `source-os` as migration alias

2. `registry/canonical-repos.yaml`
   - ensure canonical runtime root points to `SociOS-Linux/SourceOS`
   - demote or remove any canonical references to `source-os`

3. `manifest/workspace.toml`
   - replace old lowercase root references where they imply canonical authority
   - align remote mirror/runtime root references to `SociOS-Linux/SourceOS`

4. `docs/repo-map.md`
   - clarify that sociosphere is not the runtime repo
   - declare `SociOS-Linux/SourceOS` as canonical runtime root

5. `docs/notes/automation-integration-capture-2026-04-15.md`
   - add explicit canonical runtime note

## Acceptance criteria

- No governance artifact lists `source-os` as canonical runtime root.
- Canonical runtime references resolve to `SociOS-Linux/SourceOS`.
- The duplicate-root state is documented as migration in progress, not undecided.

## Follow-up implementation task

Perform content-level comparison before any archive/redirect step:

- compare `SociOS-Linux/SourceOS`
- compare `SociOS-Linux/source-os`

The naming decision is locked now. Content migration direction can still be decided after diff review.
