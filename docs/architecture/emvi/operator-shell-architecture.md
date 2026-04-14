# EMVI Operator Shell Architecture

Status: Draft v0.1

## Purpose

This document is the first codebase-native consolidation of the EMVI operator-shell
specification set. It establishes the shell layer that sits above the local-first,
offline-first agent stack and defines the core contracts that downstream
implementations must preserve.

The intent is to make browser tabs, pages, file ranges, snippets, terminal
commands, outputs, servers, graph results, collections, snapshots, and annotations
behave as first-class typed objects under one keyboard-first shell.

## Canonical position in the stack

EMVI is the operator shell and interaction grammar for the larger agent system.
It is not the planner, not the policy engine, not the knowledge substrate, and
not the browser runtime.

The surrounding stack provides:
- planning and decomposition of larger actions
- policy evaluation and permission checks
- symbolic and graph truth
- local digital-twin UI rendering and fetch mediation
- provenance, run-package, and ledger visibility
- host/LMS/fog/cloud placement

EMVI provides:
- summon and focus ownership
- grammar and token interpretation
- preview, review, and execution-plan selection
- capture into collections and snapshots
- operator-visible action routing
- cross-surface continuity across host, browser, editor, and terminal

## Architectural invariants

1. Search is the default interpretation for free text.
2. Slash is scope/filter syntax in shell-owned states, not a universal command prefix.
3. Grammar only runs in grammar-owning states. It must not hijack editor insert,
   terminal pass-through, browser text fields, password fields, or accessibility-owned input.
4. EMVI lowers intent into stable service families rather than talking directly to
   arbitrary subsystems.
5. Every side effect must pass through an execution-plan boundary with trust class,
   confirmation policy, and provenance.
6. Every captured reference must be anchorable and re-resolvable over time.
7. The shell is host-first and offline-first by default, then may spill to LMS,
   fog, or cloud-twin placement when policy or workload requires it.

## Universal object model

The shell operates over six top-level kinds.

### 1. Resource
A typed thing that can be opened, inspected, captured, or acted on.
Examples: page, browser tab, URL, file, folder, symbol, snippet, terminal
command, terminal output, host, service, graph row, issue, note.

### 2. Context
The active environment that binds deictics like `current`, `selection`, `recent`,
and `here`.
Examples: current browser window, current editor buffer, current terminal pane,
current collection view, current graph result set.

### 3. Collection
A mutable working set of typed references.
Collections are for research, curation, briefing, comparison, incident handling,
reading, or summarization. They are the operator working surface.

### 4. Snapshot
An immutable freeze of a collection or live context.
Snapshots are evidence-bearing and exportable. They should be treated as the
stable handoff unit for review, replay, and provenance.

### 5. Annotation
A human or agent-authored interpretation layer attached to one or more anchors.
Annotations may hold notes, tags, claims, summaries, relationships, rankings,
follow-up tasks, or citations.

### 6. ActionSpec
A typed, reviewable execution plan produced after parsing but before execution.
It includes normalized intent, target objects, trust class, required confirmations,
rollback expectations, service-family routing, and provenance metadata.

## Identity, locator, and anchor split

The shell distinguishes between object identity, locator, and anchor.

- Identity answers: what object is this?
- Locator answers: where can this object be reached or re-opened?
- Anchor answers: where inside the object is the relevant portion?

That split is essential because a URL is not the same as a quote inside a page,
and a file path is not the same as a line range or symbol path.

## Focus and ownership model

Keyboard correctness depends on explicit focus ownership.

The important states are:
- host idle
- shell overlay input
- shell result list
- shell preview
- shell action sheet
- local list or tree navigation
- local editor insert/normal/select
- terminal pass-through
- remote shell pass-through
- modal confirmation
- plan review
- tool confirmation

### Ownership rules

- Printable input belongs to the active local surface in pass-through states.
- Tab and Shift-Tab move between regions unless an active completion surface owns Tab.
- Arrow keys move within local composite regions.
- Escape unwinds the innermost active transient state first.
- Enter does not imply universal commit; in composition surfaces it may remain newline,
  while an explicit send or execute chord owns commit.
- Up/Down history escape from multiline surfaces only at allowed boundaries.

## Grammar model

The parser uses a safe hybrid grammar.

### Default rule
Free text is search.

### Command entry
Commands enter command mode either:
- explicitly with a leading `>`; or
- implicitly when a reserved verb is followed by enough command evidence.

This prevents ambiguous phrases like `open source licensing` from being parsed as
commands when they are more likely to be search.

### Scope rule
Leading slash tokens denote scope/filter in shell-owned states.
Examples:
- `/files telemetry policy`
- `/browser current`
- `/graph commonsense deer corridor`

### Path rule
Absolute POSIX-style paths must not collide with scope syntax.
Absolute paths therefore require one of:
- `path:/etc/hosts`
- quoted absolute path strings
- `file://...`
- relative forms like `./`, `../`, or `~/`

### Deictics
Deictics such as `current`, `selection`, `recent`, and `here` are late-bound against
focus owner and context, not expanded too early.

## Trust and action classes

Parsing intent is not execution.
Every parsed command must become an ActionSpec with a trust class.

The minimum action classes are:
- Observe
- Capture
- Draft
- ReversibleWrite
- IrreversibleWrite
- PrivilegedExecute
- DelegatedProposal
- DelegatedExecute

### Required plan fields
Every ActionSpec must declare:
- normalized intent
- target objects and locators
- service-family routing
- trust class
- required confirmation boundary
- preview availability
- rollback availability
- provenance sink

## Service-family lowering

EMVI should route to stable service families rather than directly to arbitrary
implementation details.

The current service-family set is:
- `user`
- `planner`
- `policy`
- `graph`
- `knowledge`
- `search`
- `shell`
- `network`
- `ui_runtime`
- `collection`
- `ledger`
- `placement`

This means, for example, that browser actions lower through `ui_runtime`,
`network`, and `policy`, not direct remote page execution.

## Local digital-twin UI boundary

Browser-like work in this stack is local-runtime work, not remote page trust.
The shell must assume:
- no trust in remote JS/CSS/fonts by default
- local verified components only
- fetch mediated by network and policy services
- rendering through the local digital-twin UI runtime
- cloud-twin or K3s bastion roles are execution or relay roles, not UX authority

## Collections, snapshots, and list aggregation

The shell treats list aggregation as a primitive, not as a browser convenience.
Tabs, snippets, terminal outputs, graph rows, and service references all become
collection members under one capture model.

### Core verbs
- capture current
- capture selection
- capture all visible
- append to collection
- create snapshot
- export snapshot
- summarize collection
- compare collections
- publish or brief from collection

### Export requirement
Collections and snapshots are not complete unless export is first-class.
The architecture assumes export to portable forms such as Markdown, JSON/JSONL,
HTML bundle, plain link list, and citation-bearing outputs.

## Adapter contract

Every EMVI-facing adapter must support, at minimum:
- capability discovery
- search or list
- open
- preview
- capture
- inspect
- act
- cancel
- replay or re-open provenance

Every adapter must also disclose:
- supported trust classes
- session/auth requirements
- degraded-mode behavior
- latency or placement expectations
- anchor strategy or locator stability

## Anchor-resolution contract

Anchors are how captured knowledge survives drift.
The architecture requires multi-anchor resolution where appropriate.

Examples:
- page quote + DOM locator + heading path + content hash neighborhood
- file path + symbol path + line range + content hash
- terminal command id + output span + command hash + run timestamp
- graph result row id + query hash + selected field set

Anchor resolution should prefer stable structural anchors first, content-match
fallbacks second, and manual conflict surfacing when both fail.

## Host-boundary policy

By default EMVI preserves host ownership for:
- OS launcher and app switching unless user explicitly opts into replacement
- window cycling and workspace controls
- screen-reader and accessibility management
- terminal emulator management chords
- tmux prefix and copy-mode ownership
- browser chrome shortcuts
- editor insert-mode text entry and formatting shortcuts
- password fields and other sensitive raw-input surfaces

EMVI may mirror these actions in searchable form, but must not silently steal them.

## Cross-surface proof slice

The first proof slice must exercise the actual architecture rather than only the shell UI.
The required path is:
1. browse through local digital-twin UI runtime
2. capture a page into a collection
3. capture an editor snippet into the same collection
4. run and capture a guarded shell command plus output
5. query the graph façade
6. freeze everything into a snapshot
7. export the snapshot
8. inspect ledger/provenance for the entire flow

The acceptance gate is not “demo works.”
The acceptance gate is that one shell coordinates these surfaces while preserving:
- focus correctness
- trust-class correctness
- anchor stability
- collection membership correctness
- provenance completeness
- host-boundary discipline

## Implementation guidance

The first implementation should not try to build every shell feature at once.
It should:
- respect pass-through ownership aggressively
- implement only the proof-slice grammar subset first
- produce execution plans before any side effects
- log parse, focus, routing, and provenance events from day one
- validate each adapter against the service-family contract

## Relationship to the rest of sociosphere

This subtree is intentionally documentation-first.
It should guide implementation in downstream component or protocol repos, and
then be refined as the proof slice hardens.

Until the proof slice is live, these docs should be treated as draft architecture
with explicit implementation pressure still pending.
