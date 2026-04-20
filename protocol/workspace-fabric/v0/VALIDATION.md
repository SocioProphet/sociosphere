# Workspace Fabric Validation

Current lightweight validation path:

```bash
python3 tools/validate_workspace_fabric_fixtures.py
```

This check currently validates:
- the request fixture top-level and nested required fields
- the lease fixture top-level and nested required fields
- the evidence-event fixture top-level required fields
- workspace, mount, authority, dataset, and adapter consistency across fixtures

It is intentionally minimal and dependency-free so the protocol slice can be checked in a bare workspace before a fuller schema-validation stack exists.
