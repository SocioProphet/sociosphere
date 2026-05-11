#!/usr/bin/env python3
"""Materialize proof repositories declared in manifest/proof-workspace.toml.

This is the first strict implementation step for the SocioSphere proof apparatus
workspace. It clones or updates the domain proof repositories into their declared
`local_path` locations so strict adapter validation can inspect each repo's
`proof-adapter.json`.

When called from a domain proof repo workflow, the environment variables below
can force the changed repo to materialize at the exact pushed/PR commit instead
of the manifest's default ref:

- PROOF_WORKSPACE_DOMAIN_REPO, for example SocioProphet/Heller-Godel
- PROOF_WORKSPACE_DOMAIN_REF, for example feature-branch
- PROOF_WORKSPACE_DOMAIN_SHA, preferred exact commit SHA
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

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


def repo_full_name_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return path


def checkout_repo(local_path: Path, *, ref: str, sha: str | None) -> None:
    if sha:
        run(["git", "fetch", "--depth", "1", "origin", sha], cwd=local_path)
        run(["git", "checkout", "--detach", sha], cwd=local_path)
        return
    run(["git", "fetch", "--depth", "1", "origin", ref], cwd=local_path)
    run(["git", "checkout", "FETCH_HEAD"], cwd=local_path)


def materialize_repo(repo: dict[str, Any], *, force: bool, override_repo: str | None, override_ref: str | None, override_sha: str | None) -> None:
    for key in ("name", "url", "ref", "local_path"):
        if key not in repo:
            fail(f"repo entry missing {key}: {repo}")

    name = repo["name"]
    url = repo["url"]
    manifest_ref = repo["ref"]
    local_path = ROOT / repo["local_path"]
    repo_full_name = repo_full_name_from_url(url)

    effective_ref = manifest_ref
    effective_sha: str | None = None
    if override_repo and override_repo.lower() == repo_full_name.lower():
        effective_ref = override_ref or manifest_ref
        effective_sha = override_sha or None
        print(
            f"using changed domain repo override for {repo_full_name}: "
            f"ref={effective_ref} sha={effective_sha or 'n/a'}"
        )

    if local_path.exists() and force:
        print(f"removing existing materialized repo for {name}: {local_path}")
        shutil.rmtree(local_path)

    if local_path.exists():
        git_dir = local_path / ".git"
        if not git_dir.exists():
            fail(f"local_path exists but is not a git checkout: {local_path}")
        print(f"updating existing proof repo {name} at {local_path}")
        checkout_repo(local_path, ref=effective_ref, sha=effective_sha)
    else:
        print(f"cloning proof repo {name} into {local_path}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        if effective_sha:
            run(["git", "clone", "--depth", "1", url, str(local_path)])
            checkout_repo(local_path, ref=effective_ref, sha=effective_sha)
        else:
            run(["git", "clone", "--depth", "1", "--branch", effective_ref, url, str(local_path)])

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

    override_repo = os.environ.get("PROOF_WORKSPACE_DOMAIN_REPO") or None
    override_ref = os.environ.get("PROOF_WORKSPACE_DOMAIN_REF") or None
    override_sha = os.environ.get("PROOF_WORKSPACE_DOMAIN_SHA") or None

    for repo in repos:
        materialize_repo(
            repo,
            force=args.force,
            override_repo=override_repo,
            override_ref=override_ref,
            override_sha=override_sha,
        )

    print(f"proof workspace materialization passed: repos={len(repos)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
