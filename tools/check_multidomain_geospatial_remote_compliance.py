#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REGISTRY = "registry/multidomain_geospatial_standards_compliance.v1.json"
REQUIRED_DOC_STRINGS = [
    "Standards consumed",
    "Implementation responsibility",
    "Promotion gate",
]
REQUIRED_PR_DOC_STRINGS = REQUIRED_DOC_STRINGS
USER_AGENT = "SocioProphet-SocioSphere-Compliance-Validator/1.0"


def fail(message: str) -> None:
    print(f"ERR: {message}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path}: invalid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path}: expected object")
    return data


def http_get(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8", errors="replace")
            if response.status < 200 or response.status >= 300:
                fail(f"{url}: unexpected HTTP status {response.status}")
            return body
    except urllib.error.HTTPError as exc:
        fail(f"{url}: HTTP {exc.code}")
    except urllib.error.URLError as exc:
        fail(f"{url}: URL error {exc}")


def raw_url(repo: str, path: str, ref: str = "main") -> str:
    owner, name = repo.split("/", 1)
    return f"https://raw.githubusercontent.com/{owner}/{name}/{ref}/{path}"


def pr_url(repo: str, pr_number: int) -> str:
    return f"https://api.github.com/repos/{repo}/pulls/{pr_number}"


def pr_files_url(repo: str, pr_number: int) -> str:
    return f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"


def require_doc_markers(repo: str, path: str, body: str, markers: list[str]) -> None:
    missing = [marker for marker in markers if marker not in body]
    if missing:
        fail(f"{repo}:{path}: missing required doc markers: {', '.join(missing)}")


def validate_committed_doc(repo: str, path: str) -> None:
    body = http_get(raw_url(repo, path))
    require_doc_markers(repo, path, body, REQUIRED_DOC_STRINGS)


def validate_open_pr_doc(repo: str, path: str, pr_number: int) -> None:
    pr = json.loads(http_get(pr_url(repo, pr_number)))
    if pr.get("state") != "open":
        fail(f"{repo}#{pr_number}: expected open PR, got {pr.get('state')!r}")
    if pr.get("draft") is True:
        fail(f"{repo}#{pr_number}: PR must not be draft")
    head_ref = pr.get("head", {}).get("ref")
    if not isinstance(head_ref, str) or not head_ref:
        fail(f"{repo}#{pr_number}: missing head ref")
    files = json.loads(http_get(pr_files_url(repo, pr_number)))
    if not isinstance(files, list):
        fail(f"{repo}#{pr_number}: files response must be array")
    changed_paths = {item.get("filename") for item in files if isinstance(item, dict)}
    if path not in changed_paths:
        fail(f"{repo}#{pr_number}: expected {path} in PR changed files")
    body = http_get(raw_url(repo, path, ref=head_ref))
    require_doc_markers(repo, path, body, REQUIRED_PR_DOC_STRINGS)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    registry = load_json(root / REGISTRY)
    docs = registry.get("required_implementation_docs")
    if not isinstance(docs, list) or not docs:
        fail("required_implementation_docs must be a non-empty array")
    checked = 0
    for entry in docs:
        if not isinstance(entry, dict):
            fail("implementation doc entry must be object")
        repo = entry.get("repo")
        path = entry.get("path")
        status = entry.get("status")
        if not isinstance(repo, str) or not isinstance(path, str) or not isinstance(status, str):
            fail(f"invalid implementation doc entry: {entry!r}")
        if status == "committed":
            validate_committed_doc(repo, path)
        elif status == "open_pr":
            pr_number = entry.get("pr")
            if not isinstance(pr_number, int):
                fail(f"{repo}: open_pr entry requires integer pr")
            validate_open_pr_doc(repo, path, pr_number)
        elif status == "blocked":
            continue
        else:
            fail(f"{repo}: unsupported status {status!r}")
        checked += 1
    print(f"OK: remotely verified {checked} multi-domain geospatial compliance doc(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
