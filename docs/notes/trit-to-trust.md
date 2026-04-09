# Trit-to-Trust – Source Archive & Consolidation Notes

> **Status:** Archive stub. The curated, normative version of this document
> belongs in the [tritrpc](https://github.com/SocioProphet/TriTRPC) repository
> at `docs/trit-to-trust.md`. Only raw/historical source material lives here.

## Purpose

This file records the provenance and consolidation status of the "Trit-to-Trust"
conceptual documentation that describes the trust-encoding semantics of the
TriTRPC protocol.

## Consolidation checklist

- [ ] Raw RTF/HTML source material has been located in `tritrpc-notes-archive` or
      equivalent historical repo.
- [ ] Curated Markdown version authored/reviewed and placed in
      `tritrpc/docs/trit-to-trust.md`.
- [ ] Normative statements extracted into `tritrpc/spec/` (protocol-level only).
- [ ] This stub updated with a link to the final curated doc once merged.

## Key concepts (summary for discoverability)

- **Trit**: A three-valued signal (negative / neutral / positive) used in TriTRPC
  to encode trust and validity assertions beyond binary true/false.
- **Trust encoding**: How trit values propagate through a computation or
  communication graph to compose a composite trust score.
- **Trit-to-Trust mapping**: The normative rules for converting trit sequences into
  human-readable trust assertions for agent-plane participants.

## Sources

- Original RTF/HTML drafts: to be confirmed in `tritrpc-notes-archive` repository.
- Related: `tritrpc/spec/` (normative statements only, once consolidated).

## See also

- [docs/TOPOLOGY.md](../TOPOLOGY.md) — repo roles and archival policy
- [tritrpc repository](https://github.com/SocioProphet/TriTRPC) — canonical home
  for the curated `docs/trit-to-trust.md`
