# EMVI Universal Object Model

Status: Draft v0.1

## Purpose

This document defines the shell-facing noun system so browser tabs, URLs, pages,
file ranges, snippets, terminal commands, outputs, graph rows, collections, and
snapshots can be handled by one operator shell without ad hoc per-surface logic.

## Top-level kinds

### Resource
A typed thing that can be searched, previewed, opened, captured, inspected, or acted on.
Examples:
- page
- url
- browser_tab
- file
- folder
- symbol
- snippet
- terminal_command
- terminal_output
- graph_row
- service
- host

### Context
The active environment that resolves deictic references such as `current`,
`selection`, `recent`, and `here`.
Examples:
- current browser window
- current editor buffer
- current terminal pane
- current collection view
- current graph result set

### Collection
A mutable working set of typed members. Collections are used for research,
curation, incident work, comparison, and summarization.

### Snapshot
An immutable freeze of a collection or live context. Snapshots are the stable
handoff/evidence/export unit.

### Annotation
An interpretation layer attached to one or more anchors. An annotation may hold
notes, claims, summaries, tags, rankings, relationships, or follow-up work.

### ActionSpec
A structured execution plan emitted after parsing but before side effects.
The ActionSpec is the execution contract between shell intent and service-family routing.

## Base fields

All shell-addressable objects should support, where applicable:
- `id` — stable identifier
- `kind` — object type
- `title` — human-oriented label
- `summary` — compact preview text
- `locators[]` — re-open or re-fetch routes
- `anchors[]` — intra-object stability points
- `provenance` — source, capture, and transformation metadata
- `capabilities[]` — what the object can do
- `relations[]` — graph or working-set relationships
- `lifecycle` — live, frozen, archived, missing, degraded
- `exportable` — whether and how the object may leave the system

## Identity / locator / anchor split

### Identity
What object is this?

### Locator
How do we re-open or re-fetch it?
Examples:
- URL
- file path
- service URI
- graph query identifier
- collection member reference

### Anchor
Where inside the object is the relevant portion?
Examples:
- quote + heading path
- file path + line range
- symbol path
- terminal output span
- graph row id + selected field set

## Collection membership

Collection membership is typed, not just string-based.
Each member should retain:
- object identity
- membership reason or capture intent
- collection-local note if present
- ordering/ranking metadata if present
- provenance of insertion into the collection

## Snapshot semantics

A Snapshot must be:
- immutable
- exportable
- replayable or inspectable later
- detached from future mutations in the source collection

## Annotation semantics

Annotations may attach to:
- a full object
- one or more anchors inside an object
- a set of related objects
- a collection or snapshot as a whole

## ActionSpec minimum fields

Every ActionSpec must include:
- normalized intent
- target objects
- routing service families
- trust class
- preview / review requirement
- confirmation requirement
- rollback availability
- provenance sink

## Design invariants

1. Collections are mutable; snapshots are immutable.
2. An annotation is not the same as a collection member.
3. A locator is not the same as an anchor.
4. The same shell command should operate over many resource kinds if capabilities match.
5. Every state-changing action must refer to typed objects, not only free text.
