# Proof Slice Demo Runner

Minimal current path:

```bash
python3 tools/validate_emvi_proof_slice_fixtures.py && \
python3 tools/run_emvi_proof_slice_demo.py --output artifacts/workspace/emvi-proof-slice-demo.json
```

This does **not** execute the real shell or service families yet.
It composes the governed fixture inputs into one concrete demo artifact so that
implementation can converge on a stable output shape before the full runtime exists.
