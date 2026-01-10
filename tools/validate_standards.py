from __future__ import annotations
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

METRIC_ID_RE = re.compile(r"^[a-z0-9]+(\.[a-z0-9_]+)*$")

OPS_REG = ROOT / "standards/ops/metrics/registry.yaml"
OPS_LINK = ROOT / "standards/ops/metrics/linkage.yaml"
OPS_CAD = ROOT / "standards/ops/metrics/cadence.yaml"

SCHEMA_REG = ROOT / "schemas/json/ops-metrics-registry.v1.schema.json"
SCHEMA_LINK = ROOT / "schemas/json/ops-metrics-linkage.v1.schema.json"

WEEKLY_TEMPLATE = ROOT / "standards/ops/reports/weekly-ops-pack.template.md"

def load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def load_json(p: Path):
    import json
    return json.loads(p.read_text(encoding="utf-8"))

def validate_schema(obj, schema_path: Path, label: str) -> None:
    schema = load_json(schema_path)
    v = Draft202012Validator(schema)
    errors = sorted(v.iter_errors(obj), key=lambda e: e.path)
    if errors:
        print(f"ERR: {label} failed schema validation ({schema_path.name})", file=sys.stderr)
        for e in errors[:50]:
            loc = ".".join(str(x) for x in e.path) or "<root>"
            print(f"  - {loc}: {e.message}", file=sys.stderr)
        raise SystemExit(2)

def norm_metric_id_to_sql(metric_id: str) -> str:
    return metric_id.replace(".", "_")

def main() -> int:
    missing = [p for p in [OPS_REG, OPS_LINK, OPS_CAD, SCHEMA_REG, SCHEMA_LINK] if not p.exists()]
    if missing:
        print("ERR: missing required files:", file=sys.stderr)
        for p in missing:
            print(f"  - {p}", file=sys.stderr)
        return 2

    reg = load_yaml(OPS_REG)
    link = load_yaml(OPS_LINK)
    cad = load_yaml(OPS_CAD)

    validate_schema(reg, SCHEMA_REG, "ops registry")
    validate_schema(link, SCHEMA_LINK, "ops linkage")

    # Basic cadence sanity: all cadence-listed metrics exist in registry
    cadence_metrics = []
    for period in ["weekly", "monthly", "quarterly"]:
        cadence_metrics.extend(cad.get("cadence", {}).get(period, []))

    registry_ids = [m["metric_id"] for m in reg["metrics"]]
    registry_set = set(registry_ids)

    # Unique metric IDs
    if len(registry_ids) != len(registry_set):
        dupes = [x for x in registry_set if registry_ids.count(x) > 1]
        print(f"ERR: duplicate metric_id(s): {dupes}", file=sys.stderr)
        return 2

    # Metric id format + SQL ref existence
    for m in reg["metrics"]:
        mid = m["metric_id"]
        if not METRIC_ID_RE.match(mid):
            print(f"ERR: invalid metric_id format: {mid}", file=sys.stderr)
            return 2
        sql_ref = m["formula_ref"]
        sql_path = ROOT / sql_ref
        if not sql_path.exists():
            print(f"ERR: formula_ref missing on disk for {mid}: {sql_ref}", file=sys.stderr)
            return 2
        expected = f"pipelines/ops/sql/metrics/{norm_metric_id_to_sql(mid)}.sql"
        if sql_ref != expected:
            print(f"ERR: formula_ref mismatch for {mid}\n  expected: {expected}\n  got:      {sql_ref}", file=sys.stderr)
            return 2

    # Cadence references must exist
    unknown = [mid for mid in cadence_metrics if mid not in registry_set]
    if unknown:
        print(f"ERR: cadence.yaml references unknown metric_id(s): {unknown}", file=sys.stderr)
        return 2

    # Linkage references must exist, and controls must exist
    linkage_ids = [x["metric_id"] for x in link["linkages"]]
    missing_link_metrics = [mid for mid in linkage_ids if mid not in registry_set]
    if missing_link_metrics:
        print(f"ERR: linkage.yaml references unknown metric_id(s): {missing_link_metrics}", file=sys.stderr)
        return 2

    for x in link["linkages"]:
        for dep in x.get("control_dependencies", []):
            if dep not in registry_set:
                print(f"ERR: linkage control_dependency unknown: {dep} (referenced by {x['metric_id']})", file=sys.stderr)
                return 2

    # Privacy enforcement: HR metrics must not appear in default weekly template
    hr_ids = {m["metric_id"] for m in reg["metrics"] if m.get("privacy_domain") == "hr"}
    if WEEKLY_TEMPLATE.exists():
        tmpl = WEEKLY_TEMPLATE.read_text(encoding="utf-8")
        leaked = [mid for mid in hr_ids if mid in tmpl]
        if leaked:
            print(f"ERR: HR metrics leaked into weekly default template: {leaked}", file=sys.stderr)
            return 2

    # Privacy policy sanity
    if not reg["privacy"].get("audit_log", False):
        print("ERR: registry privacy.audit_log must be true", file=sys.stderr)
        return 2
    if "hr" not in reg["privacy"].get("restricted_domains", []):
        print("ERR: registry privacy.restricted_domains must include 'hr'", file=sys.stderr)
        return 2

    print("OK: standards validation passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
