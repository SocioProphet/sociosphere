# Proof Slice Validation

Current lightweight validation path:

```bash
python3 tools/validate_emvi_proof_slice_fixtures.py
```

This check currently validates:
- the ActionSpec fixture shape
- the event-envelope fixture shape
- cross-reference consistency between the fixture files

It is intentionally minimal and dependency-free so the proof-slice protocol can
be checked in a bare workspace before a fuller validation stack exists.
