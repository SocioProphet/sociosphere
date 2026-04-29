#!/usr/bin/env python3
"""Validate normalized software operational-risk JSONL files with lightweight shape checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from .jsonl_shape_checks import summarize_validation


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    payloads: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{line_no}: expected top-level object")
            payloads.append(payload)
    return payloads


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="One or more JSONL files to validate")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payloads: List[Dict[str, Any]] = []
    for raw_path in args.paths:
        payloads.extend(load_jsonl(Path(raw_path)))

    summary = summarize_validation(payloads)
    if summary["invalid"]:
        print(json.dumps(summary, indent=2), file=sys.stderr)
        return 1

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
