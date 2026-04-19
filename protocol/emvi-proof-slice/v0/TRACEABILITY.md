# Proof Slice Traceability

This note maps acceptance gates to the protocol-facing proof-slice artifacts.

| Acceptance area | Primary artifact | Supporting artifact |
|---|---|---|
| Focus ownership | `../docs/architecture/emvi/focus-state-machine.md` | `ACCEPTANCE.md` |
| Parse / ActionSpec boundary | `ACTIONSPEC.md` | `schemas/actionspec.schema.json` |
| Event / provenance trail | `EVENTS.md` | `schemas/event-envelope.schema.json`, `fixtures/events.example.jsonl` |
| End-to-end flow | `FIXTURE.md` | `ACCEPTANCE.md` |
| Page/snippet/output capture | `README.md` | `fixtures/actionspec.example.json` |

## Rule

A proof-slice implementation should not be considered complete until every row above
has at least one executable validation path behind it.
