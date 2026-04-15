from __future__ import annotations
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

LINES = ROOT / "standards/finance/statements/lines.yaml"
COA = ROOT / "standards/finance/coa/coa.v1.yaml"
TEMPL = ROOT / "standards/finance/posting/templates.v1.yaml"

SCHEMA_LINES = ROOT / "schemas/json/finance-statement-lines.v1.schema.json"
SCHEMA_COA = ROOT / "schemas/json/finance-coa.v1.schema.json"
SCHEMA_TEMPL = ROOT / "schemas/json/finance-posting-templates.v1.schema.json"

OPS_LINK = ROOT / "standards/ops/metrics/linkage.yaml"

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

def main() -> int:
    for p in [LINES, COA, TEMPL, SCHEMA_LINES, SCHEMA_COA, SCHEMA_TEMPL]:
        if not p.exists():
            print(f"ERR: missing required file: {p}", file=sys.stderr)
            return 2

    lines = load_yaml(LINES)
    coa = load_yaml(COA)
    templ = load_yaml(TEMPL)

    validate_schema(lines, SCHEMA_LINES, "statement lines")
    validate_schema(coa, SCHEMA_COA, "chart of accounts")
    validate_schema(templ, SCHEMA_TEMPL, "posting templates")

    # Build valid statement-line ID set
    sl_ids = set()
    for section in ["income_statement","balance_sheet","cash_flow"]:
        for x in lines[section]:
            sl_ids.add(x["id"])

    # COA must reference only known statement lines (or null)
    acct_ids = set()
    for a in coa["accounts"]:
        aid = a["id"]
        if aid in acct_ids:
            print(f"ERR: duplicate account id in COA: {aid}", file=sys.stderr)
            return 2
        acct_ids.add(aid)
        sl = a["statement_line"]
        if sl is not None and sl not in sl_ids:
            print(f"ERR: COA account {aid} references unknown statement_line: {sl}", file=sys.stderr)
            return 2

    # Posting templates must reference existing accounts and have at least one debit and one credit.
    for t in templ["templates"]:
        deb = 0
        cred = 0
        for ln in t["lines"]:
            if ln["account"] not in acct_ids:
                print(f"ERR: template {t['event_type']} references unknown account: {ln['account']}", file=sys.stderr)
                return 2
            if ln["side"] == "debit":
                deb += 1
            else:
                cred += 1
        if deb == 0 or cred == 0:
            print(f"ERR: template {t['event_type']} must include both debits and credits", file=sys.stderr)
            return 2

    # Cross-standard guard: ops→finance linkage may reference statement lines; ensure they exist.
    if OPS_LINK.exists():
        link = load_yaml(OPS_LINK)
        for x in link.get("linkages", []):
            stm = x.get("statement_lines", {})
            for sec, ids in stm.items():
                for sid in ids:
                    if sid not in sl_ids:
                        print(f"ERR: ops linkage references unknown finance statement line: {sid} (metric {x.get('metric_id')})", file=sys.stderr)
                        return 2

    print("OK: finance standards validation passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
