---
report_id: "weekly_ops_pack"
week: "{{week}}"
entity: "{{entity}}"
data_snapshot: "{{snapshot_hash}}"
generated_at: "{{generated_at}}"
privacy_default_view: "aggregate"
---

# Weekly Ops Pack — {{week}}

## Highlights
- Stage Velocity:
- Handoff Defects:
- Evidence Pack Compliance:
- Coaching Cadence:
- Pod Scorecards:

## Metrics (Aggregate)
| Metric | Value | Definition | Financial Link | Lineage |
|---|---:|---|---|---|
| stage_velocity |  | median/P90 stage time | Revenue timing, OCF timing | metric:stage_velocity |
| handoff.defects |  | defects attributable to handoffs | COGS leakage, OpEx drag | metric:handoff.defects |
| evidence_pack.compliance |  | completeness rate | RevRec cleanliness, disputes | metric:evidence_pack.compliance |

## Notes
- All HR-domain metrics are excluded from default views; see restricted report if authorized.
