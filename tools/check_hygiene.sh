#!/usr/bin/env bash
# check_hygiene.sh – fail CI if macOS cruft files are committed or if submodules are un-pinned.
#
# Usage: bash tools/check_hygiene.sh
# Exit 0 on success, 1 on any violation.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

# ── 1. macOS cruft check ────────────────────────────────────────────────────
echo "==> Checking for macOS cruft files..."

# Search tracked files only (avoids false positives from untracked builds/caches)
CRUFT=$(git -C "$ROOT" ls-files | grep -E '(^|/)\.DS_Store$|(^|/)__MACOSX(\/|$)|(^|/)\._' || true)

if [[ -n "$CRUFT" ]]; then
    echo "FAIL: macOS cruft files found in the repository:" >&2
    echo "$CRUFT" | sed 's/^/  /' >&2
    echo "Remove them with: git rm --cached <file>" >&2
    FAIL=1
else
    echo "OK: no macOS cruft files detected"
fi

# ── 2. Submodule pin sanity ──────────────────────────────────────────────────
echo "==> Checking submodule pin sanity..."

LOCK="$ROOT/manifest/workspace.lock.json"

if [[ ! -f "$LOCK" ]]; then
    echo "WARN: manifest/workspace.lock.json not found; skipping submodule pin check"
else
    # Parse .gitmodules to get submodule names and paths
    if [[ -f "$ROOT/.gitmodules" ]]; then
        while IFS= read -r line; do
            if [[ "$line" =~ submodule\ \"(.+)\" ]]; then
                SM_NAME="${BASH_REMATCH[1]}"
            elif [[ "$line" =~ path\ =\ (.+) ]]; then
                SM_PATH="${BASH_REMATCH[1]// /}"
                # Check that this submodule path corresponds to a pinned entry in the lock
                PINNED=$(python3 - "$LOCK" "$SM_PATH" <<'PYEOF'
import json, sys
lock = json.load(open(sys.argv[1]))
path = sys.argv[2]
for r in lock.get("repos", []):
    if (r.get("local_path") or "").rstrip("/") == path.rstrip("/"):
        rev = r.get("rev")
        if rev:
            print("pinned:" + rev)
        else:
            print("unpinned")
        sys.exit(0)
print("missing")
PYEOF
)
                if [[ "$PINNED" == "unpinned" ]]; then
                    echo "FAIL: submodule '$SM_PATH' has no rev pinned in manifest/workspace.lock.json" >&2
                    FAIL=1
                elif [[ "$PINNED" == "missing" ]]; then
                    echo "FAIL: submodule '$SM_PATH' is not tracked in manifest/workspace.lock.json" >&2
                    FAIL=1
                else
                    echo "OK: submodule '$SM_PATH' pinned to ${PINNED#pinned:}"
                fi
            fi
        done < "$ROOT/.gitmodules"
    else
        echo "OK: no .gitmodules found; nothing to check"
    fi
fi

if [[ "$FAIL" -ne 0 ]]; then
    echo "" >&2
    echo "hygiene-check: FAILED — resolve violations above before merging" >&2
    exit 1
fi

echo "hygiene-check: OK"
