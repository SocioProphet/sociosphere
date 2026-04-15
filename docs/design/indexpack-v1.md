# indexpack.v1

## Purpose
`indexpack.v1` is the portable bundle of derived retrieval state associated with a specific `manifest.v1` root.

## Invariants
- every indexpack binds to exactly one `manifest_id`
- indexpacks are rebuildable from canonical objects + pipeline definition
- indexpacks may be exported without raw objects when policy permits

## Required fields
- `schema_version`: `indexpack.v1`
- `indexpack_id`
- `manifest_id`
- `pipeline_version`
- `created_at`
- `created_by`
- `chunk_sets[]`
- `embedding_sets[]`
- `keyword_index_refs[]`
- `provenance`

## Chunk set
Each chunk record includes:
- `chunk_id`
- `object_id`
- `object_version`
- `byte_range` or logical segment ref
- `text_hash`
- `classification_tags[]`

## Embedding set
Each embedding record includes:
- `embedding_id`
- `chunk_id`
- `model_id`
- `vector_dim`
- `storage_ref`
- optional `redaction_profile`

## Keyword index refs
May include:
- local sqlite/fts path ref
- tantivy/lucene segment ref
- exported postings bundle ref

## Provenance
Must describe:
- source `manifest_id`
- extraction policy version
- chunking policy version
- embedding model id/version
- indexing tool/runtime id

## Export modes
- `local_only`
- `portable_bundle`
- `mesh_export`

## Security note
Embedding export MAY leak semantic content. `high_threat` policy SHOULD require explicit allow before exporting embedding sets outside the authoritative cell.
