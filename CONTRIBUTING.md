# Contributing to sociosphere

## Repository hygiene

### macOS cruft files
Never commit `.DS_Store`, `__MACOSX/` directories, or `._*` resource-fork files.
These are already excluded by `.gitignore`, but CI will also reject them via
`tools/check_hygiene.sh` as a backstop.

If you accidentally staged macOS files, remove them with:
```bash
git rm --cached .DS_Store
git rm -r --cached __MACOSX/
```

### Submodule pins
Submodules in `.gitmodules` must always be pinned to an exact commit SHA in
`manifest/workspace.lock.json`. CI will fail if any submodule is unpinned.

To bump a submodule pin, follow the procedure in
[docs/TOPOLOGY.md § Submodule update playbook](docs/TOPOLOGY.md).

## Naming and versioning

Follow [docs/NAMING_VERSIONING.md](docs/NAMING_VERSIONING.md) for:
- Repo naming conventions (stable nouns, no version suffixes in names)
- SemVer tag discipline
- Submodule pin-bump commit message format

## Topology and dependency rules

Follow [docs/TOPOLOGY.md](docs/TOPOLOGY.md) for allowed dependency directions.
In particular: `tritrpc` must never depend on `sociosphere`.

CI enforces these rules via `python tools/check_topology.py`.

## Glossary and ontology

New terms and concepts should be added to [docs/GLOSSARY.md](docs/GLOSSARY.md)
and reflected in the ontology files:
- `ontologies/sociosphere.jsonld` (JSON-LD)
- `ontologies/sociosphere.ttl` (Turtle / RDF)

## Running CI checks locally

```bash
# Full workspace check (topology, hygiene, standards, registry)
make workspace-check

# Individual checks
make topology-check       # dependency directionality
make hygiene-check        # macOS cruft + submodule pin sanity
make registry-validate    # ontology roles + dep-graph cycles
make validate-standards   # standards schema validation
make lock-verify          # lock file consistency
```
