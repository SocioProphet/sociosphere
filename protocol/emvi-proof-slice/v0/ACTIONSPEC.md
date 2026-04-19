# ActionSpec Contract (v0)

The proof slice treats `ActionSpec` as the execution boundary between parsed shell
intent and side effects.

## Required fields

- `id` — stable action identifier
- `intent` — normalized shell intent
- `action_class` — Observe | Capture | Draft | ReversibleWrite | IrreversibleWrite | PrivilegedExecute | DelegatedProposal | DelegatedExecute
- `targets[]` — typed target objects
- `service_families[]` — execution routing families
- `placement` — host | LMS | fog | cloud-twin
- `preview_required` — boolean
- `confirmation_required` — boolean
- `rollback_expected` — boolean
- `policy_status` — pending | allowed | denied | confirmation_required
- `provenance_sink` — ledger/provenance target

## Example intent classes in proof slice

### Open page
Observe action routed through `ui_runtime`, `network`, `policy`.

### Capture page/snippet/output
Capture action routed through `collection` and `ledger`, with source-specific
families also present.

### Guarded shell execution
ReversibleWrite, IrreversibleWrite, or PrivilegedExecute depending on the command,
routed through `shell`, `policy`, and `ledger`.

### Snapshot export
Capture or Observe, routed through `collection` and `ledger`.

## Rule

No nontrivial execution path in the proof slice bypasses ActionSpec creation.
