# Source Exposure Governance Standard v0.1

## Purpose

This standard controls what Sociosphere and downstream platform repositories may publish in public source, public release mirrors, community inner-source repositories, and restricted security/operations channels.

The goal is not secrecy for its own sake. The goal is to prevent public repositories from becoming a live, machine-readable attack graph against our own running systems while preserving auditable MIT-licensed release source, public standards, provenance, SBOMs, and security accountability.

This standard is the first implemented lane under the [Angel of the Lord Hardening Regime](../angel-of-the-lord/README.md).

## Core rule

Public source is allowed only after it is no longer privileged reconnaissance against our live systems.

Code visibility must never expose:

- current production topology;
- exact deployed commit/version mapping for live services;
- credentials, private keys, tokens, cookies, tenant identifiers, or customer context;
- unresolved exploitable security defects;
- exploit reproduction material before a patched release exists;
- raw telemetry, HAR, packet capture, or log material that reveals live service structure;
- CI/CD permissions, deployment paths, or operational gaps that enable a kill chain.

## Visibility tiers

| Tier | Meaning | Examples |
|---|---|---|
| `public_trust` | Public trust-building material that is safe before and after release. | Stable specs, high-level architecture, security policy, public governance, non-sensitive threat model summaries. |
| `public_release_mirror` | Hardened release snapshots that passed publication gates. | Tagged source releases, SBOMs, VEX, provenance, signed artifacts. |
| `community_inner_source` | Active development visible only to governed platform/community participants. | Work-in-progress implementation, unreleased branches, CI implementation details, non-sensitive test fixtures. |
| `restricted_security` | Security material requiring limited access and explicit disclosure handling. | Vulnerability reports, exploit repros, fuzz crashers, detection gaps, private advisories. |
| `restricted_operations` | Operational material that must not become public source. | Production topology, customer configs, cloud account layout, live deployed hashes, raw logs/HARs/traces. |

## Exposure classes

| Class | Default tier | Publication posture |
|---|---:|---|
| `source_text` | `community_inner_source` before release, `public_release_mirror` after gate | Publish as release snapshot only after checks pass. |
| `stable_protocol_spec` | `public_trust` | Public by default unless it embeds live topology or exploit detail. |
| `ci_workflow` | `community_inner_source` | Public only when token scopes, deploy paths, and operational internals are safe. |
| `dependency_manifest` | `community_inner_source` before release, `public_release_mirror` after gate | Public with SBOM/VEX after vulnerability triage. |
| `deployment_manifest` | `restricted_operations` | Public only as sanitized reference architecture. |
| `telemetry_log` | `restricted_operations` | Never public unless synthetically generated or fully sanitized. |
| `vulnerability_repro` | `restricted_security` | Private until remediation and disclosure gate complete. |
| `threat_model` | mixed | Public summary; implementation-sensitive appendix stays restricted. |

## Publication gate

A repository or release snapshot is publishable only when all required checks pass:

1. no blocked credential/secret indicators;
2. no blocked operational file paths;
3. no raw HAR, packet capture, private key, kubeconfig, Terraform state, or production `.env` files;
4. no live production topology, customer identifiers, or exact deployed hash mapping;
5. no unresolved exploitable critical/high vulnerability in released artifact context;
6. SBOM emitted for release artifacts;
7. VEX or equivalent exploitability decision emitted for known vulnerable components;
8. provenance/attestation emitted for release artifacts;
9. CI workflow permissions are least-privilege and publication-safe;
10. security-sensitive issues, red-team fixtures, and exploit repros are excluded or restricted.

## Sociosphere integration

Sociosphere owns this standard because it is the workspace controller. The implementation surface is:

- `standards/source-exposure/policy.v0.json` — machine-readable exposure policy.
- `standards/source-exposure/schemas/source_exposure_report.v1.json` — report contract.
- `tools/check_source_exposure.py` — stdlib-only validator for source publication checks.
- `make source-exposure-check` — local and CI entrypoint.
- `artifacts/source-exposure/source-exposure-report.json` — generated evidence report.

## Required downstream behavior

Downstream repositories should eventually expose the same target name:

```bash
make source-exposure-check
```

Where a repository cannot implement the check directly, Sociosphere may run this workspace-level validator against the materialized repository tree.

## Severity model

| Severity | CI behavior | Meaning |
|---|---:|---|
| `block` | fail | The item is likely unsafe for public source or release mirror publication. |
| `warn` | pass with finding | The item needs review but is not automatically unsafe. |
| `info` | pass | The item contributes to exposure accounting or inventory only. |

## Design notes

This standard is deliberately conservative about high-confidence leaks and deliberately restrained about natural-language scanning. A noisy validator becomes theater. A useful validator blocks things we should never publish and produces structured review evidence for the rest.
