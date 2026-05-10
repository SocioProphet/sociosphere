#!/usr/bin/env python3
"""Validate Superconscious / SourceOS reasoning artifacts for SocioSphere.

SocioSphere owns workspace topology, registry governance, and source-exposure posture.
This validator is dependency-free and read-only. It validates canonical SourceOS
reasoning artifacts emitted by Superconscious without executing agents or requiring
raw private reasoning content.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


REQUIRED_CANONICAL = [
    "reasoning-events.sourceos.jsonl",
    "reasoning-run.sourceos.json",
    "reasoning-receipt.json",
    "reasoning-replay-plan.json",
    "reasoning-benchmark.json",
]
VALID_REPLAY_CLASSES = {"exact", "best-effort", "evidence-only", "non-replayable-side-effect"}
VALID_TRACE_LEVELS = {"public-safe", "workspace-safe", "operator-private", "restricted"}
VALID_TRUST_LEVELS = {
    "trusted-control-input",
    "trusted-workspace-source",
    "semi-trusted-project-source",
    "untrusted-observation",
    "restricted-material",
}
SENSITIVE_MARKERS = ["credential-marker", "secret-marker", "raw-private-material"]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def validate_reasoning_dir(run_dir: Path) -> Dict[str, Any]:
    run_dir = run_dir.resolve()
    errors: List[str] = []
    warnings: List[str] = []

    for artifact in REQUIRED_CANONICAL:
        if not (run_dir / artifact).exists():
            errors.append(f"missing canonical artifact: {artifact}")

    if errors:
        return _report(run_dir, None, errors, warnings)

    events = load_jsonl(run_dir / "reasoning-events.sourceos.jsonl")
    reasoning_run = load_json(run_dir / "reasoning-run.sourceos.json")
    receipt = load_json(run_dir / "reasoning-receipt.json")
    replay = load_json(run_dir / "reasoning-replay-plan.json")
    benchmark = load_json(run_dir / "reasoning-benchmark.json")

    run_id = reasoning_run.get("id")
    workspace_ref = reasoning_run.get("workspaceRef")

    if reasoning_run.get("type") != "ReasoningRun":
        errors.append("reasoning-run.sourceos.json type must be ReasoningRun")
    if not str(run_id or "").startswith("urn:srcos:reasoning-run:"):
        errors.append("ReasoningRun.id must be a SourceOS reasoning-run URN")
    if not workspace_ref:
        errors.append("ReasoningRun.workspaceRef is required for SocioSphere validation")
    if workspace_ref and not str(workspace_ref).startswith("urn:socioprophet:workspace:"):
        warnings.append("ReasoningRun.workspaceRef is not a SocioProphet workspace URN")

    safe_trace = reasoning_run.get("safeTrace", {})
    if safe_trace.get("mode") != "operational-trace-only":
        errors.append("ReasoningRun.safeTrace.mode must be operational-trace-only")
    if safe_trace.get("rawPrivateReasoning") != "not-collected":
        errors.append("ReasoningRun.safeTrace.rawPrivateReasoning must be not-collected")

    event_ids = set()
    for index, event in enumerate(events, start=1):
        event_id = event.get("id")
        event_ids.add(event_id)
        if event.get("type") != "ReasoningEvent":
            errors.append(f"event line {index} type must be ReasoningEvent")
        if event.get("runRef") != run_id:
            errors.append(f"event line {index} runRef mismatch")
        if event.get("traceLevel") not in VALID_TRACE_LEVELS:
            errors.append(f"event line {index} traceLevel is invalid")
        if event.get("trustLevel") not in VALID_TRUST_LEVELS:
            errors.append(f"event line {index} trustLevel is invalid")
        summary = str(event.get("summary", "")).lower()
        if any(marker in summary for marker in SENSITIVE_MARKERS):
            errors.append(f"event line {index} summary appears to contain restricted marker text")

    missing_event_refs = sorted(ref for ref in reasoning_run.get("eventRefs", []) if ref not in event_ids)
    if missing_event_refs:
        errors.append(f"ReasoningRun.eventRefs missing from event stream: {missing_event_refs}")
    if len(events) != safe_trace.get("eventCount"):
        errors.append("ReasoningRun.safeTrace.eventCount must equal event stream length")

    if receipt.get("type") != "ReasoningReceipt" or receipt.get("runRef") != run_id:
        errors.append("ReasoningReceipt must reference the ReasoningRun")
    if not receipt.get("traceHash"):
        errors.append("ReasoningReceipt.traceHash is required")

    if replay.get("type") != "ReasoningReplayPlan" or replay.get("runRef") != run_id:
        errors.append("ReasoningReplayPlan must reference the ReasoningRun")
    if replay.get("replayClass") not in VALID_REPLAY_CLASSES:
        errors.append("ReasoningReplayPlan.replayClass is invalid")

    if benchmark.get("type") != "ReasoningBenchmark" or benchmark.get("runRef") != run_id:
        errors.append("ReasoningBenchmark must reference the ReasoningRun")
    if benchmark.get("passed") is not True:
        errors.append("ReasoningBenchmark.passed must be true")

    summary = {
        "runId": run_id,
        "workspaceRef": workspace_ref,
        "status": reasoning_run.get("status"),
        "eventCount": len(events),
        "safeTraceMode": safe_trace.get("mode"),
        "rawPrivateReasoning": safe_trace.get("rawPrivateReasoning"),
        "receiptRef": receipt.get("id"),
        "replayClass": replay.get("replayClass"),
        "benchmarkRef": benchmark.get("id"),
        "benchmarkSuite": benchmark.get("suite"),
    }
    return _report(run_dir, summary, errors, warnings)


def _report(run_dir: Path, summary: Dict[str, Any] | None, errors: List[str], warnings: List[str]) -> Dict[str, Any]:
    return {
        "schema_version": "sociosphere.superconscious-reasoning-validation/v1",
        "generated_at": now_iso(),
        "run_dir": str(run_dir),
        "result": "pass" if not errors else "fail",
        "summary": summary or {},
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Superconscious reasoning artifacts for SocioSphere.")
    parser.add_argument("run_dir", help="Directory containing canonical SourceOS reasoning artifacts")
    parser.add_argument("--json-out", default=None, help="Optional path to write validation report JSON")
    args = parser.parse_args(argv)

    try:
        report = validate_reasoning_dir(Path(args.run_dir))
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"superconscious reasoning validation failed: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
