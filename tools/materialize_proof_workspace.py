#!/usr/bin/env python3
"""Materialize proof repositories declared in manifest/proof-workspace.toml.

This is the first strict implementation step for the SocioSphere proof apparatus
workspace. It clones or updates the domain proof repositories into their declared
`local_path` locations so strict adapter validation can inspect each repo's
`proof-adapter.json`.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
PROOF_MANIFEST = ROOT / "manifest" / "proof-workspace.toml"


def fail(message: str) -> None:
    print(f"proof workspace materialization failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("$ " + " ".join(cmd))
    completed = subprocess.run(cmd, cwd=cwd, text=True)
    if completed.returncode != 0:
        fail(f"command failed with exit code {completed.returncode}: {' '.join(cmd)}")


def load_manifest() -> dict[str, Any]:
    if tomllib is None:
        fail("Python tomllib is unavailable; use Python 3.11+ for TOML validation")
    try:
        with PROOF_MANIFEST.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError:
        fail(f"missing manifest: {PROOF_MANIFEST}")
    except Exception as exc:
        fail(f"invalid TOML in {PROOF_MANIFEST}: {exc}")


def materialize_repo(repo: dict[str, Any], *, force: bool) -> None:
    for key in ("name", "url", "ref", "local_path"):
        if key not in repo:
            fail(f"repo entry missing {key}: {repo}")

    name = repo["name"]
    url = repo["url"]
    ref = repo["ref"]
    local_path = ROOT / repo["local_path"]

    if local_path.exists() and force:
        print(f"removing existing materialized repo for {name}: {local_path}")
        shutil.rmtree(local_path)

    if local_path.exists():
        git_dir = local_path / ".git"
        if not git_dir.exists():
            fail(f"local_path exists but is not a git checkout: {local_path}")
        print(f"updating existing proof repo {name} at {local_path}")
        run(["git", "fetch", "--depth", "1", "origin", ref], cwd=local_path)
        run(["git", "checkout", "FETCH_HEAD"], cwd=local_path)
    else:
        print(f"cloning proof repo {name} into {local_path}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth", "1", "--branch", ref, url, str(local_path)])

    adapter = local_path / "proof-adapter.json"
    if not adapter.exists():
        fail(f"materialized repo {name} missing proof-adapter.json at {adapter}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Remove existing materialized proof repo paths before cloning.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_manifest()
    repos = manifest.get("repos")
    if not isinstance(repos, list) or not repos:
        fail("manifest must contain proof [[repos]] entries")

    for repo in repos:
        materialize_repo(repo, force=args.force)

    print(f"proof workspace materialization passed: repos={len(repos)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
