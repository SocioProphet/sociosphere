# SourceOS substrate alignment note

This note explains the additive SourceOS/SociOS substrate boundary supplement added under `governance/SOURCEOS_SUBSTRATE_BOUNDARIES.yaml`.

## Why this file exists

Recent codification work landed in multiple upstream authorities:
- `workspace-inventory` expanded the cross-org repo graph
- `workstation-contracts` gained the first M2 runner↔adapter IPC pack
- `sourceos-spec` gained the shared content/build/release object family
- `socios` gained the first FCOS + Foreman/Katello automation scaffold
- `SourceOS` gained the first artifact-truth scaffold for flavors, installer profiles, channels, and manifests

The existing `governance/CANONICAL_SOURCES.yaml` remains authoritative.

This note and the companion YAML file exist only to make the new substrate boundaries explicit without rewriting the canonical map in one risky pass.

## Intended follow-on

After review, the accepted namespace additions should be folded into `governance/CANONICAL_SOURCES.yaml` and the supplement can be removed.
