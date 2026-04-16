#!/usr/bin/env python3
"""Normalize official status-history payloads into software operational-risk incident records.

This is the first harvester scaffold for the software operational risk lane.
It intentionally starts with a narrow, explicit contract:

- read a JSON payload exported or fetched from an official status-history surface;
- normalize incidents into the SourceOS/SociOS typed contract shape;
- write JSON Lines suitable for registry ingestion and later scenario modeling.

The script currently supports a generic Atlassian Statuspage-style payload, which is
sufficient for many provider status pages and provides a concrete starting point for
provider-specific adapters.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse


STATUS_SOURCES: Dict[str, Dict[str, Any]] = {
    "openai": {
        "provider": "OpenAI",
        "mode": "statuspage",
        "status_url": "https://status.openai.com/history",
        "default_event_family": "system_platform_disruption",
        "default_layer": "model_provider",
        "default_tags": ["model-provider", "statuspage"],
    },
    "github": {
        "provider": "GitHub",
        "mode": "statuspage",
        "status_url": "https://www.githubstatus.com/history",
        "default_event_family": "system_platform_disruption",
        "default_layer": "control_plane",
        "default_tags": ["github", "statuspage"],
    },
    "npm": {
        "provider": "npm",
        "mode": "statuspage",
        "status_url": "https://status.npmjs.org/history",
        "default_event_family": "supply_chain_upstream_failure",
        "default_layer": "registry",
        "default_tags": ["npm", "registry", "statuspage"],
    },
}


STATUS_MAP = {
    "investigating": "investigating",
    "identified": "identified",
    "monitoring": "monitoring",
    "resolved": "resolved",
    "postmortem_published": "resolved",
}

IMPACT_MAP = {
    "none": "low",
    "minor": "medium",
    "major": "high",
    "critical": "critical",
}


@dataclass
class NormalizedIncident:
    payload: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(self.payload, sort_keys=False)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def duration_minutes(started_at: Optional[str], ended_at: Optional[str]) -> Optional[int]:
    start_dt = parse_iso(started_at)
    end_dt = parse_iso(ended_at)
    if not start_dt or not end_dt:
        return None
    delta = end_dt - start_dt
    return max(int(delta.total_seconds() // 60), 0)


def make_incident_urn(provider_key: str, title: str, started_at: Optional[str]) -> str:
    slug_title = "".join(ch.lower() if ch.isalnum() else "-" for ch in title).strip("-")
    slug_title = "-".join(part for part in slug_title.split("-") if part)
    date_part = (started_at or "unknown").split("T", 1)[0]
    return f"urn:srcos:oprisk-incident:{provider_key}:{date_part}:{slug_title[:80]}"


def make_source_ref(url: Optional[str], observed_at: str, note: Optional[str] = None) -> Dict[str, Any]:
    ref = {
        "kind": "status_page",
        "uri": url or "https://example.invalid/status-page",
        "observedAt": observed_at,
    }
    if note:
        ref["note"] = note
    return ref


def extract_statuspage_incidents(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(payload.get("incidents"), list):
        return payload["incidents"]
    if isinstance(payload.get("data"), dict) and isinstance(payload["data"].get("incidents"), list):
        return payload["data"]["incidents"]
    raise ValueError("Could not locate a top-level incident list in the input payload.")


def normalize_statuspage_payload(provider_key: str, payload: Dict[str, Any]) -> List[NormalizedIncident]:
    config = STATUS_SOURCES[provider_key]
    observed_at = now_iso()
    normalized: List[NormalizedIncident] = []

    for raw in extract_statuspage_incidents(payload):
        title = raw.get("name") or raw.get("title") or "Untitled incident"
        status = STATUS_MAP.get(raw.get("status", ""), "investigating")
        impact = IMPACT_MAP.get(raw.get("impact", ""), "medium")
        started_at = raw.get("created_at") or raw.get("started_at") or raw.get("createdAt")
        ended_at = raw.get("resolved_at") or raw.get("ended_at") or raw.get("resolvedAt")
        url = raw.get("shortlink") or raw.get("incident_url") or config["status_url"]
        incident = {
            "id": make_incident_urn(provider_key, title, started_at),
            "type": "SoftwareOperationalIncident",
            "specVersion": "2.0.0",
            "incidentTitle": title,
            "provider": config["provider"],
            "product": raw.get("name") or title,
            "eventFamily": config["default_event_family"],
            "affectedLayer": config["default_layer"],
            "status": status,
            "severity": impact,
            "startedAt": started_at or observed_at,
            "evidenceGrade": "timing_scope_only",
            "sourceRefs": [
                make_source_ref(url, observed_at, note="Normalized from provider status-history payload.")
            ],
            "tags": list(config.get("default_tags", [])),
        }
        if ended_at:
            incident["endedAt"] = ended_at
            maybe_duration = duration_minutes(started_at, ended_at)
            if maybe_duration is not None:
                incident["durationMinutes"] = maybe_duration
        components = raw.get("components")
        if isinstance(components, list):
            names = [c.get("name") for c in components if isinstance(c, dict) and c.get("name")]
            if names:
                incident["affectedServices"] = names
        if raw.get("incident_updates"):
            updates = raw["incident_updates"]
            if isinstance(updates, list) and updates:
                latest = updates[-1]
                body = latest.get("body") if isinstance(latest, dict) else None
                if body:
                    incident["rootCauseSummary"] = body[:500]
        normalized.append(NormalizedIncident(incident))
    return normalized


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_jsonl(path: Path, incidents: Iterable[NormalizedIncident]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in incidents:
            handle.write(item.to_json())
            handle.write("\n")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider", choices=sorted(STATUS_SOURCES.keys()), help="Named provider source configuration.")
    parser.add_argument("--input", required=True, help="Path to a JSON payload exported from a provider status-history surface.")
    parser.add_argument("--output", required=True, help="Path to the normalized JSONL output file.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    payload = load_json(Path(args.input))
    incidents = normalize_statuspage_payload(args.provider, payload)
    write_jsonl(Path(args.output), incidents)
    print(f"wrote {len(incidents)} incidents to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
