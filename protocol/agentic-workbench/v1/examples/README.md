# Agentic Workbench v1 Examples

This examples lane documents the extension surfaces added after the initial v1 index.

## Core relationship

These examples are projections or refinements over the canonical workbench objects:

- `WorkOrder` is an operator-friendly projection of `WorkflowRun`.
- `LaunchConfig` refines how a `WorkflowRun` + `ExecutionEnvelope` should be launched.
- `ProfileArtifact` captures profiling output that can be linked into `ExecutionRecord` evidence sets.

## Files

- `work_order.example.v0.1.json`
- `launch_config.example.v0.1.json`
- `profile_artifact.example.v0.1.json`

## Discoverability note

The primary protocol index currently tracks the original v1 workbench object set.
The companion file `../projections.index.v0.1.json` lists the projection/extension schemas introduced later.
