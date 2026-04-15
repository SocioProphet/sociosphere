# Prophet Platform Evidence Registration

This note records the current placement decision for the evidence runtime surfaces associated with `SocioProphet/prophet-platform`.

## Decision

`evidence-receipts` is currently registered as an **app inside** `prophet-platform`, not as a standalone repository.

## Why

Sociosphere's workspace manifest is repo-level. `prophet-platform` is already declared in `manifest/workspace.toml`, so no new workspace repository entry is required just to add one more app inside that repo.

At the current maturity level, the evidence surfaces are still tightly coupled to the platform runtime and artifact layouts:
- `apps/eval-fabric-api` emits local payload / `EventEnvelope` / `EvidenceReceipt` artifacts
- `apps/lampstand` emits local payload / `EventEnvelope` / `EvidenceReceipt` artifacts plus catalog entries
- `apps/evidence-receipts` reads those artifacts
- `apps/gateway` exposes thin evidence reader routes

Because artifact layout conventions and read paths are still stabilizing, splitting `evidence-receipts` into a dedicated repository now would over-separate the platform.

## Current registration rule

Keep the capability inside `prophet-platform` while:
- producer artifact layout conventions are still being normalized
- gateway read paths are still being proven
- the reader remains tightly bound to platform-local runtime behavior

Promote it to a standalone repository only if it becomes:
- independently versioned
- independently deployed
- or broadly reused outside `prophet-platform`

## Sociosphere interpretation

- Workspace repo registration remains unchanged: `prophet-platform` continues to be the registered repo.
- This note serves as the explicit current-state registration for the in-repo evidence surfaces until or unless they justify repo-level separation.
