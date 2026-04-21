#!/usr/bin/env python3
"""Check local bindings from the software operational-risk registry lane to canonical schemas.

This helper does not perform full JSON Schema validation. Instead, it verifies that the
current canonical schema targets declared in `schema_registry.py` resolve cleanly against
an available local checkout of `SourceOS-Linux/sourceos-spec`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .schema_registry import SCHEMA_TARGETS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contracts-root",
        required=True,
        help="Path to a local checkout of SourceOS-Linux/sourceos-spec",
    )
    parser.add_argument(
        "--target",
        choices=sorted(SCHEMA_TARGETS.keys()),
        help="Optional single schema target to check",
    )
    return parser.parse_args()


def check_target(contracts_root: Path, name: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    schema_path = contracts_root / meta["source_path"]
    example_path = contracts_root / meta["example_path"]
    return {
        "target": name,
        "normalized_type": meta["normalized_type"],
        "schema_id": meta["schema_id"],
        "schema_exists": schema_path.exists(),
        "schema_path": str(schema_path),
        "example_exists": example_path.exists(),
        "example_path": str(example_path),
    }


def main() -> int:
    args = parse_args()
    contracts_root = Path(args.contracts_root)
    names = [args.target] if args.target else list(SCHEMA_TARGETS.keys())

    results = [check_target(contracts_root, name, SCHEMA_TARGETS[name]) for name in names]
    summary = {
        "contracts_root": str(contracts_root),
        "checked": len(results),
        "all_bound": all(item["schema_exists"] and item["example_exists"] for item in results),
        "results": results,
    }
    print(json.dumps(summary, indent=2))
    return 0 if summary["all_bound"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
