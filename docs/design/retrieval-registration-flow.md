# Retrieval registration flow

## Purpose
Define how an `IndexRef` becomes queryable in the workspace retrieval graph.

## Core rule
Registration happens immediately after index attachment, even when the index is still `WARMING`.

## Inputs
- `IndexRef`
- `ManifestRef`
- `PolicyBundleRef`
- workspace and dataset scope refs

## Registration phases
### Phase 1 — accept
The retrieval graph records the new `IndexRef` and binds it to dataset/workspace scope.

### Phase 2 — expose
The retrieval planner may use the index in `WARMING` state for partial or degraded retrieval according to policy.

### Phase 3 — promote
When index state becomes `READY`, the planner promotes it to preferred candidate for the associated manifest.

## Required registration fields
- `index_id`
- `manifest_id`
- `dataset_ref`
- `workspace_ref`
- `state`
- `pipeline_version`
- `classification_tags[]`
- `query_visibility`

## Query visibility modes
- `hidden`
- `partial`
- `full`

## Planner rules
- `READY + full` beats `WARMING + partial`
- local authoritative indexes beat remote mirrors in `local_first`
- stale remote indexes may be used only when policy allows stale reads

## Failure behavior
- failed registration blocks queryability even if the index artifacts exist
- distribution success is not required for local retrieval registration

## Example
1. mount registration yields `IndexRef(state=WARMING)`
2. retrieval graph registers it as `partial`
3. chunk lookup works for already-materialized segments
4. when embeddings and keyword segments complete, state becomes `READY`
5. planner promotes to `full`
