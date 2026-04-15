# Canonical encoding and signatures

## Purpose
Freeze the normative serialization and signing profile for fabric control objects before implementation fans out.

This document applies to:
- `manifest.v1`
- `indexpack.v1`
- `ManifestDelta`
- `IndexDelta`
- `CapabilityGrant`
- quorum proposal / approval / commit objects
- evidence and audit envelopes when marked `signed=true`

## Design choice summary
### Canonical object encoding
Long-lived normative objects use:
- canonical JSON as the source-of-truth representation
- UTF-8 bytes
- deterministic key ordering
- no insignificant whitespace

### Feed/event transport
Streaming feeds use:
- NDJSON where each line is one canonical JSON object
- object digests computed over each line's canonical JSON payload only

### Binary payloads
Large binary payloads are never embedded in canonical signed objects.
They are referenced by:
- `object_id`
- `object_version`
- content hash
- optional size and mime metadata

### Optional transport optimization
CBOR or other compact transport encodings MAY be used on the wire for efficiency, but the canonical digest and signature base MUST still be derived from the canonical JSON representation.

## Canonical JSON rules
The canonicalization profile MUST enforce:
- UTF-8 encoding
- object keys sorted lexicographically by code point
- arrays preserved in semantically defined order only
- numbers rendered deterministically; avoid floats where exact integer/fixed-point forms are available
- booleans and null rendered with standard JSON literals
- no duplicate keys
- no comments
- no trailing commas

## Digest rules
Default digest algorithm:
- `sha256`

For every signed object, compute:
1. canonical JSON bytes
2. `sha256(canonical_bytes)`
3. detached signature over the digest or over the canonical bytes, but the profile must be consistent per object class

## Signature algorithm choice
Default signature algorithm:
- `Ed25519`

Reasons:
- small keys and signatures
- broad open-source support
- good fit for offline/local-first environments
- simple detached-signature workflows

## Key hierarchy
### Cell root key
Used for:
- signing policy bundle releases
- signing quorum authority set updates
- signing trust-domain transitions

### Dataset signing key
Used for:
- release manifests
- immutable dataset releases
- delegated signing for dataset-specific objects

### Service/operator key
Used for:
- runtime-generated evidence objects
- mount-agent and connector executor signed events

### Quorum signer keys
Used for:
- approvals on high-impact governance actions

## Signature object shape
A detached signature object SHOULD include:
- `signature_id`
- `signed_object_type`
- `signed_object_id`
- `signer_key_id`
- `signature_algorithm`
- `digest_algorithm`
- `digest`
- `signature`
- `signed_at`

## Signing requirements by object class
### `manifest.v1`
Sign:
- `manifest_id`
- `root_hash`
- `dataset_ref`
- `policy_bundle_ref`
- `created_at`

### `indexpack.v1`
Sign:
- `indexpack_id`
- `manifest_id`
- `pipeline_version`
- `created_at`

### `CapabilityGrant`
Sign:
- `grant_id`
- `principal`
- `mount_ref`
- `rights`
- `network_profile`
- `expires_at`

### Quorum objects
- proposals MAY be unsigned at creation but SHOULD become signed before review in hostile environments
- approvals MUST be signed
- commits MUST be signed by the controller/service applying the change and SHOULD reference the satisfied approvals

## Replay and anti-tamper guidance
Every signed object SHOULD support:
- monotonic or nonce-based replay protection where applicable
- explicit expiry for grants and approvals
- correlation to prior object/version where mutation is involved

## Implementation guidance
- canonicalize once, hash once, sign once
- persist canonical bytes or exact digest inputs for audit reproducibility
- reject objects that cannot be round-tripped to canonical JSON without semantic change

## Open decisions
- whether to sign canonical bytes directly or sign the digest uniformly across all object classes
- whether to adopt multi-signature aggregation for quorum commits or keep detached individual approval signatures plus a signed commit summary
