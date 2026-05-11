#!/usr/bin/env python3
"""Generate proof workspace claim-boundary and ledger outputs.

Inputs:
- manifest/proof-workspace.toml
- materialized proof repos at each [[repos]].local_path
- each materialized repo's proof-adapter.json

Outputs:
- status/proof-apparatus/claim-boundary-table.md
- status/proof-apparatus/claim-ledger-events.jsonl

The generator emits controller metadata only. It does not execute mathematics and
it does not promote claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
PROOF_MANIFEST = ROOT / "manifest" / "proof-workspace.toml"
OUTPUT_DIR = ROOT / "status" / "proof-apparatus"
CLAIM_TABLE = OUTPUT_DIR / "claim-boundary-table.md"
LEDGER_EVENTS = OUTPUT_DIR / "claim-ledger-events.jsonl"
DETERMINISTIC_TIMESTAMP = "proof-workspace-materialized-adapter-snapshot"


def fail(message: str) -> None:
    print(f"proof workspace output generation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_toml(path: Path) -> dict[str, Any]:
    if tomllib is None:
        fail("Python tomllib is unavailable; use Python 3.11+")
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except FileNotFoundError:
        fail(f"missing TOML file: {path}")
    except Exception as exc:
        fail(f"invalid TOML in {path}: {exc}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing JSON file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def escape_cell(value: Any) -> str:
    text = str(value) if value is not None else ""
    return text.replace("|", "\\|").replace("\n", "<br>")


def collect_adapters(repos: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any], Path, str]]:
    collected: list[tuple[dict[str, Any], dict[str, Any], Path, str]] = []
    for repo in repos:
        adapter_path = ROOT / repo["local_path"] / "proof-adapter.json"
        adapter = load_json(adapter_path)
        collected.append((repo, adapter, adapter_path, sha256_file(adapter_path)))
    return collected


def write_claim_table(collected: list[tuple[dict[str, Any], dict[str, Any], Path, str]]) -> None:
    lines = [
        "# Proof Apparatus Claim-Boundary Table",
        "",
        "Generated from materialized proof adapters by `tools/generate_proof_workspace_outputs.py`.",
        "",
        "This table is controller metadata. It does not promote theorem status.",
        "",
        "| Repo | Claim | State | Severity | Gates | Obstruction walls | Boundary | Adapter digest |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for repo, adapter, _adapter_path, digest in collected:
        claims = adapter.get("claims", [])
        if not claims:
            lines.append(
                "| "
                + " | ".join(
                    [
                        escape_cell(adapter.get("repo", repo["name"])),
                        "_No claims declared_",
                        "diagnosed",
                        "E7",
                        escape_cell(", ".join(g.get("gate_id", "") for g in adapter.get("gates", []))),
                        escape_cell(", ".join(repo.get("primary_walls", []))),
                        "Adapter declares gates and non-claims only.",
                        digest,
                    ]
                )
                + " |"
            )
            continue

        for claim in claims:
            lines.append(
                "| "
                + " | ".join(
                    [
                        escape_cell(adapter.get("repo", repo["name"])),
                        escape_cell(claim.get("claim_id")),
                        escape_cell(claim.get("state")),
                        escape_cell(claim.get("severity")),
                        escape_cell(", ".join(claim.get("owned_gates", []))),
                        escape_cell(", ".join(claim.get("obstruction_walls", []))),
                        escape_cell("; ".join(claim.get("boundary", []))),
                        digest,
                    ]
                )
                + " |"
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CLAIM_TABLE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_ledger_events(collected: list[tuple[dict[str, Any], dict[str, Any], Path, str]]) -> None:
    events: list[dict[str, Any]] = []

    for repo, adapter, adapter_path, digest in collected:
        claims = adapter.get("claims", [])
        if not claims:
            event_id_seed = f"{adapter.get('repo', repo['name'])}:adapter-only:{digest}"
            events.append(
                {
                    "event_id": hashlib.sha256(event_id_seed.encode("utf-8")).hexdigest()[:24],
                    "event_type": "evidence_recorded",
                    "timestamp": DETERMINISTIC_TIMESTAMP,
                    "repo": adapter.get("repo", repo["name"]),
                    "ref": repo.get("ref", "main"),
                    "claim_id": "adapter-only",
                    "claim_state": "diagnosed",
                    "severity": "E7",
                    "claim_boundary": ["Adapter declares gates and non-claims only; no claim promotion."],
                    "non_claims": [n.get("statement", "") for n in adapter.get("non_claims", [])],
                    "gates": adapter.get("gates", []),
                    "artifact_digests": [
                        {
                            "path": str(adapter_path.relative_to(ROOT)),
                            "digest": digest,
                            "media_type": "application/json",
                        }
                    ],
                    "obstruction_walls": repo.get("primary_walls", []),
                    "controller": {
                        "repo": "SocioProphet/sociosphere",
                        "protocol": "protocol/proof-apparatus-workspace/v0",
                        "decision": "record_adapter_metadata",
                    },
                }
            )
            continue

        for claim in claims:
            event_id_seed = f"{adapter.get('repo', repo['name'])}:{claim.get('claim_id')}:{digest}"
            events.append(
                {
                    "event_id": hashlib.sha256(event_id_seed.encode("utf-8")).hexdigest()[:24],
                    "event_type": "claim_registered",
                    "timestamp": DETERMINISTIC_TIMESTAMP,
                    "repo": adapter.get("repo", repo["name"]),
                    "ref": repo.get("ref", "main"),
                    "claim_id": claim.get("claim_id"),
                    "domain": adapter.get("domain", repo.get("domain")),
                    "substrate": claim.get("substrate"),
                    "shell_level": claim.get("shell_level"),
                    "projection": claim.get("projection"),
                    "claim_state": claim.get("state"),
                    "severity": claim.get("severity"),
                    "claim_statement": claim.get("statement"),
                    "claim_boundary": claim.get("boundary", []),
                    "non_claims": [
                        n.get("statement", "")
                        for n in adapter.get("non_claims", [])
                        if n.get("non_claim_id") in set(claim.get("non_claim_refs", []))
                    ],
                    "gates": [
                        g
                        for g in adapter.get("gates", [])
                        if g.get("gate_id") in set(claim.get("owned_gates", []))
                    ],
                    "artifact_digests": [
                        {
                            "path": str(adapter_path.relative_to(ROOT)),
                            "digest": digest,
                            "media_type": "application/json",
                        }
                    ],
                    "obstruction_walls": claim.get("obstruction_walls", []),
                    "controller": {
                        "repo": "SocioProphet/sociosphere",
                        "protocol": "protocol/proof-apparatus-workspace/v0",
                        "decision": "register_claim_without_promotion",
                    },
                }
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_EVENTS.write_text("\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated outputs would change.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = load_toml(PROOF_MANIFEST)
    repos = manifest.get("repos")
    if not isinstance(repos, list) or not repos:
        fail("manifest must contain proof [[repos]] entries")

    old_claim_table = CLAIM_TABLE.read_text(encoding="utf-8") if CLAIM_TABLE.exists() else None
    old_ledger_events = LEDGER_EVENTS.read_text(encoding="utf-8") if LEDGER_EVENTS.exists() else None

    collected = collect_adapters(repos)
    write_claim_table(collected)
    write_ledger_events(collected)

    if args.check:
        new_claim_table = CLAIM_TABLE.read_text(encoding="utf-8")
        new_ledger_events = LEDGER_EVENTS.read_text(encoding="utf-8")
        if old_claim_table is not None and old_claim_table != new_claim_table:
            fail(f"generated output is stale: {CLAIM_TABLE}")
        if old_ledger_events is not None and old_ledger_events != new_ledger_events:
            fail(f"generated output is stale: {LEDGER_EVENTS}")

    print(f"proof workspace outputs generated: {CLAIM_TABLE} {LEDGER_EVENTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
