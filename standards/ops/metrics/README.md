# Ops Metrics Standard

This directory defines:
- `cadence.yaml`: which metrics are reported weekly/monthly/quarterly
- `registry.yaml`: canonical metric definitions (ownership, privacy, formula refs)
- `linkage.yaml`: how metrics map to financial drivers and statement lines

## Metric IDs
Metric IDs must match:
- lowercase
- `.`-separated namespaces allowed
- underscores allowed inside a segment
- regex: `^[a-z0-9]+(\.[a-z0-9_]+)*$`

Examples:
- `handoff.defects`
- `evidence_pack.compliance`

## SQL file mapping (deterministic)
By convention, each metric's `formula_ref` points to:
`pipelines/ops/sql/metrics/<metric_id_normalized>.sql`

Normalization rule:
- replace `.` with `_`

Examples:
- `handoff.defects` -> `handoff_defects.sql`
- `evidence_pack.compliance` -> `evidence_pack_compliance.sql`

## Privacy enforcement
- `privacy.default_view` must not expose HR metrics (domain `hr`)
- Metrics with `privacy_domain: hr` must be excluded from default report templates
- Audit logs must be enabled (`privacy.audit_log: true`)
