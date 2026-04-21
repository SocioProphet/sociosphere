# Workspace Fabric Validation

Current lightweight validation path:

```bash
python3 tools/validate_workspace_fabric_fixtures.py
```

This check currently validates:
- the mount registration request fixture shape
- the mount registration lease fixture shape
- the evidence-event fixture shape
- the lease renewal request fixture shape
- the lease revocation request fixture shape
- the authority-transition request fixture shape
- the authority-transition decision fixture shape
- the tombstone decision fixture shape
- the reconcile-required fixture shape
- the lifecycle transition fixture shape
- workspace, mount, authority, dataset, adapter, lease, quorum, state, and correlation consistency across the fixtures

It is intentionally minimal and dependency-free so the protocol slice can be checked in a bare workspace before a fuller schema-validation stack exists.
