#!/usr/bin/env python3
"""Print or save registry success metrics."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engines.metrics_collector import main as metrics_main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(metrics_main(sys.argv))
