SHELL := /bin/bash

UI_DIR := apps/ui-workbench

# --- ui-workbench targets ---

.PHONY: ui-preflight ui-install ui-build ui-check ui-dev

ui-preflight:
	./tools/ui-preflight.sh

ui-install:
	cd $(UI_DIR) && npm ci

ui-build:
	cd $(UI_DIR) && npm run build

ui-check: ui-preflight ui-build
	@echo "OK: ui-check passed"

ui-dev: ui-preflight
	cd $(UI_DIR) && npm run dev
# --- end ui-workbench targets ---

# --- standards validation targets ---
.PHONY: validate validate-standards multidomain-geospatial-standards-compliance-validate program-dashboard-validate model-fabric-work-register-validate

validate: validate-standards program-dashboard-validate model-fabric-work-register-validate
	@echo "OK: validate"

validate-standards:
	@ok=1; if [ -f tools/validate_adaptation_program.py ]; then python3 tools/validate_adaptation_program.py standards/examples/adaptation/program.example.v1.json || ok=0; else echo "ERR: tools/validate_adaptation_program.py missing"; ok=0; fi; if [ -f standards/qes/tools/validate_qes_contracts.py ]; then python3 standards/qes/tools/validate_qes_contracts.py || ok=0; else echo "WARN: standards/qes/tools/validate_qes_contracts.py missing (skipping)"; fi; if [ -f tools/check_multidomain_geospatial_standards_compliance.py ]; then python3 tools/check_multidomain_geospatial_standards_compliance.py || ok=0; else echo "ERR: tools/check_multidomain_geospatial_standards_compliance.py missing"; ok=0; fi; test $$ok -eq 1

program-dashboard-validate:
	python3 tools/validate_program_dashboard.py

model-fabric-work-register-validate:
	python3 tools/validate_model_fabric_work_register.py

multidomain-geospatial-standards-compliance-validate:
	python3 tools/check_multidomain_geospatial_standards_compliance.py

# --- registry targets ---
.PHONY: registry-validate ontology-validate dep-cycles mirror-drift-check build-intelligence-validate deployment-topology-validate contract-lock-validate

mirror-drift-check:
	python3 engines/mirror_drift_engine.py check

registry-validate:
	@echo "==> Validating registry ontology roles and layers..."
	python3 engines/ontology_engine.py validate
	@echo "==> Checking dependency graph for cycles..."
	python3 engines/propagation_engine.py cycles
	@echo "==> Validating mirror drift status..."
	python3 engines/mirror_drift_engine.py check
	@echo "OK: registry-validate passed"

build-intelligence-validate:
	python3 tools/validate_build_intelligence.py

deployment-topology-validate:
	python3 tools/validate_deployment_topology.py

contract-lock-validate:
	python3 tools/validate_contract_locks.py

ontology-validate: registry-validate

dep-cycles:
	python3 engines/propagation_engine.py cycles

# --- status targets ---
.PHONY: status status-report

status:
	python3 engines/status_reporter.py dashboard

status-report:
	python3 engines/status_reporter.py report --format json

# --- compliance targets ---
.PHONY: compliance-check compliance-summary

compliance-check:
	@echo "==> Running compliance checks..."
	python3 telemetry/compliance_checker.py check
	@echo "OK: compliance-check complete"

compliance-summary:
	python3 telemetry/compliance_checker.py summary --format json

# --- source exposure governance targets ---
.PHONY: source-exposure-check

source-exposure-check:
	@echo "==> Running source exposure publication safety check..."
	python3 tools/check_source_exposure.py
	@echo "OK: source-exposure-check passed"

# --- merge order ---
.PHONY: merge-order

merge-order:
	python3 engines/propagation_engine.py merge-order

# --- workspace runner targets ---
.PHONY: workspace-list lock-verify lock-update inventory topology-check proof-slice-smoke

workspace-list:
	python3 tools/runner/runner.py list

lock-verify:
	python3 tools/runner/runner.py lock-verify

lock-update:
	python3 tools/runner/runner.py lock-update

inventory:
	python3 tools/runner/runner.py inventory

topology-check:
	python3 tools/check_topology.py

proof-slice-smoke:
	python3 tools/runner/proof_slice_smoke.py

# --- hygiene targets ---
.PHONY: hygiene-check

hygiene-check:
	@echo "==> Running repository hygiene checks..."
	bash tools/check_hygiene.sh
	@echo "OK: hygiene-check passed"


# --- full workspace check (run in CI) ---
.PHONY: workspace-check

workspace-check: validate registry-validate build-intelligence-validate deployment-topology-validate contract-lock-validate compliance-check source-exposure-check lock-verify topology-check hygiene-check
	@echo "OK: workspace-check passed"
