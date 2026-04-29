# Proof Slice Smoke Runner

Current lightweight path:

```bash
python3 tools/run_emvi_proof_slice_smoke.py
```

Outputs:
- `artifacts/workspace/emvi-proof-slice/<timestamp>/demo-artifact.json`
- `artifacts/workspace/emvi-proof-slice/<timestamp>/run-manifest.json`
- copied fixture inputs for the run

Behavior:
1. validate merged fixtures via `tools/validate_emvi_proof_slice_fixtures.py`
2. compose the demo artifact from the governed fixture inputs
3. emit a small artifact bundle under `artifacts/workspace/`

This remains synthetic by design. It gives the repo a stable execution-shaped
artifact to target before the real proof-slice runtime exists.
