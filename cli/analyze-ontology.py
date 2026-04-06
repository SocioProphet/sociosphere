#!/usr/bin/env python3
"""cli/analyze-ontology.py

Analyse the repository ontology and print a semantic summary.

Usage:
    python cli/analyze-ontology.py [--registry-dir PATH] [--format text|json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.ontology_engine import OntologyEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyse the SocioProphet repository ontology"
    )
    parser.add_argument("--registry-dir", default=None)
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    engine = OntologyEngine(args.registry_dir)
    engine.load()

    data = {
        "total_repos": len(engine.all_repos()),
        "active_repos": len(engine.repos_by_status("active")),
        "archived_repos": len(engine.repos_by_status("archived")),
        "roles_defined": engine.all_roles(),
        "role_summary": engine.extract_role_summary(),
        "language_summary": engine.extract_language_summary(),
        "tag_cloud": engine.extract_tag_cloud(),
        "ontology_warnings": engine.validate_repos_against_ontology(),
    }

    if args.format == "json":
        print(json.dumps(data, indent=2))
        return 0

    # Text output
    print("=== Repository Ontology Analysis ===\n")
    print(f"Total repos:    {data['total_repos']}")
    print(f"Active repos:   {data['active_repos']}")
    print(f"Archived repos: {data['archived_repos']}")
    print(f"\nDefined roles ({len(data['roles_defined'])}):")
    for role, count in data["role_summary"].items():
        print(f"  {role:<22} {count:>3} repos")

    print("\nLanguage distribution:")
    for lang, count in data["language_summary"].items():
        print(f"  {lang:<22} {count:>3} repos")

    print("\nTop 15 tags:")
    for tag, count in list(data["tag_cloud"].items())[:15]:
        print(f"  {tag:<22} {count:>3} repos")

    warnings = data["ontology_warnings"]
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  WARN: {w}")
    else:
        print("\nNo ontology warnings ✓")

    return 0


if __name__ == "__main__":
    sys.exit(main())
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
