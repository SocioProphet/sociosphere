# Dolt build ledger table layout

This note captures the first recommended Dolt table layout for dependency resolution and build-cache state.

## Core tables

### `dependency_resolutions`
One row per evaluated dependency graph.

Suggested fields:
- `resolution_id`
- `workspace_ref`
- `created_at`
- `resolver_kind`
- `inputs_hash`
- `notes`

### `dependency_nodes`
One row per selected dependency node.

Suggested fields:
- `resolution_id`
- `node_id`
- `repo_ref`
- `revision_ref`
- `artifact_kind`

### `dependency_edges`
Edges for the selected dependency graph.

Suggested fields:
- `resolution_id`
- `from_node_id`
- `to_node_id`
- `edge_kind`

### `build_choices`
One row per evaluated build decision.

Suggested fields:
- `build_choice_id`
- `resolution_ref`
- `created_at`
- `target_system`
- `executor_class`
- `decision_status`
- `notes`

### `build_cache_entries`
One row per reusable cache record.

Suggested fields:
- `cache_entry_id`
- `created_at`
- `cache_key`
- `resolution_ref`
- `build_choice_ref`
- `artifact_class`
- `target_system`
- `producer_ref`
- `content_ref`
- `state`
- `notes`

### `build_materializations`
One row per materialization run.

Suggested fields:
- `materialization_id`
- `created_at`
- `build_choice_ref`
- `result_state`
- `notes`

### `build_materialization_artifacts`
Artifact refs emitted by a materialization.

Suggested fields:
- `materialization_id`
- `artifact_ref`

## Operational rule

These tables live in Dolt so that build-plan state can be:
- branched
- reviewed
- merged
- diffed
- replicated
- backed up

Git and the workspace lock remain canonical for source and desired inputs.
Dolt becomes canonical for the evaluated build/cache state derived from those inputs.
