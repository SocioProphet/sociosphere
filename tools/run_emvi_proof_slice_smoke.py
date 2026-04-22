#!/usr/bin/env python3
"""Run a lightweight EMVI proof-slice smoke flow.

This validates the merged proof-slice fixtures, composes the demo artifact from
those fixtures, and emits a structured artifact bundle under artifacts/workspace.
It is intentionally stdlib-only and does not attempt to execute the real shell or
service families yet.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROTO = ROOT / "protocol" / "emvi-proof-slice" / "v0"
ARTIFACT_ROOT = ROOT / "artifacts" / "workspace" / "emvi-proof-slice"
VALIDATOR = ROOT / "tools" / "validate_emvi_proof_slice_fixtures.py"
DEMO_RUNNER = ROOT / "tools" / "run_emvi_proof_slice_demo.py"


def load_module(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def now_slug() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace(":", "-")


def run_validation() -> None:
    cp = subprocess.run([sys.executable, str(VALIDATOR)], cwd=str(ROOT), text=True)
    if cp.returncode != 0:
        raise SystemExit(cp.returncode)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="auto", help="Artifact directory or 'auto'")
    args = parser.parse_args()

    run_validation()

    demo_mod = load_module(DEMO_RUNNER, "emvi_proof_slice_demo")
    artifact = demo_mod.build_demo_artifact()

    if args.output_dir == "auto":
        out_dir = ARTIFACT_ROOT / now_slug()
    else:
        out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    artifact_path = out_dir / "demo-artifact.json"
    write_json(artifact_path, artifact)

    fixture_actionspec = PROTO / "fixtures" / "actionspec.example.json"
    fixture_events = PROTO / "fixtures" / "events.example.jsonl"
    shutil.copy2(fixture_actionspec, out_dir / fixture_actionspec.name)
    shutil.copy2(fixture_events, out_dir / fixture_events.name)

    manifest = {
        "kind": "EMVIProofSliceSmokeRun",
        "generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "protocolRef": "protocol/emvi-proof-slice/v0",
        "artifactPath": str(artifact_path.relative_to(ROOT)),
        "copiedFixtures": [
            str((out_dir / fixture_actionspec.name).relative_to(ROOT)),
            str((out_dir / fixture_events.name).relative_to(ROOT)),
        ],
        "summary": artifact.get("summary", {}),
    }
    write_json(out_dir / "run-manifest.json", manifest)

    print(f"OK: EMVI proof-slice smoke artifact bundle written to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
