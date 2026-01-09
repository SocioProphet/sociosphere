from pathlib import Path
import sys

# tools/conformance/trirpc-v0/tools/conformance/trirpc_v0/smoke.py
# repo root is 5 levels up from this file
ROOT = Path(__file__).resolve().parents[5]

REQ = [
    ROOT / "schemas/avro/trirpc/envelope.v0.avsc",
    ROOT / "schemas/avro/trirpc/value.v0.avsc",
    ROOT / "schemas/avro/trirpc/error.v0.avsc",
    ROOT / "schemas/schemasalad/trirpc-schema-bundle.v0.yml",
]

missing = [str(p) for p in REQ if not p.exists()]
if missing:
    print("ERR: missing required TriRPC v0 artifacts:")
    for m in missing:
        print(" -", m)
    sys.exit(2)

print("OK: TriRPC v0 artifacts present")
