# Lattice Studio Workspace Integration Registration

Sociosphere tracks this integration as part of the workspace topology and governance graph.

## Registered capability

```text
prophet-workspace office/workspace surfaces
  -> prophet-platform Lattice Studio
  -> PlatformAssetRecord
  -> search/topics/governance/evidence spine
```

## Repositories

- `SocioProphet/prophet-workspace`
  - Owns backend-neutral office/workspace product semantics.
  - Owns `WorkspaceSource` and `WorkspaceActionReceipt` contracts.
  - Owns workspace source/action examples for docs, sheets, slides, and publication receipts.

- `SocioProphet/prophet-platform`
  - Owns Lattice Studio orchestration.
  - Owns PlatformAssetRecord conversion for workspace sources and action receipts.
  - Owns CLI demo emission and platform-local contract fixtures.

- `SocioProphet/lattice-forge`
  - Owns governed runtime construction through `RuntimeAsset`.
  - Provides notebook/runtime surfaces consumed by Lattice Studio.

- `SocioProphet/google_workspace_mcp`
  - May serve as a Google Workspace adapter implementation.
  - Does not own the canonical product contract.

## Governance state

Status: active integration slice.

Current proof level:

- Contract-level integration exists in `prophet-workspace`.
- Platform ingestion/conversion exists in `prophet-platform`.
- Demo fixtures exist in both producer and platform consumer surfaces.
- Lattice Studio CLI can emit a workspace demo bundle and PlatformAssetRecordSet.

Not yet complete:

- No live backend adapter invocation has been proven.
- No production authorization/policy gate has been enforced against real workspace data.
- No end-to-end UI flow has been proven.
- No search/topic/governance ingestion job has been executed from these records.

## Required topology edge

```text
prophet-workspace:WorkspaceSource
  providesSourceFor -> prophet-platform:LatticeStudio

prophet-workspace:WorkspaceActionReceipt
  providesEvidenceFor -> prophet-platform:EvidenceBundle

prophet-platform:LatticeStudio
  consumesRuntimeFrom -> lattice-forge:RuntimeAsset

prophet-platform:LatticeStudio
  mayUseAdapter -> google_workspace_mcp
```

## Product doctrine

Office work is not outside the notebook/workbench. It is part of the source, evidence, publication, and collaboration fabric.

Lattice Studio should feel like NotebookLM-class source-grounded synthesis plus executable governed workbench infrastructure, integrated with workspace documents, sheets, slides, mail, calendar, chat, meetings, and audit surfaces.
