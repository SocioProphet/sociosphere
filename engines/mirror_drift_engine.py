#!/usr/bin/env python3
"""mirror_drift_engine.py — generate and validate mirror drift artifacts.

Source of truth:
  - registry/external-mirrors.yaml

Derived artifact:
  - status/mirror-drift.yaml

Commands:
  - probe:    query remote heads via `git ls-remote` and update the registry when
              upstream/mirror heads change.
  - generate: render status/mirror-drift.yaml from the registry.
  - check:    verify status/mirror-drift.yaml matches the registry-derived payload.

Dependencies:
  - Stdlib + PyYAML only.
  - `probe` requires `git` in PATH and network access to GitHub.
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: PyYAML required (pip install pyyaml)", file=sys.stderr)
    raise

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registry" / "external-mirrors.yaml"
STATUS_PATH = REPO_ROOT / "status" / "mirror-drift.yaml"

REGISTRY_HEADER = """# registry/external-mirrors.yaml
# Cross-organization mirror and external-canonical metadata.
# Purpose: allow sociosphere governance + tooling to reason about repos that live
# outside the SocioProphet org (e.g., SociOS-Linux and SourceOS-Linux).
#
# NOTE: this file is updated by `engines/mirror_drift_engine.py probe`.
#       Avoid manual edits unless you also update status/mirror-drift.yaml.

"""

STATUS_HEADER = """# status/mirror-drift.yaml
# Machine-readable snapshot of mirror drift state.
# Source of truth: registry/external-mirrors.yaml

"""


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text("utf-8"))


def _write_yaml(path: Path, header: str, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = yaml.safe_dump(payload, sort_keys=False, default_flow_style=False)
    path.write_text(header + body, encoding="utf-8")


def _today_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def _canonical_generated_at(registry: dict[str, Any]) -> str:
    # Deterministic timestamp: derive from registry.updated_at (date string).
    # This avoids CI drift caused by wall-clock timestamps.
    updated_at = str(registry.get("updated_at") or "").strip()
    if not updated_at:
        return "1970-01-01T00:00:00Z"
    # If it's already an ISO timestamp, keep it; else assume YYYY-MM-DD.
    if "T" in updated_at:
        return updated_at
    return f"{updated_at}T00:00:00Z"


def _strip_nones(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


def _git_ls_remote(url: str, ref: str) -> str | None:
    """Return the SHA for (url, ref) using git ls-remote.

    Accepts either a branch name (e.g., "main") or a full refspec.
    """
    candidates: list[str] = []
    if ref.startswith("refs/"):
        candidates.append(ref)
    else:
        candidates.append(f"refs/heads/{ref}")
        candidates.append(ref)

    for r in candidates:
        proc = subprocess.run(
            ["git", "ls-remote", "--exit-code", url, r],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            continue
        out = (proc.stdout or "").strip()
        if not out:
            continue
        return out.split()[0]

    return None


def _probe_registry(registry: dict[str, Any]) -> tuple[dict[str, Any], bool, list[str]]:
    mirrors = registry.get("mirrors") or []
    if not isinstance(mirrors, list):
        raise ValueError("registry/external-mirrors.yaml: mirrors must be a list")

    changed = False
    warnings: list[str] = []
    today = _today_utc()

    for m in mirrors:
        if not isinstance(m, dict):
            continue
        upstream = m.get("upstream")
        if not isinstance(upstream, dict):
            warnings.append(f"{m.get('name','<unknown>')}: missing upstream block")
            continue

        upstream_url = str(upstream.get("url") or "").strip()
        upstream_ref = str(upstream.get("ref") or "").strip() or "main"
        mirror_url = str(m.get("url") or "").strip()

        if not upstream_url:
            warnings.append(f"{m.get('name','<unknown>')}: upstream.url missing")
            continue
        if not mirror_url:
            warnings.append(f"{m.get('name','<unknown>')}: mirror url missing")
            continue

        # upstream head
        new_up = _git_ls_remote(upstream_url, upstream_ref)
        if new_up is None:
            warnings.append(f"{m.get('name','<unknown>')}: unable to resolve upstream head ({upstream_url} {upstream_ref})")
        else:
            if upstream.get("head_sha") != new_up:
                upstream["head_sha"] = new_up
                upstream["checked_at"] = today
                changed = True

        # mirror head (assume same branch naming)
        new_mirror = _git_ls_remote(mirror_url, upstream_ref)
        if new_mirror is None:
            warnings.append(f"{m.get('name','<unknown>')}: unable to resolve mirror head ({mirror_url} {upstream_ref})")
        else:
            if m.get("mirror_head_sha") != new_mirror:
                m["mirror_head_sha"] = new_mirror
                changed = True

    if changed:
        registry["updated_at"] = today

    return registry, changed, warnings


def build_payload(registry: dict[str, Any]) -> dict[str, Any]:
    mirrors = registry.get("mirrors") or []
    if not isinstance(mirrors, list):
        raise ValueError("registry/external-mirrors.yaml: mirrors must be a list")

    rows: list[dict[str, Any]] = []
    for m in mirrors:
        if not isinstance(m, dict):
            continue
        upstream = m.get("upstream") or {}
        drift = m.get("drift") or {}
        if not isinstance(upstream, dict):
            upstream = {}
        if not isinstance(drift, dict):
            drift = {}

        row = _strip_nones(
            {
                "name": m.get("name"),
                "org": m.get("org"),
                "url": m.get("url"),
                "upstream_url": upstream.get("url"),
                "upstream_ref": upstream.get("ref"),
                "upstream_head_sha": upstream.get("head_sha"),
                "checked_at": upstream.get("checked_at"),
                "mirror_head_sha": m.get("mirror_head_sha"),
                "drift_status": drift.get("status") or "unknown",
                "drift_note": drift.get("note"),
            }
        )
        if not row.get("name"):
            continue
        rows.append(row)

    rows.sort(key=lambda r: str(r.get("name")))

    payload: dict[str, Any] = {
        "version": str(registry.get("version") or "1.0.0"),
        "generated_at": _canonical_generated_at(registry),
        "mirrors": rows,
        "notes": [
            "Generated by engines/mirror_drift_engine.py from registry/external-mirrors.yaml; do not edit manually.",
        ],
    }
    return payload


def cmd_probe(args: argparse.Namespace) -> int:
    if not REGISTRY_PATH.exists():
        print(f"ERROR: missing {REGISTRY_PATH}", file=sys.stderr)
        return 2

    registry = _load_yaml(REGISTRY_PATH) or {}
    if not isinstance(registry, dict):
        print("ERROR: registry/external-mirrors.yaml must parse to a mapping", file=sys.stderr)
        return 2

    updated, changed, warnings = _probe_registry(registry)

    for w in warnings:
        print(f"WARN: {w}", file=sys.stderr)

    if changed and args.write:
        _write_yaml(REGISTRY_PATH, REGISTRY_HEADER, updated)
        print(f"OK: updated {REGISTRY_PATH}")
    elif changed:
        print("INFO: mirror heads changed (run with --write to update registry)")
    else:
        print("OK: no upstream/mirror head changes detected")

    return 0


def cmd_generate(_: argparse.Namespace) -> int:
    if not REGISTRY_PATH.exists():
        print(f"ERROR: missing {REGISTRY_PATH}", file=sys.stderr)
        return 2
    registry = _load_yaml(REGISTRY_PATH) or {}
    if not isinstance(registry, dict):
        print("ERROR: registry/external-mirrors.yaml must parse to a mapping", file=sys.stderr)
        return 2

    payload = build_payload(registry)
    _write_yaml(STATUS_PATH, STATUS_HEADER, payload)
    print(f"OK: wrote {STATUS_PATH}")
    return 0


def cmd_check(_: argparse.Namespace) -> int:
    if not REGISTRY_PATH.exists():
        print(f"ERROR: missing {REGISTRY_PATH}", file=sys.stderr)
        return 2
    if not STATUS_PATH.exists():
        print(f"ERROR: missing {STATUS_PATH}. Run: python3 engines/mirror_drift_engine.py generate", file=sys.stderr)
        return 2

    registry = _load_yaml(REGISTRY_PATH) or {}
    if not isinstance(registry, dict):
        print("ERROR: registry/external-mirrors.yaml must parse to a mapping", file=sys.stderr)
        return 2

    expected = build_payload(registry)
    current = _load_yaml(STATUS_PATH) or {}
    if not isinstance(current, dict):
        print("ERROR: status/mirror-drift.yaml must parse to a mapping", file=sys.stderr)
        return 2

    if current != expected:
        print("ERROR: status/mirror-drift.yaml is out of date.", file=sys.stderr)
        print("Run: python3 engines/mirror_drift_engine.py generate", file=sys.stderr)
        return 2

    print("OK: mirror drift status matches registry")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("probe", help="Probe upstream/mirror heads and optionally update the registry")
    sp.add_argument("--write", action="store_true", help="Write registry/external-mirrors.yaml if changes are detected")
    sp.set_defaults(fn=cmd_probe)

    sp = sub.add_parser("generate", help="Generate status/mirror-drift.yaml")
    sp.set_defaults(fn=cmd_generate)

    sp = sub.add_parser("check", help="Verify status/mirror-drift.yaml matches the registry")
    sp.set_defaults(fn=cmd_check)

    args = p.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
