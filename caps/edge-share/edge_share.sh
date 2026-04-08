#!/usr/bin/env bash
set -euo pipefail

# cap.edge.share@0.1 shim
# Depends on: airshare in PATH
# Emits: a Cairn receipt to ./out/cairn.edge.share.transfer.json (per invocation)

OUTDIR="${OUTDIR:-./out}"
DIRECTION="${DIRECTION:-send}" # send|receive
PEER="${PEER:-}"
SAVE_DIR="${SAVE_DIR:-}"
CLIPBOARD_SEND="${CLIPBOARD_SEND:-}" # if set, send as clipboard text
CLIPBOARD_COPY="${CLIPBOARD_COPY:-false}" # true to copy received clipboard when compatible
mkdir -p "$OUTDIR"

if ! command -v airshare >/dev/null 2>&1; then
  echo "error: airshare not found in PATH" >&2
  exit 127
fi

if [ -z "$PEER" ]; then
  echo "error: PEER is required (Airshare username/handle)" >&2
  exit 2
fi

TOOL_VERSION="$(airshare -h 2>/dev/null | head -n1 | tr -d '\r')"
[ -z "$TOOL_VERSION" ] && TOOL_VERSION="unknown"

if [ "$DIRECTION" = "send" ]; then
  if [ -n "$CLIPBOARD_SEND" ]; then
    # Send clipboard text
    airshare -cs "$PEER" <<<"$CLIPBOARD_SEND"
    CLIP_SHA="$(printf '%s' "$CLIPBOARD_SEND" | shasum -a 256 | awk '{print $1}')"
    python3 - <<PY
import json, os, datetime
outdir=os.environ.get("OUTDIR","./out")
peer=os.environ["PEER"]
tool_version=os.environ.get("TOOL_VERSION","unknown")
clip_sha=os.environ.get("CLIP_SHA","")
receipt={
 "cairn_type":"cairn.edge.share.transfer",
 "version":"0.1",
 "event_time": datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
 "direction":"send",
 "peer": peer,
 "payload":{"clipboard_text_sha256": clip_sha},
 "evidence":{"tool":"airshare","tool_version":tool_version,"discovery":{"method":"mdns","service":"unknown"}}
}
with open(os.path.join(outdir,"cairn.edge.share.transfer.json"),"w",encoding="utf-8") as f:
  json.dump(receipt,f,indent=2,sort_keys=True)
PY
  else
    if [ "$#" -lt 1 ]; then
      echo "usage: PEER=<peer> DIRECTION=send $0 <path> [path...]" >&2
      exit 2
    fi
    # Send files/paths
    airshare -u "$PEER" "$@"
    python3 - <<PY
import json, os, datetime
outdir=os.environ.get("OUTDIR","./out")
peer=os.environ["PEER"]
tool_version=os.environ.get("TOOL_VERSION","unknown")
paths=os.environ.get("PATHS","").splitlines()
receipt={
 "cairn_type":"cairn.edge.share.transfer",
 "version":"0.1",
 "event_time": datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
 "direction":"send",
 "peer": peer,
 "payload":{"paths": paths},
 "evidence":{"tool":"airshare","tool_version":tool_version,"discovery":{"method":"mdns","service":"unknown"}}
}
with open(os.path.join(outdir,"cairn.edge.share.transfer.json"),"w",encoding="utf-8") as f:
  json.dump(receipt,f,indent=2,sort_keys=True)
PY
  fi
elif [ "$DIRECTION" = "receive" ]; then
  # Receive: Airshare UX is interactive; we log receipt stub now and tighten later.
  # If SAVE_DIR set, user should run in that dir; for now we just invoke base receive mode (no flags).
  if [ "$CLIPBOARD_COPY" = "true" ]; then
    airshare -cr "$PEER"
  else
    airshare "$PEER"
  fi
  python3 - <<PY
import json, os, datetime
outdir=os.environ.get("OUTDIR","./out")
peer=os.environ["PEER"]
tool_version=os.environ.get("TOOL_VERSION","unknown")
receipt={
 "cairn_type":"cairn.edge.share.transfer",
 "version":"0.1",
 "event_time": datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z",
 "direction":"receive",
 "peer": peer,
 "payload":{},
 "evidence":{"tool":"airshare","tool_version":tool_version,"discovery":{"method":"mdns","service":"unknown"}}
}
with open(os.path.join(outdir,"cairn.edge.share.transfer.json"),"w",encoding="utf-8") as f:
  json.dump(receipt,f,indent=2,sort_keys=True)
PY
else
  echo "error: DIRECTION must be send|receive" >&2
  exit 2
fi
