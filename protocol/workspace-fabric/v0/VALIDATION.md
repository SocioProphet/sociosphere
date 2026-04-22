# Workspace Fabric Validation

Local validation path:

```bash
python3 tools/validate_workspace_fabric_fixtures.py
```

CI validation path:

- `.github/workflows/workspace-fabric.yml`

This check currently validates:
- the mount registration request fixture shape
- the mount registration lease fixture shape
- the evidence-event fixture shape
- the lease renewal request fixture shape
- the lease revocation request fixture shape
- the authority-transition request fixture shape
- the authority-transition decision fixture shape
- the policy-decision fixture shape
- the quorum-decision fixture shape
- the tombstone decision fixture shape
- the reconcile-required fixture shape
- the lifecycle transition fixture shape
- the adapter profile schema
- the TopoLVM, Hypercore, S3, rsync, and Drive adapter profile fixtures
- workspace, mount, authority, dataset, adapter, lease, quorum, policy, state, and correlation consistency across the fixtures

It is intentionally lightweight and dependency-free so the protocol slice can be checked in a bare workspace before a fuller schema-validation stack exists.
