#!/usr/bin/env python3
"""
cli/analyze-ontology.py

Run the ontology engine against one or more repositories to extract
controlled vocabulary and topic models, then update
registry/repository-ontology.yaml.

Usage:
    python cli/analyze-ontology.py                  # analyse all local repos
    python cli/analyze-ontology.py sociosphere      # analyse a single repo
    python cli/analyze-ontology.py repo1 repo2      # analyse specific repos
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure engines/ is importable when run directly.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engines.ontology_engine import run as _engine_run  # noqa: E402


def main(argv: list[str]) -> int:
    repo_names = [a for a in argv[1:] if not a.startswith("--")] or None
    if repo_names:
        print(f"Analysing repos: {', '.join(repo_names)}")
    else:
        print("Analysing all local repository directories …")
    return _engine_run(repo_names)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
