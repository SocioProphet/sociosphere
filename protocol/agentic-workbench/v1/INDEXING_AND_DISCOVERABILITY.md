# Agentic Workbench v1 — Indexing and Discoverability

This note clarifies how to discover the full v1 workbench schema set while the primary index file and the later projection layer coexist.

## Primary index

The original canonical core object set remains listed in:

- `index.json`

That file currently covers the original workbench kernel objects.

## Additive projection layer

Later additive work introduced the following projection/extension schemas without replacing the original workbench canon:

- `WorkOrder`
- `LaunchConfig`
- `ProfileArtifact`

Those schemas are discoverable through:

- `projections.index.v0.1.json`

## Aggregate full-set index

For consumers that need one file containing the complete current v1 schema set, use:

- `index.extended.v0.1.json`

That aggregate file includes the original nine core workbench objects plus the three later projection/extension objects.

## Examples

Concrete examples for the projection layer live under:

- `examples/work_order.example.v0.1.json`
- `examples/launch_config.example.v0.1.json`
- `examples/profile_artifact.example.v0.1.json`
- `examples/README.md`

## Practical guidance

- Use `index.json` when you only want the original workbench kernel.
- Use `index.extended.v0.1.json` when you want the full current v1 surface.
- Use `projections.index.v0.1.json` when you want only the additive projection layer.

## Follow-on cleanup

When a safe existing-file update path is available, the preferred end state is to patch `index.json` in place and reduce the need for multiple parallel discoverability files.
