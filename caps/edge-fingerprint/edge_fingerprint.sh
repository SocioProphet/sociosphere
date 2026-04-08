#!/usr/bin/env bash
set -euo pipefail

# cap.edge.fingerprint@0.1 shim
# Depends on: cdncheck in PATH
# Emits: jsonl results to stdout, and a Cairn receipt to ./out/cairn.edge.fingerprint.json

OUTDIR="${OUTDIR:-./out}"
MODE="${MODE:-any}" # any|cdn|cloud|waf
mkdir -p "$OUTDIR"

if ! command -v cdncheck >/dev/null 2>&1; then
  echo "error: cdncheck not found in PATH" >&2
  exit 127
fi

if [ "$#" -lt 1 ]; then
  echo "usage: $0 <target> [target...]" >&2
  exit 2
fi

# Build args
ARGS=()
case "$MODE" in
  any) ;;
  cdn) ARGS+=("-cdn") ;;
  cloud) ARGS+=("-cloud") ;;
  waf) ARGS+=("-waf") ;;
  *) echo "error: MODE must be one of any|cdn|cloud|waf" >&2; exit 2 ;;
esac

# Run cdncheck in jsonl mode.
# Note: cdncheck's -jsonl writes json(line) format. We keep it as our stable wire format.
cdncheck -i "$@" -jsonl "${ARGS[@]}" | tee "$OUTDIR/results.jsonl" >/dev/null

# Evidence: attempt to capture tool version; sources hash is best-effort (unknown unless we can locate sources_data.json).
TOOL_VERSION="$(cdncheck -version 2>/dev/null | tr -d '\r' | head -n1 | sed 's/^[^0-9]*//')"
[ -z "$TOOL_VERSION" ] && TOOL_VERSION="unknown"

# sources_hash: we can’t reliably locate provider index from installed binary without conventions.
# We keep placeholder "unknown" until we implement a deterministic build/install lane.
SOURCES_HASH="unknown"

python3 - <<'PY'
import json, os, hashlib, datetime
outdir = os.environ.get("OUTDIR","./out")
tool_version = os.environ.get("TOOL_VERSION","unknown")
sources_hash = os.environ.get("SOURCES_HASH","unknown")
targets = os.environ.get("TARGETS","").splitlines()
results_path = os.path.join(outdir, "results.jsonl")

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1024*1024), b""):
            h.update(b)
    return h.hexdigest()

# We do minimal parsing: store raw jsonl hash and leave detailed extraction to later.
receipt = {
  "cairn_type": "cairn.edge.fingerprint",
  "version": "0.1",
  "event_time": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
  "input": {"targets": targets},
  "results": [],
  "evidence": {
    "tool": "cdncheck",
    "tool_version": tool_version,
    "sources_hash": sources_hash,
    "results_jsonl_sha256": sha256_file(results_path) if os.path.exists(results_path) else None
  }
}

with open(os.path.join(outdir, "cairn.edge.fingerprint.json"), "w", encoding="utf-8") as f:
    json.dump(receipt, f, indent=2, sort_keys=True)
PY
