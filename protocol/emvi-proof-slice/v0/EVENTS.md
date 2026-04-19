# Proof Slice Event Envelope (v0)

This document defines the minimum event trail expected from the EMVI proof slice.

## Event types

- `shell.intent_parsed`
- `shell.actionspec_created`
- `policy.evaluated`
- `ui.page_opened`
- `collection.member_appended`
- `shell.command_executed`
- `shell.output_captured`
- `graph.query_executed`
- `snapshot.created`
- `snapshot.exported`
- `ledger.recorded`

## Required fields

- `event_id`
- `event_type`
- `timestamp`
- `correlation_id`
- `actor`
- `action_spec_id` when applicable
- `target_ids[]`
- `service_family`
- `status`
- `placement`

## Requirements

1. Every nontrivial proof-slice step emits at least one event.
2. Events share a common `correlation_id` for one end-to-end run.
3. Ledger visibility is mandatory for execution and capture milestones.
4. Policy outcomes must be represented explicitly, not inferred from absence.
