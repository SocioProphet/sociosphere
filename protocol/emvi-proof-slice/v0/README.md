# EMVI Proof Slice Protocol (v0)

This module defines the first governed execution contract for the EMVI cross-surface
proof slice.

The purpose is to move the EMVI/operator-shell work from architecture prose into a
protocol-shaped implementation surface that downstream components can target.

## Scope

This protocol covers the minimum end-to-end path for:
- local digital-twin UI page open
- page capture into a collection
- editor snippet capture into the same collection
- guarded shell execution with output capture
- graph façade query and result capture
- snapshot freeze and export
- provenance and ledger inspection

## Core invariant

A parsed shell intent becomes an `ActionSpec` before execution.
Execution routes through stable service families and records provenance.

## Minimum service families in scope

- `ui_runtime`
- `network`
- `policy`
- `collection`
- `graph`
- `knowledge`
- `shell`
- `ledger`
- `placement`
- `user`

## Required object kinds in scope

- `page`
- `snippet`
- `terminal_command`
- `terminal_output`
- `graph_result`
- `collection`
- `snapshot`
- `annotation`
- `action_spec`

## Required flow

1. `open page`
2. `capture current page into collection`
3. `capture current editor selection into collection`
4. `propose guarded shell execution`
5. `review policy outcome`
6. `capture shell output`
7. `query graph façade`
8. `capture graph result`
9. `freeze snapshot`
10. `export snapshot`
11. `inspect ledger trail`

## Companion documents

- `ACCEPTANCE.md` — acceptance gates for the proof slice
- `FIXTURE.md` — canonical demonstration sequence and fixture expectations
