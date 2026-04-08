#!/usr/bin/env python3
"""deps_inventory: emit a JSON report of installed pip packages.

Implements the 'deps_inventory' capability required by the cc adapter contract.
The output is a JSON object with:
  - python:     Python version string
  - executable: path to the Python interpreter
  - packages:   list of {name, version} dicts from pip list
"""
from __future__ import annotations

import json
import subprocess
import sys


def _pip_list() -> list[dict[str, str]]:
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return json.loads(out)  # type: ignore[no-any-return]
    except Exception as exc:
        return [{"error": str(exc)}]


def main() -> int:
    packages = _pip_list()
    report = {
        "python": sys.version,
        "executable": sys.executable,
        "packages": packages,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
