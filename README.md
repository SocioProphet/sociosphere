# sociosphere

Sociosphere is the **workspace controller** for the SocioProphet ecosystem.
It is the meta-repository that defines reproducible multi-repo assembly via a
canonical manifest + lock, plus validation and orchestration tooling.

## Canonical scope

Sociosphere is responsible for:

- Declaring workspace repositories and roles in `manifest/workspace.toml`.
- Pinning exact revisions in `manifest/workspace.lock.json`.
- Materializing and validating the workspace with `tools/runner/runner.py`.
- Enforcing topology and dependency-direction policies via `tools/check_topology.py`.
- Maintaining cross-repo governance/registry data in `registry/` and `governance/`.

Sociosphere is **not** the place for product feature implementation inside
component repositories.

## Canonical entry points

- Documentation index: `docs/README.md`
- Architecture baseline: `docs/architecture/overview.md`
- Scope and backlog: `docs/SCOPE_PURPOSE_STATUS_BACKLOG.md`
- Integration status ledger: `docs/INTEGRATION_STATUS.md`
- Governance ownership map: `governance/CANONICAL_SOURCES.yaml`

## Quickstart

```bash
python3 tools/runner/runner.py list
python3 tools/runner/runner.py fetch
python3 tools/runner/runner.py lock-verify
python3 tools/runner/runner.py run test --all
```

## Documentation de-duplication policy

To avoid conflicting documentation, this repository follows these rules:

1. **One canonical source per topic** (linked above).
2. Historical branch/PR narratives remain archival only and must not define
   current operational requirements.
3. When a document conflicts with canonical files, canonical files win.
