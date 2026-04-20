"""Helpers for lightweight validation of normalized software operational-risk records.

This module intentionally avoids external dependencies and focuses on the minimum
shape guarantees needed by the first harvester lane.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .record_shapes import REQUIRED_KEYS, URN_PREFIXES


def validate_record_shape(payload: Dict[str, Any]) -> List[str]:
    """Return a list of validation errors for a normalized record payload."""
    errors: List[str] = []
    obj_type = payload.get("type")
    if obj_type not in REQUIRED_KEYS:
        return [f"unknown type: {obj_type!r}"]

    for key in REQUIRED_KEYS[obj_type]:
        if key not in payload:
            errors.append(f"missing required key: {key}")

    record_id = payload.get("id")
    prefix = URN_PREFIXES[obj_type]
    if not isinstance(record_id, str):
        errors.append("id must be a string")
    elif not record_id.startswith(prefix):
        errors.append(f"id must start with {prefix}")

    if obj_type == "SoftwareOperationalIncident":
        refs = payload.get("sourceRefs")
        if not isinstance(refs, list) or not refs:
            errors.append("sourceRefs must be a non-empty list")

    if obj_type == "UpstreamWatchItem":
        signals = payload.get("signals")
        if not isinstance(signals, list) or not signals:
            errors.append("signals must be a non-empty list")

    return errors


def summarize_validation(payloads: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return a compact validation summary for a list of normalized records."""
    summary = {
        "checked": 0,
        "valid": 0,
        "invalid": 0,
        "errors": [],
    }
    for payload in payloads:
        summary["checked"] += 1
        errors = validate_record_shape(payload)
        if errors:
            summary["invalid"] += 1
            summary["errors"].append({
                "id": payload.get("id"),
                "type": payload.get("type"),
                "errors": errors,
            })
        else:
            summary["valid"] += 1
    return summary
