#!/usr/bin/env python3
"""
schemas_check.py (v0)
Pedantic local validator for our JSON schemas:
- Parse all *.json
- Ensure each file has $schema, $id, type
- Resolve all local $ref targets (file + JSON Pointer)
- Fail on missing files, missing anchors, or invalid pointers

This is NOT full JSON Schema validation (which requires jsonschema or similar),
but it guarantees our schema graph is internally consistent and ref-safe.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple, List

def json_pointer_get(doc: Any, pointer: str) -> Any:
    # pointer like "#/$defs/iso_datetime" or "/$defs/iso_datetime"
    if pointer.startswith("#"):
        pointer = pointer[1:]
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        raise KeyError(f"Pointer must start with '/': {pointer!r}")
    cur = doc
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, list):
            idx = int(token)
            cur = cur[idx]
        elif isinstance(cur, dict):
            cur = cur[token]
        else:
            raise KeyError(f"Pointer segment {token!r} not resolvable on non-container")
    return cur

def walk_refs(obj: Any, out: List[str]) -> None:
    if isinstance(obj, dict):
        if "$ref" in obj and isinstance(obj["$ref"], str):
            out.append(obj["$ref"])
        for v in obj.values():
            walk_refs(v, out)
    elif isinstance(obj, list):
        for v in obj:
            walk_refs(v, out)

def split_ref(ref: str) -> Tuple[str, str]:
    # "common.v0.json#/$defs/iso_datetime" -> ("common.v0.json", "#/$defs/iso_datetime")
    if "#" in ref:
        f, frag = ref.split("#", 1)
        return f, "#" + frag
    return ref, "#"

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("schemas/json/delex/gtm-intelligence/v0")
    if not root.exists():
        print(f"ERR: schema root not found: {root}", file=sys.stderr)
        return 2

    files = sorted(root.glob("*.json"))
    if not files:
        print(f"ERR: no schema files found under: {root}", file=sys.stderr)
        return 2

    docs_by_path: Dict[Path, Any] = {}
    docs_by_id: Dict[str, Path] = {}
    errors: List[str] = []

    # Parse + basic shape checks
    for f in files:
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            errors.append(f"{f}: JSON parse error: {e}")
            continue

        for k in ("$schema", "$id", "type"):
            if k not in doc:
                errors.append(f"{f}: missing required key {k!r}")
        if doc.get("type") != "object":
            # our v0 schemas should all be object schemas
            errors.append(f"{f}: expected type='object', got {doc.get('type')!r}")

        docs_by_path[f] = doc
        if isinstance(doc.get("$id"), str):
            if doc["$id"] in docs_by_id:
                errors.append(f"{f}: duplicate $id also in {docs_by_id[doc['$id']]}")
            else:
                docs_by_id[doc["$id"]] = f

    if errors:
        print("Schema parse/shape errors:", file=sys.stderr)
        for e in errors:
            print(" -", e, file=sys.stderr)
        return 1

    # Resolve $ref targets
    for f, doc in list(docs_by_path.items()):
        refs: List[str] = []
        walk_refs(doc, refs)
        for r in refs:
            # We only support local file refs in v0 (relative file names within the schema dir).
            # Anything absolute is a policy violation at v0.
            if r.startswith("http://") or r.startswith("https://"):
                errors.append(f"{f}: external $ref not allowed in v0: {r}")
                continue

            ref_file, ref_ptr = split_ref(r)
            if ref_file == "" and ref_ptr.startswith("#"):
                # same-document ref
                try:
                    json_pointer_get(doc, ref_ptr)
                except Exception as e:
                    errors.append(f"{f}: bad self $ref {r}: {e}")
                continue

            target_path = (f.parent / ref_file).resolve()
            if target_path not in docs_by_path:
                # allow ref to sibling schema file even if not globbed (but it should be)
                if not target_path.exists():
                    errors.append(f"{f}: $ref file not found: {ref_file} (from {r})")
                    continue
                try:
                    target_doc = json.loads(target_path.read_text(encoding="utf-8"))
                except Exception as e:
                    errors.append(f"{f}: $ref file unreadable: {target_path}: {e}")
                    continue
                docs_by_path[target_path] = target_doc
            target_doc = docs_by_path[target_path]

            try:
                json_pointer_get(target_doc, ref_ptr)
            except Exception as e:
                errors.append(f"{f}: bad $ref pointer {r}: {e}")

    if errors:
        print("Schema $ref resolution errors:", file=sys.stderr)
        for e in errors:
            print(" -", e, file=sys.stderr)
        return 1

    print(f"OK: schemas_check passed for {len(files)} schema files under {root}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
