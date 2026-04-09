#!/usr/bin/env python3
"""Run ontology analysis helpers over local repositories."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engines.ontology_engine import run as run_ontology  # noqa: E402



def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv
    repo_names = [arg for arg in argv[1:] if not arg.startswith("--")] or None
    return run_ontology(repo_names)


if __name__ == "__main__":
    raise SystemExit(main())
