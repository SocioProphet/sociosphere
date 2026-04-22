#!/usr/bin/env python3
"""Workspace wrapper for the EMVI proof-slice smoke path.

This keeps the EMVI smoke flow close to the canonical workspace runner/tooling
surface even before `tools/runner/runner.py` gets a dedicated subcommand.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools" / "validate_emvi_proof_slice_fixtures.py"
SMOKE = ROOT / "tools" / "run_emvi_proof_slice_smoke.py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="auto", help="Artifact output directory or 'auto'")
    args = parser.parse_args()

    cp = subprocess.run([sys.executable, str(VALIDATOR)], cwd=str(ROOT), text=True)
    if cp.returncode != 0:
        return cp.returncode

    cmd = [sys.executable, str(SMOKE)]
    if args.output_dir:
        cmd.extend(["--output-dir", args.output_dir])
    return subprocess.run(cmd, cwd=str(ROOT), text=True).returncode


if __name__ == "__main__":
    raise SystemExit(main())
