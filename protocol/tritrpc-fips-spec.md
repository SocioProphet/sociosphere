# TriTRPC FIPS Compliance Specification
## SocioProphet/sociosphere — Protocol Layer

**Version:** 1.0.0  
**Date:** 2026-04-05  
**Authority:** FIPS 140-2/140-3, NIST SP 800-53 Rev. 5, NIST SP 800-207, RFC 8446  
**Status:** Active  
**Related:** `ontologies/FIPS-COMPLIANCE-GUIDE.md`, `ontologies/zero-trust-govt-bindings.jsonld`

---

## 1. Overview

TriTRPC is the workspace-internal RPC framework used by the sociosphere workspace controller for all inter-component communication. This specification defines the mandatory FIPS 140-2/140-3 compliance requirements for every TriTRPC implementation, transport configuration, and procedure definition.

All TriTRPC implementations MUST conform to the cryptographic algorithm policy in §2, the transport configuration in §3, the authentication and authorization bindings in §4, the audit event specification in §5, and the supply chain integrity requirements in §6.

---

## 2. Cryptographic Requirements

### 2.1 Approved Algorithms

TriTRPC MUST use only the following algorithms. Use of any other algorithm in a TriTRPC call path is a compliance violation.

| Purpose | Approved Algorithm | FIPS Reference |
|---|---|---|
| Symmetric encryption | AES-256-GCM | FIPS 197, SP 800-38D |
| Digital signature | ECDSA-P256 | FIPS 186-5 |
| Key derivation | HKDF-SHA-256 | RFC 5869, FIPS 198-1 |
| Message digest | SHA-256 (minimum) | FIPS 180-4 |
| MAC | HMAC-SHA-256 | FIPS 198-1 |
| Key agreement | ECDH-P256 | SP 800-56A |
| CSPRNG | CTR_DRBG (AES-256) | SP 800-90A |
| Password hashing | Argon2id | RFC 9106 |

### 2.2 Disallowed Algorithms

The following algorithms MUST NOT appear anywhere in the TriTRPC call path, including in library dependencies that are transitively invoked:

```
DISALLOWED:
  - MD5 (any use: HMAC-MD5, PBKDF-MD5, file checksums)
  - SHA-1 (any use: HMAC-SHA1, certificate signatures, Git commits used as security identifiers)
  - DES (all modes)
  - 3DES / TDEA (all modes; disallowed after 2023 per SP 800-131A)
  - RC4 (stream cipher; broken)
  - AES-ECB (deterministic; leaks plaintext patterns)
  - AES-CBC without explicit padding validation (CBC padding oracle risk)
  - RSA with key size < 2048 bits
  - DSA (deprecated; ECDSA is the approved successor)
  - Diffie-Hellman with group size < 2048 bits
```

The automated compliance checker (`tools/validator/fips-compliance-checker.py`) enforces this list on every CI run.

### 2.3 Algorithm Agility Restriction

TriTRPC MUST NOT negotiate cryptographic algorithms at runtime with external callers. The algorithm suite is fixed at compile time. Algorithm negotiation interfaces that could be downgraded to disallowed algorithms are prohibited.

### 2.4 Entropy Sources

All TriTRPC nonces, session IDs, and key material MUST be derived from a FIPS-validated CSPRNG (`CTR_DRBG` seeded from a hardware entropy source). Use of `Math.random()`, `rand()`, or any non-cryptographic PRNG for security-relevant values is prohibited.

---

## 3. Transport Layer Requirements

### 3.1 TLS Configuration

All TriTRPC connections MUST use TLS 1.3 (RFC 8446). Earlier TLS versions are disallowed.

**Required TLS 1.3 cipher suites:**
```
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
```

**Prohibited:**
```
TLS 1.0, TLS 1.1, TLS 1.2 (all)
SSL 2.0, SSL 3.0 (all)
TLS_RSA_* (static RSA key exchange; no forward secrecy)
Any cipher suite with NULL, EXPORT, anon, RC4, DES, or 3DES
```

**Additional requirements:**
- OCSP stapling MUST be enabled on all TLS certificates.
- Session tickets MUST be rotated within 24 hours to limit session resumption exposure.
- Certificate revocation MUST be checked on every connection establishment.

### 3.2 Mutual TLS (mTLS) for Privileged Procedures

TriTRPC procedures classified as `privileged` or `critical` (see §4.2) MUST additionally require mutual TLS:
- The client MUST present an ECDSA-P256 certificate issued by the workspace's internal CA.
- The server MUST verify the client certificate chain to the pinned root CA.
- Certificate serial numbers of actively used client certificates MUST be recorded in the audit log.

### 3.3 Certificate Management

- All TriTRPC TLS certificates MUST use ECDSA-P256 keys.
- Certificate validity MUST NOT exceed 397 days.
- Certificates MUST be rotated at least 30 days before expiration.
- Root CA private keys MUST reside in an HSM (FIPS 140-2 Level 2+).

---

## 4. Authentication and Authorization Bindings

### 4.1 OIDC Token Requirements

Every TriTRPC request MUST carry a valid OIDC JWT bearer token with the following requirements:

```
Required claims:
  sub    - Subject identifier (stable, unique per user)
  iss    - Issuer (pinned to the workspace identity provider)
  aud    - Audience (must include the TriTRPC service identifier)
  exp    - Expiration (must not be in the past; max age 900 seconds for standard ops)
  iat    - Issued at (used for clock skew validation; tolerance ≤ 30 seconds)

Required for privileged operations:
  acr    - Authentication context class reference
  amr    - Authentication methods references (must include 'mfa' value)
```

OIDC token signing algorithm MUST be `ES256` (ECDSA-P256 + SHA-256). Tokens signed with `RS256`, `HS256`, or any other algorithm MUST be rejected.

### 4.2 Procedure Risk Classification

Each TriTRPC procedure MUST be assigned one of the following risk levels in its procedure definition:

| Risk Level | Description | Auth Required |
|---|---|---|
| `read-only` | Non-mutating, low-sensitivity reads | OIDC JWT |
| `standard` | Mutating operations, non-critical resources | OIDC JWT |
| `privileged` | Mutating operations on security-relevant resources | OIDC JWT + mTLS |
| `critical` | Build execution, key management, configuration changes | OIDC JWT + MFA + mTLS + request signing |

### 4.3 MFA Requirements for Critical Procedures

Procedures classified as `critical` MUST enforce multi-factor authentication:

1. The OIDC JWT `amr` claim MUST include one of:
   - `totp` — TOTP per RFC 6238, HMAC-SHA-256, 30-second window
   - `hwk` — Hardware token (FIDO2/WebAuthn) with attestation
2. The `acr` claim MUST be `urn:mace:incommon:iap:silver` or higher.
3. MFA MUST have been performed within 900 seconds of the request.
4. If MFA age exceeds 900 seconds, the caller MUST re-authenticate before the procedure is invoked.

### 4.4 Request Signing for Critical Procedures

Procedures classified as `critical` MUST carry a cryptographic request signature:

```
Signed payload fields (concatenated in canonical order):
  actor.sub | resource | action | timestamp_iso8601 | nonce_hex

Signature:
  algorithm: ECDSA-P256
  hash: SHA-256
  key: subject's registered signing key (HSM-resident)

Transmission:
  X-TriTRPC-Signature: <base64url(signature)>
  X-TriTRPC-Nonce: <hex(32-byte random nonce)>
  X-TriTRPC-Timestamp: <RFC 3339 UTC timestamp>
```

Nonces MUST be stored for 1 hour and rejected if replayed.

---

## 5. Audit Event Specification

### 5.1 Audit Record Format

Every TriTRPC procedure invocation MUST generate an audit record in the following JSON format:

```json
{
  "event_id": "<uuid-v4>",
  "timestamp": "<RFC 3339 UTC>",
  "timestamp_tsa": "<RFC 3161 TSA token, base64, critical procedures only>",
  "procedure": "<fully-qualified procedure name>",
  "risk_level": "<read-only|standard|privileged|critical>",
  "actor": {
    "sub": "<OIDC subject>",
    "iss": "<OIDC issuer>",
    "mfa_method": "<totp|hardware_token|null>",
    "mfa_age_seconds": "<integer|null>",
    "client_cert_serial": "<hex serial|null>"
  },
  "request": {
    "nonce": "<hex, critical only>",
    "signature": "<base64url, critical only>",
    "source_ip": "<IPv4 or IPv6>"
  },
  "resource": "<URN or URL>",
  "action": "<read|write|execute|admin>",
  "outcome": "<success|failure|denied>",
  "error_code": "<string|null>",
  "artifact_digest": "<sha256:<hex>, critical only>",
  "previous_hash": "<SHA-256 hex of previous record in chain>",
  "record_hash": "<SHA-256 hex of this record, excluding record_hash field>",
  "signature": "<ECDSA-P256 signature over record_hash, base64, critical only>"
}
```

### 5.2 Hash Chain Construction

```
record_hash = SHA-256(JSON.stringify(record_without_record_hash_field))
previous_hash_of_next_record = record_hash
```

The hash chain forms a tamper-evident linked list. Any modification to a historical record will invalidate all subsequent hashes. Verification MUST be performed weekly by the automated hash chain verifier.

### 5.3 RFC 3161 Timestamps

For `critical` procedures:
1. Compute `record_hash` as defined in §5.2.
2. Submit `record_hash` to the configured RFC 3161 Timestamp Authority (TSA).
3. Store the TSA token in the `timestamp_tsa` field.
4. Verify the TSA token on retrieval.

The TSA MUST be an accredited provider trusted by the workspace's PKI.

### 5.4 Audit Storage Requirements

Audit records MUST be written to WORM-compliant storage before the procedure response is returned to the caller. A procedure MUST NOT return success if audit record creation fails.

Storage requirements:
- WORM-compliant (append-only; no modification or deletion)
- Encrypted at rest with AES-256-GCM (HSM-resident KEK)
- Minimum 3-year retention (7 years for `critical` procedure records)
- Replicated to at least one geographically separate location

---

## 6. Artifact Signing and Supply Chain Integrity

### 6.1 Build Artifact Signing

Every artifact produced by a build execution procedure MUST be signed:

```
1. Compute SHA-256 digest of artifact bytes.
2. Sign digest with the workspace build signing key (ECDSA-P256, HSM-resident).
3. Produce a signature bundle:
   {
     "artifact_digest": "sha256:<hex>",
     "signed_at": "<RFC 3339 UTC>",
     "signer": "<signing certificate subject DN>",
     "signature": "<base64url(ECDSA-P256 signature)>",
     "signing_cert_pem": "<PEM>"
   }
4. Attach signature bundle to artifact manifest.
5. Record artifact_digest and signer in the audit log (§5.1).
```

### 6.2 Artifact Verification

Before deploying any artifact, the deployer MUST:

```
1. Retrieve artifact by SHA-256 digest (not by mutable tag).
2. Load signing certificate from trust store; verify chain to root CA.
3. Verify ECDSA-P256 signature over SHA-256 digest.
4. Verify signing_cert_pem has not been revoked (OCSP or CRL).
5. Verify signed_at is within the certificate's validity period.
6. Reject artifact and abort deployment on any verification failure.
```

### 6.3 Software Bill of Materials (SBOM)

Every TriTRPC service release MUST include an SBOM:
- Format: CycloneDX 1.4+ (preferred) or SPDX 2.3+
- Scope: All direct and transitive dependencies
- Content: Package name, version, PURL, license, known CVEs at time of release
- Signing: SBOM document MUST be signed with the same ECDSA-P256 build signing key

### 6.4 Vulnerability Scanning

CI/CD MUST run a vulnerability scan on every build:
- Scanner MUST check all SBOM dependencies against NVD CVE database.
- Build MUST fail if any dependency has a CVE with CVSS score ≥ 7.0 (high or critical).
- Exceptions MUST be documented in a signed exception record with justification and remediation timeline.

### 6.5 Dependency Pinning

All dependencies MUST be pinned by cryptographic digest (not by version tag):
- Container images: `image@sha256:<hex>`
- npm/pip/go: lock files with integrity hashes committed to the repository
- Git submodules: pinned by commit SHA (not branch ref)

---

## 7. Error Handling and Failure Modes

### 7.1 Cryptographic Failure

If a cryptographic operation fails (signature verification, decryption, MAC check):
- Return a generic error code. Do not reveal which specific check failed.
- Log a detailed audit record with `outcome: failure` and `error_code: CRYPTO_FAILURE`.
- Alert the security monitoring system.
- Do not cache or retry the failed operation without a fresh authentication.

### 7.2 Audit Write Failure

If the audit record cannot be written to WORM storage:
- Abort the procedure; return an error to the caller.
- Do NOT proceed with the requested operation.
- Alert the security monitoring system immediately.
- Implementing systems MUST treat audit availability as a safety prerequisite.

### 7.3 MFA Timeout

If MFA age exceeds 900 seconds for a `critical` procedure:
- Return `HTTP 401` with `WWW-Authenticate: OIDC step-up`.
- The caller MUST re-authenticate before retrying.
- Do NOT grant access based on a stale MFA token.

---

## 8. Implementation Checklist

Implementors MUST verify all items before marking a TriTRPC service as FIPS-compliant:

- [ ] All cryptographic operations use only algorithms from §2.1
- [ ] No disallowed algorithms appear in §2.2 (verified by `fips-compliance-checker.py`)
- [ ] TLS 1.3 is the minimum version; no TLS 1.2 or earlier fallback
- [ ] mTLS is enforced for `privileged` and `critical` procedures
- [ ] OIDC JWT validation includes issuer pinning and algorithm restriction to ES256
- [ ] MFA is enforced for `critical` procedures (TOTP or hardware token)
- [ ] Request signing is implemented for `critical` procedures
- [ ] Nonce replay protection is active (1-hour window)
- [ ] Audit records are written before returning success
- [ ] WORM storage is configured for audit logs
- [ ] Hash chain verification runs weekly
- [ ] RFC 3161 timestamps are collected for `critical` procedure audit records
- [ ] Build artifacts are signed with ECDSA-P256
- [ ] Artifact verification is enforced at deploy time
- [ ] SBOM is generated and signed for every release
- [ ] Vulnerability scanning blocks release on CVSS ≥ 7.0 findings

---

## 9. Normative References

- **FIPS 140-2/140-3:** Cryptographic Module Validation Program — https://csrc.nist.gov/projects/cryptographic-module-validation-program/
- **FIPS 186-5:** Digital Signature Standard
- **FIPS 197:** Advanced Encryption Standard
- **FIPS 198-1:** The Keyed-Hash Message Authentication Code
- **NIST SP 800-38D:** GCM Mode of Operation
- **NIST SP 800-52 Rev. 2:** TLS Implementation Guidelines
- **NIST SP 800-53 Rev. 5:** Security and Privacy Controls — https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
- **NIST SP 800-56A:** Key-Establishment Schemes
- **NIST SP 800-57 Parts 1–3:** Key Management Recommendations
- **NIST SP 800-88 Rev. 1:** Media Sanitization — https://csrc.nist.gov/publications/detail/sp/800-88
- **NIST SP 800-90A:** DRBG Recommendation
- **NIST SP 800-131A Rev. 2:** Cryptographic Algorithm Transitions
- **NIST SP 800-207:** Zero Trust Architecture — https://csrc.nist.gov/publications/detail/sp/800-207
- **RFC 3161:** Time-Stamp Protocol — https://tools.ietf.org/html/rfc3161
- **RFC 5869:** HKDF — https://tools.ietf.org/html/rfc5869
- **RFC 6238:** TOTP — https://tools.ietf.org/html/rfc6238
- **RFC 8446:** TLS 1.3 — https://tools.ietf.org/html/rfc8446
- **RFC 9106:** Argon2 — https://tools.ietf.org/html/rfc9106
- **ontologies/FIPS-COMPLIANCE-GUIDE.md** — Sociosphere compliance guide
- **ontologies/zero-trust-govt-bindings.jsonld** — Zero-trust binding catalog
