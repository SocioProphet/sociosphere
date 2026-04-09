# metrics/README.md
# Metrics Directory

This directory contains runtime metric files produced by the
`engines/metrics_collector.py` and related engines.

## Files

| File | Description |
|---|---|
| `registry-metrics.json` | Latest snapshot of all metrics (written by `cli/measure-success.py`) |
| `propagation-log.jsonl` | Append-only log of every propagation event (JSONL) |
| `devops-log.jsonl` | Append-only log of every DevOps automation run (JSONL) |
| `automation-summary.yaml` | Human-readable automation effectiveness summary |

## Usage

```bash
# Print dashboard to console and save snapshot
python cli/measure-success.py

# Print only (no file write)
python cli/measure-success.py --no-save

# Update automation summary
python engines/metrics_collector.py
```

## Metric Targets

| Metric | Week 1 | Week 4 | Week 8 | Target |
|---|---|---|---|---|
| Registry completeness | 40% | 70% | 90% | 100% |
| Automation success rate | 75% | 90% | 97% | >95% |
| Deduplication progress | 0% | 50% | 100% | 100% |
