#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]  # standards/qes
CAT = ROOT / "schemas/topics/topic-catalog.v1.yaml"


def _parse_topic_catalog_without_yaml(raw: str) -> list[dict[str, str]]:
    """
    Fallback parser for the limited structure of topic-catalog.v1.yaml.

    This intentionally supports only the subset we validate here:
    - topics:
      - name: ...
        schema: ...
    """
    topics: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        topic_start = re.match(r"-\s+name:\s*(.+)", stripped)
        if topic_start:
            if current:
                topics.append(current)
            current = {"name": topic_start.group(1).strip()}
            continue
        schema = re.match(r"schema:\s*(.+)", stripped)
        if schema and current is not None:
            current["schema"] = schema.group(1).strip()
    if current:
        topics.append(current)
    return topics

def main() -> int:
    if not CAT.exists():
        print(f"ERR: missing topic catalog: {CAT}", file=sys.stderr)
        return 2
    raw_catalog = CAT.read_text()
    if yaml is None:
        print(
            "WARN: PyYAML not installed; using fallback parser for topic-catalog.v1.yaml",
            file=sys.stderr,
        )
        topics = _parse_topic_catalog_without_yaml(raw_catalog)
    else:
        doc = yaml.safe_load(raw_catalog)
        topics = doc.get("topics", [])
    errs = 0
    for t in topics:
        schema_rel = t.get("schema")
        if not schema_rel:
            print(f"ERR: topic missing schema field: {t}", file=sys.stderr)
            errs += 1
            continue
        schema_path = ROOT / "schemas" / schema_rel
        if not schema_path.exists():
            print(f"ERR: missing schema file for topic {t.get('name')}: {schema_path}", file=sys.stderr)
            errs += 1
            continue
        if schema_path.suffix == ".json":
            try:
                json.loads(schema_path.read_text())
            except Exception as e:
                print(f"ERR: invalid JSON in {schema_path}: {e}", file=sys.stderr)
                errs += 1
    if errs:
        print(f"FAIL: {errs} schema issue(s)", file=sys.stderr)
        return 1
    print("OK: topic catalog schemas exist and JSON parses")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
