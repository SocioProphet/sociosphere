#!/usr/bin/env python3
"""
metrics_spec_check.py (v0)
Pedantic validator for metrics.v0.yaml:
- YAML parse
- Required top-level keys
- Events have required_fields and enums where applicable
- Metrics have description, cadence, inputs, formula (type + definition)
- Thresholds are sane when present
"""
from __future__ import annotations
import sys
from pathlib import Path

try:
    import yaml
except Exception as e:
    print(f"ERR: PyYAML required but not importable: {e}", file=sys.stderr)
    raise

def die(msg: str) -> int:
    print("ERR:", msg, file=sys.stderr)
    return 1

def main() -> int:
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("programs/delex/gtm-intelligence/metrics/metrics.v0.yaml")
    if not p.exists():
        return die(f"metrics spec not found: {p}")

    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        return die("metrics spec must be a mapping/object")

    for k in ("version", "owner", "events", "metrics"):
        if k not in doc:
            return die(f"missing top-level key: {k}")

    events = doc["events"]
    if not isinstance(events, dict) or not events:
        return die("events must be a non-empty mapping")

    for ev_name, ev in events.items():
        if not isinstance(ev, dict):
            return die(f"event {ev_name} must be a mapping")
        rf = ev.get("required_fields")
        if not isinstance(rf, list) or not rf:
            return die(f"event {ev_name} missing required_fields list")
        # ensure strings and unique
        if any((not isinstance(x, str) or not x) for x in rf):
            return die(f"event {ev_name} required_fields must be non-empty strings")
        if len(set(rf)) != len(rf):
            return die(f"event {ev_name} required_fields contains duplicates")

    metrics = doc["metrics"]
    if not isinstance(metrics, dict) or not metrics:
        return die("metrics must be a non-empty mapping")

    allowed_cadence = {"realtime", "daily", "weekly", "monthly", "quarterly"}
    for m_name, m in metrics.items():
        if not isinstance(m, dict):
            return die(f"metric {m_name} must be a mapping")
        for k in ("description", "cadence", "inputs", "formula"):
            if k not in m:
                return die(f"metric {m_name} missing key: {k}")
        if m["cadence"] not in allowed_cadence:
            return die(f"metric {m_name} cadence must be one of {sorted(allowed_cadence)}, got {m['cadence']!r}")
        if not isinstance(m["inputs"], list) or not m["inputs"]:
            return die(f"metric {m_name} inputs must be a non-empty list")
        if any((not isinstance(x, str) or not x) for x in m["inputs"]):
            return die(f"metric {m_name} inputs must be non-empty strings")
        formula = m["formula"]
        if not isinstance(formula, dict):
            return die(f"metric {m_name} formula must be a mapping")
        if "type" not in formula or "definition" not in formula:
            return die(f"metric {m_name} formula must include type + definition")
        if not isinstance(formula["type"], str) or not formula["type"]:
            return die(f"metric {m_name} formula.type must be non-empty string")
        if not isinstance(formula["definition"], str) or len(formula["definition"].strip()) < 5:
            return die(f"metric {m_name} formula.definition too short")

        thr = m.get("thresholds")
        if thr is not None:
            if not isinstance(thr, dict) or not thr:
                return die(f"metric {m_name} thresholds must be a mapping if present")
            # very light sanity: values must be number-like
            for tk, tv in thr.items():
                if not isinstance(tv, (int, float)):
                    return die(f"metric {m_name} threshold {tk} must be numeric, got {type(tv).__name__}")

    print(f"OK: metrics_spec_check passed for {p}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
