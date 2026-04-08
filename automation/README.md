# Automation Framework — Phase A: Autonomous Registry Management

This directory contains the complete automation framework that makes
Sociosphere self-managing: webhook ingestion, job scheduling, API rate
limiting, change propagation, and DevOps orchestration.

---

## Architecture

```
GitHub Events (push to main on any of the 76 repos)
    │
    ▼ (HMAC-SHA256 validated)
Webhook Handler  (automation/webhooks.py — Flask, port 5000)
    │
    ▼ (thread-safe queue)
Event Queue
    │
    ▼ (drained every minute)
Scheduler  (automation/scheduler.py — APScheduler)
    ├─ Hourly  : Registry Rebuild  (~200 API calls)
    ├─ Daily   : Deep Scan @ 02:00 UTC (~800 API calls)
    └─ 1 min   : Drain webhook queue
    │
    ▼
Rate Limiter  (automation/rate_limiter.py)
    │ 5 000 req/h  ·  500 safety buffer  ·  adaptive backoff @ 80 %
    ▼
Propagation Handler  (automation/propagation_handler.py)
    │ look up repo → find dependents → trigger action per change type
    ▼
DevOps Orchestrator  (automation/devops_orchestrator.py)
    │ build → test → deploy staging → deploy prod → rollback on failure
    ▼
Metrics Collector  (automation/metrics_collector.py)
    │ API usage · propagation success · latency · cost · dedup progress
    ▼
Alerts + Daily Reports
```

---

## Modules

| Module | Purpose |
|--------|---------|
| `webhooks.py` | Flask app; validates GitHub webhook signatures; queues push events |
| `scheduler.py` | APScheduler; hourly rebuild, daily deep scan, per-minute queue drain |
| `rate_limiter.py` | Thread-safe GitHub API quota tracker; adaptive backoff |
| `auto_merge_handler.py` | Detect + auto-merge Phase A PRs #1 and #2 on deployment |
| `propagation_handler.py` | Fan out changes to dependent repos; rollback on failure |
| `devops_orchestrator.py` | Execute build/test/deploy steps from `devops-automation.yaml` |
| `metrics_collector.py` | Track all metrics; generate daily reports; send alerts |

---

## Local Development

### Prerequisites

```bash
pip install -r requirements-dev.txt
```

### Run the webhook handler

```bash
export GITHUB_WEBHOOK_SECRET=dev-secret
python -m automation.webhooks
# → listening on http://0.0.0.0:5000
```

### Run via Docker Compose

```bash
cp .env.example .env       # fill in GITHUB_WEBHOOK_SECRET and GITHUB_TOKEN
docker compose -f deployment/docker-compose.yaml up --build
```

Services started:

| Service | URL |
|---------|-----|
| Webhooks | http://localhost:5000 |
| Redis | localhost:6379 |

### Run the tests

```bash
pytest tests/ -v
```

---

## Deploying to Kubernetes

```bash
# 1. Create the namespace and secrets
kubectl create namespace sociosphere-automation

kubectl create secret generic github-secrets \
  --from-literal=webhook-secret="$GITHUB_WEBHOOK_SECRET" \
  --from-literal=github-token="$GITHUB_TOKEN" \
  -n sociosphere-automation

# 2. Apply the manifest
kubectl apply -f deployment/kubernetes.yaml

# 3. Verify
kubectl get pods -n sociosphere-automation
kubectl logs -n sociosphere-automation -l app=webhooks
kubectl logs -n sociosphere-automation -l app=scheduler
```

The init container in the `webhooks` deployment automatically merges
Phase A PRs #1 and #2 before the webhook handler starts.

---

## Monitoring

### Health check

```
GET http://<host>:5000/health
→ {"status": "ok", "queue_depth": 0, ...}
```

### Metrics

```
GET http://<host>:5000/metrics
→ {
    "webhooks_received": 42,
    "webhooks_valid": 42,
    "webhooks_queued": 38,
    "rate_limiter": {
      "calls_this_hour": 120,
      "remaining_this_hour": 4380,
      "usage_pct": 2.7,
      ...
    }
  }
```

### Scheduler metrics (programmatic)

```python
from automation.scheduler import RegistryScheduler
# scheduler.get_metrics() returns counts of jobs run/failed/skipped
```

---

## Rate Limiting Strategy

| Band | Usage | Action |
|------|-------|--------|
| Normal | < 50 % | Full speed |
| Slow | 50–80 % | No change (within budget) |
| Backoff | 80–95 % | 10–500 ms delay per call; queue paused |
| Emergency | ≥ 95 % | All calls blocked; alert sent |
| Reset | — | Counters reset every 60 minutes |

---

## Failure Handling

| Failure | Detection | Response |
|---------|-----------|----------|
| Invalid webhook signature | 403 response | Log + increment counter |
| API quota exceeded | Rate limiter blocks | Wait for hourly reset |
| Merge conflict | `mergeable_state != clean` | Alert; skip |
| Build failure | Non-zero exit code | Retry × 3 (exponential backoff) |
| Deploy failure | Orchestrator returns False | Auto-rollback; log |
| Test failure | Orchestrator returns False | Skip prod deploy; rollback |
| Scheduler crash | Liveness probe fails | Kubernetes restarts pod |

---

## Debugging

```bash
# Tail webhook logs
kubectl logs -n sociosphere-automation -l app=webhooks -f

# Inspect the event queue depth
curl http://<host>:5000/health | python -m json.tool

# Run a single propagation dry-run locally
python - <<'EOF'
from automation.propagation_handler import PropagationHandler
from automation.devops_orchestrator import DevOpsOrchestrator

orch = DevOpsOrchestrator(dry_run=True)
handler = PropagationHandler(
    registry={"owner/repo": {"dependents": ["owner/dep"]}},
    devops_orchestrator=orch,
)
handler.handle({
    "repo": "owner/repo",
    "ref": "refs/heads/main",
    "payload": {"commits": [{"added": [], "modified": ["src/main.py"], "removed": []}]},
})
print(handler.get_metrics())
EOF
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `403` on all webhooks | Wrong `GITHUB_WEBHOOK_SECRET` | Match secret in GitHub repo settings |
| Queue depth keeps growing | Scheduler not running | Check scheduler pod logs |
| `emergency_stops > 0` in metrics | API quota blown | Reduce job frequency or wait for reset |
| Auto-merge not running | PR not in `clean` state | Resolve conflicts; re-run handler |
| Deploy fails repeatedly | Bad step in `devops-automation.yaml` | Fix the step command; check step logs |
