#!/usr/bin/env python3
"""
cli/measure-success.py

Print the full metrics dashboard to the console and save a snapshot to
metrics/registry-metrics.json.

Usage:
    python cli/measure-success.py
    python cli/measure-success.py --quiet     # save only, no stdout
    python cli/measure-success.py --no-save   # print only, no file write
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engines.metrics_collector import main as _metrics_main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(_metrics_main(sys.argv))
