#!/usr/bin/env bash
set -euo pipefail

NH="${NEW_HOPE_REPO:?set NEW_HOPE_REPO}"
ST="${SLASH_TOPICS_REPO:?set SLASH_TOPICS_REPO}"
PACK="${NH_ST_PACK:-}"

for d in "$NH" "$ST"; do
  test -d "$d" || { echo "[fail] missing dir: $d"; exit 2; }
  test -f "$d/LICENSE" || { echo "[fail] missing LICENSE in $d"; exit 2; }
  find "$d" -name '.DS_Store' -print -quit | grep -q . && { echo "[fail] .DS_Store in $d"; exit 2; } || true
  find "$d" -type d -name '__MACOSX' -print -quit | grep -q . && { echo "[fail] __MACOSX in $d"; exit 2; } || true
done

if [[ -n "$PACK" && -f "$PACK/tools/validate_newhope_slash_topics.py" ]]; then
  python3 -m venv .venv-nh-st >/dev/null 2>&1 || true
  source .venv-nh-st/bin/activate
  python -m pip install -U pip >/dev/null
  pip install -q jsonschema
  python "$PACK/tools/validate_newhope_slash_topics.py" "$PACK" "$NH" "$ST"
  echo "[ok] nh/slash schema validation passed"
else
  echo "[warn] pack validator not found; only hygiene/license validated"
fi
