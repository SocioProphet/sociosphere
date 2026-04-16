from __future__ import annotations

from pathlib import Path


SCHEMA_ROOT = Path("schemas") / "fabric"

MANIFEST_V1 = SCHEMA_ROOT / "manifest.v1.schema.json"
INDEXPACK_V1 = SCHEMA_ROOT / "indexpack.v1.schema.json"
CAPABILITY_GRANT_V1 = SCHEMA_ROOT / "capability-grant.v1.schema.json"
EVIDENCE_EVENT_V1 = SCHEMA_ROOT / "evidence-event.v1.schema.json"


def schema_paths() -> dict[str, Path]:
    return {
        "manifest.v1": MANIFEST_V1,
        "indexpack.v1": INDEXPACK_V1,
        "capability-grant.v1": CAPABILITY_GRANT_V1,
        "evidence-event.v1": EVIDENCE_EVENT_V1,
    }
