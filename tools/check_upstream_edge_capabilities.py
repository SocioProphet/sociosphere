#!/usr/bin/env python3
"""Check upstream drift for edge-capability donor/dependency repos.

This is a lightweight operational check for the upstream baselines recorded in
`registry/upstream-bindings-edge-capabilities.yaml`.

Current implementation keeps the baseline table inline to avoid adding a YAML
runtime dependency to sociosphere's control-plane tooling. Keep this file in
sync with the registry file when baselines are intentionally updated.

Usage:
    python3 tools/check_upstream_edge_capabilities.py

Requirements:
    - gh CLI authenticated and able to access the public GitHub API
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Upstream:
    key: str
    repo: str
    branch: str
    baseline_sha: str
    disposition: str


UPSTREAMS = [
    Upstream(
        key="cap.edge.share",
        repo="KuroLabs/Airshare",
        branch="master",
        baseline_sha="92a144dbf7af2d2a5fbcfbfb3078f4c9ecf86c13",
        disposition="wrap_or_hardened_fork",
    ),
    Upstream(
        key="cap.edge.fingerprint",
        repo="projectdiscovery/cdncheck",
        branch="main",
        baseline_sha="68bfbae83a4aad30d9cbb17c30bb44c32e10affb",
        disposition="direct_dependency_plus_wrapper",
    ),
    Upstream(
        key="memex.papers",
        repo="marawangamal/papers",
        branch="main",
        baseline_sha="1ae5061b7ec9d2ab7d0e37ad254ad435a58fc5ec",
        disposition="reference_implementation_only",
    ),
    Upstream(
        key="future.llm.train",
        repo="ServiceNow/Fast-LLM",
        branch="main",
        baseline_sha="7a7129d7775cea459cb19a48be0d831ccc7b4e7d",
        disposition="watchlist_later_lane",
    ),
]


def gh_json(*args: str) -> dict:
    cmd = ["gh", "api", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "gh api failed")
    return json.loads(proc.stdout)


def get_head_sha(repo: str, branch: str) -> str:
    payload = gh_json(f"repos/{repo}/commits/{branch}")
    return payload["sha"]


def main() -> int:
    print("== upstream drift check: edge capabilities ==")
    drift = False

    for upstream in UPSTREAMS:
        try:
            head_sha = get_head_sha(upstream.repo, upstream.branch)
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR  {upstream.key:20} {upstream.repo}@{upstream.branch} :: {exc}")
            drift = True
            continue

        if head_sha == upstream.baseline_sha:
            print(
                f"OK     {upstream.key:20} {upstream.repo}@{upstream.branch} "
                f"baseline={upstream.baseline_sha[:12]} disposition={upstream.disposition}"
            )
        else:
            drift = True
            print(
                f"DRIFT  {upstream.key:20} {upstream.repo}@{upstream.branch} "
                f"baseline={upstream.baseline_sha[:12]} head={head_sha[:12]} "
                f"disposition={upstream.disposition}"
            )

    if drift:
        print("\nResult: upstream drift detected or check failed.")
        return 1

    print("\nResult: all tracked upstream heads match the recorded baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
