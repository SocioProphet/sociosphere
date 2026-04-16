"""Shared normalized record metadata for the software operational risk lane."""

REQUIRED_KEYS = {
    "SoftwareOperationalIncident": [
        "id",
        "type",
        "specVersion",
        "incidentTitle",
        "provider",
        "eventFamily",
        "status",
        "startedAt",
        "evidenceGrade",
        "sourceRefs",
    ],
    "UpstreamWatchItem": [
        "id",
        "type",
        "specVersion",
        "subjectType",
        "subjectKey",
        "observedAt",
        "riskState",
        "signals",
    ],
}

URN_PREFIXES = {
    "SoftwareOperationalIncident": "urn:srcos:oprisk-incident:",
    "UpstreamWatchItem": "urn:srcos:upstream-watch:",
}
