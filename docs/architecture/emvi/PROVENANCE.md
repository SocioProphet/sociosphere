# EMVI Spec Bundle Provenance

This bundle consolidates operator-shell design work that was previously developed
across multiple design-session artifacts and source notes.

## Source themes incorporated here

- EMVI keyboard-first command-surface design
- slashtag / scoped-intent semantics
- macOS / launcher / accessibility alignment
- Matrix hotkey pressure testing
- local digital-twin UI constraints
- local-first / offline-first agent stack alignment
- collection / snapshot / annotation primitives
- trust-class, proof-slice, and host-boundary policies

## Repo placement rationale

This bundle lands in `sociosphere` because `sociosphere` is the workspace
controller and canonical architecture/governance surface for the platform.
Downstream component repositories should consume, implement, or further refine
these contracts rather than redefining them independently.
