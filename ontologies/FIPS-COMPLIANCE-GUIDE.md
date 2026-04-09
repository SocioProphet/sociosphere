# FIPS 140-2/140-3 Compliance Guide
## SocioProphet/sociosphere — Workspace Controller

**Version:** 1.0.0  
**Date:** 2026-04-05  
**Authority:** NIST SP 800-53 Rev. 5, FIPS 140-2/140-3, NIST SP 800-207, NIST SP 800-88  
**Status:** Active

---

## 1. Executive Summary

The sociosphere workspace controller operates as a government-grade orchestration layer requiring full FIPS 140-2/140-3 cryptographic compliance and a zero-trust security posture per NIST SP 800-207. This guide defines the cryptographic standards, NIST 800-53 control mappings, audit trail requirements, and ongoing compliance obligations for all maintainers and integrators.

All cryptographic operations MUST use FIPS-validated modules. All inter-service communication MUST enforce TLS 1.3 or later. All privileged operations MUST require multi-factor authentication and produce immutable, hash-chained audit records.

**Scope:** This guide applies to:
- The sociosphere workspace controller runtime
- All protocol bindings (TriTRPC, OIDC, mTLS)
- Artifact signing and supply chain operations
- CI/CD pipeline integrations

---

## 2. Cryptographic Standards

### 2.1 Approved Algorithms

| Category | Algorithm | Standard | Notes |
|---|---|---|---|
| Symmetric Encryption | AES-256-GCM | FIPS 197, SP 800-38D | Authenticated encryption; nonce MUST be unique per key |
| Digital Signature | ECDSA-P256 | FIPS 186-5 | Minimum curve; P-384 or P-521 preferred for long-term keys |
| Key Derivation | HKDF-SHA-256 | RFC 5869, FIPS 198-1 | Extract-then-Expand construction |
| Message Digest | SHA-256, SHA-384, SHA-512 | FIPS 180-4 | SHA-1 is disallowed (see §2.2) |
| Key Agreement | ECDH-P256 | SP 800-56A | Combined with HKDF for session key derivation |
| MAC | HMAC-SHA-256 | FIPS 198-1 | Minimum 256-bit output |
| Random Number Generation | CTR_DRBG (AES-256) | SP 800-90A | FIPS-validated entropy source required |

### 2.2 Disallowed Algorithms

The following algorithms MUST NOT be used in any production code path:

- **MD5** — broken; no collision resistance
- **SHA-1** — deprecated by NIST (SP 800-131A)
- **DES / 3DES** — disallowed after 2023 (SP 800-131A)
- **RC4** — stream cipher; cryptographically broken
- **ECB mode** (any block cipher) — deterministic; leaks plaintext patterns
- **RSA < 2048-bit** — insufficient key length
- **Diffie-Hellman < 2048-bit** — insufficient group size

### 2.3 Key Management

Key management MUST comply with NIST SP 800-57 Parts 1–3:

1. **Key Generation** — Use a FIPS-validated DRBG seeded from a hardware entropy source.
2. **Key Storage** — Keys at rest MUST be encrypted with AES-256-GCM using a key-encryption-key (KEK) stored in a Hardware Security Module (HSM) or cloud KMS with FIPS 140-2 Level 2+ validation.
3. **Key Distribution** — Use ECDH-P256 + HKDF-SHA-256 for ephemeral session key establishment. Never transmit raw private keys over a network.
4. **Key Rotation** — Symmetric keys MUST be rotated at least every 90 days. Asymmetric keys MUST be rotated at least annually.
5. **Key Destruction** — Follow NIST SP 800-88 media sanitization guidance. Overwrite key material with cryptographically random data before deallocation.
6. **Key Escrow** — Escrow is prohibited except where required by law, and only with explicit policy documentation.

### 2.4 TLS Requirements

Per RFC 8446 and NIST SP 800-52 Rev. 2:

- **Minimum version:** TLS 1.3 — TLS 1.0, 1.1, and 1.2 are disallowed.
- **Cipher suites (TLS 1.3):**
  - `TLS_AES_256_GCM_SHA384`
  - `TLS_CHACHA20_POLY1305_SHA256`
- **Certificate:** ECDSA-P256 or RSA-2048+ signed by a FIPS-compliant CA.
- **Certificate Pinning:** Required for all inter-service mTLS connections.
- **OCSP Stapling:** MUST be enabled.
- **Session Resumption:** Session tickets MUST be rotated within 24 hours.

---

## 3. NIST SP 800-53 Rev. 5 Control Mappings

### 3.1 Access Control (AC)

#### AC-2: Account Management
- Implement automated provisioning and de-provisioning via OIDC claims.
- Enforce principle of least privilege: each service account has exactly the permissions it needs.
- Review all accounts quarterly; disable unused accounts within 24 hours of departure.
- Audit log every account creation, modification, and deletion event.

**Evidence:** OIDC token claims, account lifecycle audit records, quarterly review attestation.

#### AC-3: Access Enforcement
- All API endpoints enforce RBAC policies derived from OIDC JWT `roles` claims.
- Zero-trust micro-segmentation: no implicit trust between workspace components.
- Network policies enforce allow-list-only communication patterns.

**Evidence:** Network policy manifests, RBAC configuration, access decision audit records.

### 3.2 Audit and Accountability (AU)

#### AU-2: Event Logging
Auditable events include but are not limited to:
- Authentication success and failure
- Authorization decisions (allow and deny)
- Manifest fetch operations
- Build execution start, completion, and failure
- Key management operations
- Configuration changes
- Privileged command execution

#### AU-12: Audit Record Generation
- Every auditable event MUST produce a structured JSON audit record (see §5).
- Audit records MUST be written to an append-only, WORM-compliant storage backend.
- Each record MUST carry a cryptographic hash of the previous record (hash chain).
- Each record MUST carry an RFC 3161 trusted timestamp.

**Evidence:** Audit log samples, hash chain verification reports, WORM storage configuration.

### 3.3 Identification and Authentication (IA)

#### IA-2: Identification and Authentication (Organizational Users)
- All human users MUST authenticate via OIDC with a FIPS-approved identity provider.
- Privileged operations (build execution, key management, configuration changes) MUST require MFA:
  - TOTP (RFC 6238) using a FIPS-validated TOTP implementation, OR
  - Hardware token (FIDO2/WebAuthn with FIPS-validated authenticator)
- Service-to-service authentication MUST use mTLS with ECDSA-P256 certificates.

#### IA-5: Authenticator Management
- Passwords, if used, MUST be at least 16 characters and hashed with Argon2id (memory: 64 MiB, iterations: 3, parallelism: 4).
- TOTP secrets MUST be stored encrypted with AES-256-GCM in the HSM-backed key store.
- Certificate private keys MUST reside in an HSM or cloud KMS; never in plain-text files.
- Credential rotation intervals: passwords ≤ 90 days, certificates ≤ 1 year.

### 3.4 System and Communications Protection (SC)

#### SC-7: Boundary Protection
- All ingress and egress traffic traverses an application-layer gateway with TLS termination inspection.
- Inter-service communication uses a service mesh with mTLS enforcement.
- Egress allow-lists MUST be maintained and reviewed monthly.

#### SC-8: Transmission Confidentiality and Integrity
- All data in transit MUST be protected with TLS 1.3 (see §2.4).
- Integrity is enforced via AEAD cipher suites (AES-256-GCM).

#### SC-12: Cryptographic Key Establishment and Management
- Implements the key management lifecycle described in §2.3.
- Key custodian roles are defined with documented separation of duties.

### 3.5 System and Information Integrity (SI)

#### SI-7: Software, Firmware, and Information Integrity
- All build artifacts MUST be signed with ECDSA-P256 (see §4.3).
- SBOM (Software Bill of Materials) MUST be generated in CycloneDX or SPDX format for every release.
- Vulnerability scanning MUST run in CI/CD and block release on critical CVEs.
- Container images MUST be pulled by digest, not by mutable tag.

**Evidence:** Artifact signatures, SBOM files, vulnerability scan reports, digest-pinned manifests.

---

## 4. Zero-Trust Architecture (NIST SP 800-207)

### 4.1 Core Principles

The sociosphere workspace controller implements zero-trust per NIST SP 800-207 §3:

1. **All resources are treated as if on an untrusted network.** No implicit trust based on network location.
2. **Access is granted on a per-session, per-request basis.** Tokens are short-lived (≤ 15 minutes for privileged operations).
3. **Access is determined by dynamic policy.** Policy engine evaluates user identity, device posture, and request context on every call.
4. **All communication is authenticated and encrypted.** TLS 1.3 + mTLS for service-to-service; OIDC JWT for user sessions.
5. **Integrity and security posture of all assets is monitored.** Continuous telemetry feeds the policy engine.

### 4.2 Binding Types

Two interaction binding types are defined (see `zero-trust-govt-bindings.jsonld`):

- **ManifestFetchBinding** — Read-only, low-risk. Requires OIDC + cryptographic signature. Rate-limited.
- **BuildExecutionBinding** — Critical, high-risk. Requires OIDC + MFA + cryptographic binding. Immutable audit trail with RFC 3161 timestamps.

### 4.3 Artifact Signing

Every build artifact undergoes the following signing workflow:

```
1. Compute SHA-256 digest of artifact bytes.
2. Sign digest with ECDSA-P256 private key (HSM-resident).
3. Attach signature and signing certificate to artifact manifest.
4. Record signing event in immutable audit log (§5).
5. Publish artifact with digest-based addressing only.
```

Verification at deploy time:
```
1. Retrieve artifact by digest.
2. Fetch signing certificate from trust store.
3. Verify ECDSA-P256 signature over SHA-256 digest.
4. Verify signing certificate chain to root CA.
5. Reject artifact if any verification step fails.
```

---

## 5. Immutable Audit Trail (NIST SP 800-88)

### 5.1 Audit Record Schema

Every audit event MUST be a JSON object with the following fields:

```json
{
  "event_id": "<uuid-v4>",
  "timestamp": "<RFC 3339 UTC>",
  "timestamp_tsa": "<RFC 3161 TSA token, base64>",
  "event_type": "<string: e.g. manifest.fetch, build.execute>",
  "actor": {
    "sub": "<OIDC subject>",
    "iss": "<OIDC issuer>",
    "mfa_method": "<totp|hardware_token|null>"
  },
  "resource": "<URN or URL of the resource>",
  "action": "<read|write|execute|admin>",
  "outcome": "<success|failure|denied>",
  "previous_hash": "<SHA-256 hex of previous record>",
  "record_hash": "<SHA-256 hex of this record (excluding record_hash field)>",
  "signature": "<ECDSA-P256 signature over record_hash, base64>"
}
```

### 5.2 Storage Requirements

- **WORM (Write Once, Read Many):** Audit logs MUST be stored in WORM-compliant storage (e.g., AWS S3 Object Lock, Azure Immutable Blob Storage, or a hardware WORM device).
- **Retention:** Minimum 3-year retention, with at least 1 year in immediately accessible (hot) storage.
- **Encryption at Rest:** AES-256-GCM with HSM-resident KEK.
- **Replication:** Logs MUST be replicated to at least one geographically separate location.
- **Hash Chain Verification:** The hash chain MUST be verified weekly by an automated process that reports any break in the chain.

### 5.3 Non-Repudiation

Every BuildExecutionBinding event MUST carry:
- An ECDSA-P256 digital signature over the audit record, proving the actor's identity.
- An RFC 3161 trusted timestamp from an accredited TSA, proving the time of the event.

These two elements together provide cryptographic non-repudiation: the actor cannot plausibly deny having performed the action.

---

## 6. Ongoing Compliance Calendar

### Continuous (Every Commit)
- CI/CD runs `fips-compliance-checker.py` (§7).
- Vulnerability scan blocks release on critical CVEs.
- Artifact signing is performed automatically.

### Weekly
- Automated hash chain verification on audit logs.
- Certificate expiry monitoring alert (warn at 30 days).

### Monthly
- Egress allow-list review.
- Service account access review.
- Dependency update review (check for newly disclosed CVEs).

### Quarterly
- Full NIST 800-53 control evidence collection.
- Key rotation for symmetric keys.
- MFA enrollment audit (ensure all privileged users enrolled).
- Penetration testing of externally accessible endpoints.

### Annually
- FIPS cryptographic module certification review.
- Full key rotation (asymmetric keys).
- Third-party compliance audit.
- Update this guide and all related ontologies to reflect changes in NIST guidance.

---

## 7. FIPS Compliance Checker

The automated compliance checker is located at `tools/validator/fips-compliance-checker.py`. It performs the following checks:

| Check | Description | Fail Condition |
|---|---|---|
| `algo-scan` | Scan source for disallowed algorithms | Any match of MD5, SHA-1, DES, 3DES, RC4, ECB |
| `tls-version` | Validate TLS configuration | TLS version < 1.3 configured anywhere |
| `audit-worm` | Check audit trail for WORM configuration | No WORM storage policy found |
| `hash-chain` | Verify audit log hash chain integrity | Any record's hash does not match next record's `previous_hash` |
| `nist-controls` | Spot-check NIST 800-53 control evidence | Missing required evidence files |

Run as part of CI:
```bash
python tools/validator/fips-compliance-checker.py --report compliance-report.json
```

Exit code 0 = all checks pass. Exit code 1 = one or more failures. The report is written as a structured JSON file suitable for archiving as compliance evidence.

---

## 8. Cross-Repository References

This document is cross-linked with:

| Repository | Artifact | Purpose |
|---|---|---|
| `SocioProphet/sociosphere` | `docs/GLOSSARY-FIPS.md` | Controlled FIPS/NIST vocabulary |
| `SocioProphet/sociosphere` | `ontologies/sociosphere-fips-schema.jsonld` | JSON-LD formal ontology |
| `SocioProphet/sociosphere` | `ontologies/sociosphere-fips.ttl` | RDF/Turtle semantic representation |
| `SocioProphet/sociosphere` | `ontologies/zero-trust-govt-bindings.jsonld` | Zero-trust binding specifications |
| `SocioProphet/sociosphere` | `protocol/tritrpc-fips-spec.md` | TriTRPC FIPS framework specification |
| `SocioProphet/sociosphere` | `tools/validator/fips-compliance-checker.py` | Automated compliance validation |
| `SocioProphet/socioprophet-standards-storage` | `standards/fips-compliance/INDEX.md` | Master FIPS standards index |
| `SocioProphet/socioprophet-standards-storage` | `standards/nist-800-53/control-mappings.md` | NIST control implementation matrix |

---

## 9. Normative References

- **FIPS 140-2/140-3:** [Cryptographic Module Validation Program](https://csrc.nist.gov/projects/cryptographic-module-validation-program/)
- **FIPS 186-5:** Digital Signature Standard (DSS)
- **FIPS 197:** Advanced Encryption Standard (AES)
- **FIPS 198-1:** The Keyed-Hash Message Authentication Code (HMAC)
- **NIST SP 800-38D:** Recommendation for Block Cipher Modes of Operation: GCM and GMAC
- **NIST SP 800-52 Rev. 2:** Guidelines for TLS Implementations
- **NIST SP 800-53 Rev. 5:** Security and Privacy Controls for Information Systems
- **NIST SP 800-56A:** Recommendation for Pair-Wise Key-Establishment Schemes Using DH
- **NIST SP 800-57 Parts 1–3:** Recommendation for Key Management
- **NIST SP 800-88 Rev. 1:** Guidelines for Media Sanitization
- **NIST SP 800-90A:** Recommendation for Random Number Generation Using DRBGs
- **NIST SP 800-131A Rev. 2:** Transitioning the Use of Cryptographic Algorithms and Key Lengths
- **NIST SP 800-207:** Zero Trust Architecture
- **RFC 3161:** Internet X.509 PKI Time-Stamp Protocol (TSP)
- **RFC 5869:** HMAC-based Extract-and-Expand Key Derivation Function (HKDF)
- **RFC 6238:** TOTP: Time-Based One-Time Password Algorithm
- **RFC 8446:** The Transport Layer Security (TLS) Protocol Version 1.3
