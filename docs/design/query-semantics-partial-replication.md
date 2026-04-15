# Query semantics for partial and stale replication

## Purpose
Define what it means to query datasets when content and indexes are only partially replicated, stale, or mirror-only.

## Core rule
Every query result set MUST be labeled with its visibility and freshness posture.

## Visibility classes
- `authoritative_local`
- `local_partial`
- `stale_mirror`
- `remote_metadata_only`
- `hydrated_on_demand`

## Freshness classes
- `fresh`
- `bounded_stale`
- `unknown_stale`

## Planner inputs
The retrieval planner MUST consider:
- local `IndexRef` state (`WARMING | READY | DEGRADED`)
- local manifest generation
- remote mirror manifest generation if known
- connector lag metrics
- policy profile (`local_first`, `high_threat`, etc.)

## Default planner order in `local_first`
1. local authoritative ready index
2. local authoritative warming index with partial visibility
3. local stale mirror if policy allows stale reads
4. metadata-only results when content/index hydration is not allowed or unavailable
5. on-demand hydration only if connector and policy permit

## Result labeling
Each query response SHOULD include:
- `visibility_class`
- `freshness_class`
- `manifest_id_used`
- `index_id_used`
- optional `staleness_reason`

## Allowed behaviors by profile
### Normal
- may use bounded-stale mirrors
- may hydrate on demand through approved connectors

### High threat
- prefer local-only
- do not automatically hydrate from remote sources unless explicitly allowed
- metadata-only results may be preferable to remote pulls

### Airgap
- local-only
- no hydration from connectors

## Worked examples
### Example 1 — local partial index warming
A new mount is registered. Keyword index exists, embeddings are still warming.
- result visibility: `local_partial`
- freshness: `fresh`
- planner may answer lexical queries and limited chunk retrieval

### Example 2 — remote mirror only
Local node has only manifest and indexpack mirror, not raw objects.
- result visibility: `stale_mirror` or `remote_metadata_only`
- policy may allow metadata search but not content hydration

### Example 3 — connector unavailable
Last known remote mirror generation exists, but connector lag is unknown after partition.
- result visibility: `stale_mirror`
- freshness: `unknown_stale`
- response must label this clearly

## Follow-on implementation work
- confidence scoring tied to freshness/visibility
- UI and CLI surface for result labeling
- hydration prompts and operator overrides
