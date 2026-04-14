import sys, re, yaml
from pathlib import Path

P = Path("standards/ui/component-inventory.v1.yaml")
if not P.exists():
    print("ERR: missing", P)
    sys.exit(1)

d = yaml.safe_load(P.read_text())

# Minimal but strict-enough guardrails (we harden next):
def bad(msg): 
    print("ERR:", msg); sys.exit(1)

rules = d.get("id_rules", {})
if "component_id_format" not in rules: bad("id_rules.component_id_format missing")
if "action_id_format" not in rules: bad("id_rules.action_id_format missing")

seen = set()
for c in d.get("components", []):
    cid = c.get("id")
    if not cid: bad("component missing id")
    if cid in seen: bad(f"duplicate component id: {cid}")
    seen.add(cid)

    if not cid.startswith("ui."): bad(f"component id must start with ui.: {cid}")
    if " " in cid: bad(f"component id contains space: {cid}")
    if cid.count(".") < 5: bad(f"component id too short (need >=6 segments): {cid}")

    for a in c.get("actions", []):
        if not a.startswith("action."): bad(f"action id must start with action.: {a} (in {cid})")

print(f"OK: validated {len(seen)} components")
