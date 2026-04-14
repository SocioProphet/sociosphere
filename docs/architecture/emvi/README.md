# EMVI Operator Shell Architecture

This subtree consolidates the current EMVI operator-shell specification set for the
SocioProphet / sociosphere workspace.

EMVI is treated here as the operator shell over a local-first, offline-first,
auditable agent stack. It does **not** replace policy, planning, or graph truth;
it provides summon, focus, grammar, review, capture, preview, and execution-plan
selection over those lower layers.

## Reading order

1. [Agent stack alignment](agent-stack-alignment.md)
2. [Object model](object-model.md)
3. [Focus-state machine](focus-state-machine.md)
4. [Grammar and token ownership](grammar-token-ownership.md)
5. [Trust and action classes](trust-action-classes.md)
6. [Adapter contract](adapter-contract.md)
7. [Anchor resolution](anchor-resolution.md)
8. [Host-boundary preserve/replace policy](host-boundary-preserve-replace-policy.md)
9. [Cross-surface proof slice](cross-surface-proof-slice.md)

## Teaching and operational guides

- [Agent stack teaching guide](agent-stack-teaching-guide.md)
- [List aggregation primitive](list-aggregation-primitive.md)
- [Matrix hotkey alignment pressure test](matrix-hotkey-alignment-pressure-test.md)
- [Cross-surface proof slice acceptance tests](cross-surface-proof-slice-acceptance-tests.md)

## Matrices

- [Agent stack alignment matrix](agent-stack-alignment-matrix.csv)
- [Host-boundary keymap matrix](host-boundary-keymap-matrix.csv)

## Canonical intent

This subtree is the current draft architecture bundle for:
- keyboard-first operator interaction
- host/browser/editor/terminal surface unification
- local digital-twin UI routing
- agent/service-family lowering
- collection/snapshot/annotation capture
- provenance and ledger-aware execution

## Notes

- These docs are intentionally documentation-first. The next step is to wire the
  proof slice against the acceptance tests and then normalize any contract changes
  back into protocol and component repositories.
- Existing workspace docs remain authoritative for overall repo topology and
  workspace governance. This subtree only defines the EMVI/operator-shell layer.
