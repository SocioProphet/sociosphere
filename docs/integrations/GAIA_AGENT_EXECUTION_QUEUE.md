# GAIA Agent Execution Queue

Status: v0
Owner surface: SocioSphere

## Purpose

This queue translates the GAIA / OFIF / MeshLab governance map into repo-local implementation tasks for Codex and PR-local review/repair tasks for Copilot.

SocioSphere coordinates topology, readiness, validation lanes, source-exposure safety, and cross-repo propagation. Implementation remains in the owning repositories.

## Existing source of truth

- `registry/gaia-ofif-meshlab-capability-map.v1.json`
- `docs/integrations/GAIA_OFIF_MESHLAB_GOVERNANCE.md`
- `SocioProphet/prophet-platform:registry/gaia_ofif_meshlab_progress.v1.json`

## Agent operating split

Codex is for repo-local implementation work in configured development environments.

Copilot is for PR-local review, failed-check repair, conflict repair, and large-change review.

Human maintainer approval remains required for security workflow policy, runner policy, deployment, identity, Lattice admission, and any production navigation claim.

## Active queue

### A1. Org Vue shell promotion

Repo: `SocioProphet/socioprophet`
PR: `#294`
State: implementation ready; CodeQL runner queue remains external gate.

Current verified checks:

- `client-vue-product-build`: passing
- `check`: passing
- `devsecops`: passing
- `doctrine-contract`: passing
- `doctrine-links`: passing

Current blocker:

- `CodeQL` queued on self-hosted Fedora/CoreOS runner labels.

Acceptance:

- `socioprophet-web/client-vue` lands beside the old React shell.
- `/map` renders live mode when the API is available.
- `/map` renders demo fallback mode when the API is unavailable.
- Old React shell remains untouched.

### A2. Runner gate tracking

Repo: `SocioProphet/socioprophet`
Issue: `#295`
State: infrastructure follow-up.

Acceptance:

- CodeQL jobs run, or maintainers decide runner policy explicitly.
- The UI promotion PR does not change CodeQL policy.

### A3. Deployment split decision

Repo: `SocioProphet/socioprophet`
Issue: `#296`
State: ready for Codex.

Task brief:

Read `socioprophet-web/`, `marketing/`, `docs/.vitepress/`, `firebase.json`, and deployment docs. Add a decision record under `socioprophet-web/docs/` that separates the public marketing/docs surface from the Vue app shell.

Acceptance:

- Names `socioprophet-web/client-vue` as the app shell.
- Keeps marketing/docs separate unless a later decision unifies them.
- Documents `VITE_GAIA_MAP_API_BASE` for local, preview, staging, and production.
- Documents fallback mode and advisory constraints.
- Does not change deployment behavior.

### A4. Improve `/map` usability

Repo: `mdheller/socioprophet-web`, then promote to `SocioProphet/socioprophet`
State: next implementation slice.

Task brief:

Improve the `/map` workbench with explicit refresh controls, last-loaded time, live/demo status, and panel controls for evidence and governance. Keep fallback mode. Keep Storybook out of product build. Keep route `/map`.

Acceptance:

- Refresh snapshot control exists.
- H3 lookup failures do not blank the page.
- Evidence and governance panels stay usable in fallback mode.
- Product build passes.

### A5. OSM API browser integration hardening

Repo: `SocioProphet/prophet-platform`
State: ready for Codex after UI fallback stabilizes.

Task brief:

Read `apps/osm-map-api`. Add documentation and tests for browser consumption from the Vue app shell. Focus on CORS/config posture, local dev base URLs, readiness semantics, and response stability. Do not add a production tile server.

Acceptance:

- README or runbook documents Vue shell connection.
- `VITE_GAIA_MAP_API_BASE` usage is clear.
- OSM API tests pass.
- OpenAPI contract check passes.

### A6. Real-data adapter planning

Repo: `SocioProphet/gaia-world-model`
State: contract/planning slice.

Task brief:

Add a planning document for real OSM, satellite/EO, LiDAR, DEM/terrain, and weather/reanalysis adapters. Separate fixture-backed demo mode from future production ingestion. Define schemas, provenance, attribution, uncertainty, temporal validity, and validation gates.

Acceptance:

- Production claims remain blocked until validated.
- Lattice admission prerequisites are listed.
- Existing GAIA fixture validators pass.

### A7. Sherlock map evidence enrichment

Repo: `SocioProphet/sherlock-search`
State: next discovery layer.

Task brief:

Add or refine a Sherlock result fixture for the GAIA `/map` workbench, including H3 refs, OSM refs, evidence refs, provenance refs, and map/evidence actions.

Acceptance:

- Fixture validates under existing geospatial result validator.
- No production source exposure is introduced.

### A8. MeshRush map graph-view fixture

Repo: `SocioProphet/meshrush`
State: next graph layer.

Task brief:

Add or refine a graph-view fixture connecting OSM feature, H3 cell, route graph, Sherlock evidence, governance lane, and runtime boundary.

Acceptance:

- Fixture validates.
- Graph view remains advisory.

### A9. Agentplane map review candidate

Repo: `SocioProphet/agentplane`
State: after MeshRush fixture update.

Task brief:

Add a review candidate for GAIA map workbench graph-view review. Advisory by default. Approval required where runtime or safety boundaries would be crossed.

Acceptance:

- Candidate validates.
- No direct runtime execution is introduced.

## Execution rules

1. Work in the owning repository.
2. Keep PRs scoped to one repo and one workstream.
3. Ask Copilot to review PRs over 500 changed lines.
4. Do not alter security workflows or runner policy inside feature PRs.
5. Update readiness/progress ledgers when cross-repo state changes.
