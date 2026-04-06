# Integrated Backlog (sociosphere ↔ SourceOS ↔ socios)

## P0 Contracts
- [ ] M2 IPC spec + fixtures + conformance harness (sociosphere/standards/m2-ipc)
- [ ] Training loop schemas (sociosphere/standards/training-loop)
- [ ] Evidence/provenance envelope (sociosphere/standards/evidence)

## P1 Reference impl
- [ ] contract-runner + one adapter (socios)
- [ ] qes-runner executes runspec + records provenance (socios)

## P2 Training service
- [ ] training-api + worker + dataset registry + eval gating (socios)

## P3 SourceOS integration
- [ ] integration spec + bootstrap script + systemd units (SourceOS)

## Intent Audit Follow-ups
- [ ] Enforce 24h snapshot TTL check before each wave merge window.
- [ ] Add automation to mark `fips_triage.chain_validation.*.validated` based on live PR base checks.
- [ ] Add companion-pair merge gate for sociosphere#19 and socioprophet#257.
