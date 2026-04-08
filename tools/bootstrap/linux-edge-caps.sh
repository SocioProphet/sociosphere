#!/usr/bin/env bash
set -euo pipefail

# Linux bootstrap for edge capabilities:
# - cdncheck (Go binary)
# - airshare (Python packaged as PEX-like single artifact placeholder)
#
# This script is DEV-LANE. For SourceOS base, CI should build artifacts, sign them, and publish.
#
# Outputs:
#   tools/bootstrap/edge-caps.lock

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOCK="$ROOT/tools/bootstrap/edge-caps.lock"
BIN_DIR="${BIN_DIR:-$ROOT/caps/bin}"
mkdir -p "$BIN_DIR"

echo "# edge caps lock (dev lane)" > "$LOCK"
date -u +"# generated: %Y-%m-%dT%H:%M:%SZ" >> "$LOCK"

# ---- cdncheck ----
if ! command -v cdncheck >/dev/null 2>&1; then
  if command -v go >/dev/null 2>&1; then
    echo "[+] installing cdncheck via go install (dev lane)"
    GOBIN="$BIN_DIR" go install -v github.com/projectdiscovery/cdncheck/cmd/cdncheck@latest
  else
    echo "error: go not found; install Go or provide cdncheck binary" >&2
    exit 127
  fi
else
  echo "[=] cdncheck already present at $(command -v cdncheck)"
fi

CDNCHK_VER="$( ( "$BIN_DIR/cdncheck" -version 2>/dev/null || cdncheck -version 2>/dev/null ) | head -n1 | tr -d '\r' )"
echo "cdncheck.version=$CDNCHK_VER" >> "$LOCK"

# ---- airshare ----
# We install from upstream repo and create a venv-backed wrapper in BIN_DIR.
# For SourceOS base lane, replace this with CI-built PEX/zipapp.
AIRSHARE_DIR="$ROOT/third_party/Airshare"
if [ ! -d "$AIRSHARE_DIR/.git" ]; then
  echo "[+] cloning KuroLabs/Airshare"
  mkdir -p "$(dirname "$AIRSHARE_DIR")"
  git clone https://github.com/KuroLabs/Airshare.git "$AIRSHARE_DIR"
fi

# Optional: pin commit here once chosen.
AIRSHARE_COMMIT="$(git -C "$AIRSHARE_DIR" rev-parse HEAD)"
echo "airshare.commit=$AIRSHARE_COMMIT" >> "$LOCK"

python3 -m venv "$AIRSHARE_DIR/.venv"
# shellcheck disable=SC1091
source "$AIRSHARE_DIR/.venv/bin/activate"
pip install -U pip wheel >/dev/null
if [ -f "$AIRSHARE_DIR/requirements.txt" ]; then
  pip install -r "$AIRSHARE_DIR/requirements.txt" >/dev/null
fi

ENTRY="$(ls -1 "$AIRSHARE_DIR"/*.py 2>/dev/null | head -n1)"
if [ -z "$ENTRY" ]; then
  echo "error: could not locate Airshare entrypoint (*.py) in $AIRSHARE_DIR" >&2
  exit 2
fi

cat > "$BIN_DIR/airshare" <<EOF
#!/usr/bin/env bash
exec "$AIRSHARE_DIR/.venv/bin/python" "$ENTRY" "\$@"
EOF
chmod +x "$BIN_DIR/airshare"

AIRSHARE_HELP="$("$BIN_DIR/airshare" -h 2>/dev/null | head -n1 | tr -d '\r' || true)"
echo "airshare.help_head=$AIRSHARE_HELP" >> "$LOCK"

echo "[ok] installed to: $BIN_DIR"
echo "[ok] lock written: $LOCK"
