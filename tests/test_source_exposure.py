from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_source_exposure_checker_blocks_private_key(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    policy_dir = repo / "standards" / "source-exposure"
    policy_dir.mkdir(parents=True)
    source_policy = Path("standards/source-exposure/policy.v0.json")
    policy_dir.joinpath("policy.v0.json").write_text(source_policy.read_text("utf-8"), "utf-8")

    begin_private_key = "-----BEGIN " + "PRIVATE KEY-----"
    end_private_key = "-----END " + "PRIVATE KEY-----"
    secret = repo / "bad.pem"
    secret.write_text(f"{begin_private_key}\nredacted\n{end_private_key}\n", "utf-8")

    cp = subprocess.run(
        [
            "python3",
            "tools/check_source_exposure.py",
            "--root",
            str(repo),
            "--policy",
            "standards/source-exposure/policy.v0.json",
            "--json-out",
            "-",
        ],
        cwd=Path.cwd(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert cp.returncode == 2
    report = json.loads(cp.stdout)
    assert report["result"] == "fail"
    assert report["counts"]["block"] >= 1


def test_source_exposure_checker_allows_redacted_example(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    policy_dir = repo / "standards" / "source-exposure"
    policy_dir.mkdir(parents=True)
    source_policy = Path("standards/source-exposure/policy.v0.json")
    policy_dir.joinpath("policy.v0.json").write_text(source_policy.read_text("utf-8"), "utf-8")

    example = repo / "README.md"
    example.write_text("WEBHOOK_SECRET=<shared-secret>\n", "utf-8")

    cp = subprocess.run(
        [
            "python3",
            "tools/check_source_exposure.py",
            "--root",
            str(repo),
            "--policy",
            "standards/source-exposure/policy.v0.json",
            "--json-out",
            "-",
        ],
        cwd=Path.cwd(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert cp.returncode == 0
    report = json.loads(cp.stdout)
    assert report["result"] == "pass"
