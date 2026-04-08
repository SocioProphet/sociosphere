SHELL := /bin/bash

UI_DIR := apps/ui-workbench

# --- ui-workbench targets ---

.PHONY: ui-preflight ui-install ui-build ui-check ui-dev

ui-preflight:
	./tools/ui-preflight.sh

ui-install:
	cd $(UI_DIR) && npm install && npm install -D vue-tsc typescript

ui-build:
	cd $(UI_DIR) && npm run build

ui-check: ui-preflight ui-build
	@echo "OK: ui-check passed"

ui-dev: ui-preflight
	cd $(UI_DIR) && npm run dev
# --- end ui-workbench targets ---
# --- standards validation targets ---
.PHONY: validate validate-standards

validate: validate-standards
	@echo "OK: validate"

validate-standards:
	@ok=1; if [ -f tools/validate_adaptation_program.py ]; then python3 tools/validate_adaptation_program.py standards/examples/adaptation/program.example.v1.json || ok=0; else echo "ERR: tools/validate_adaptation_program.py missing"; ok=0; fi; if [ -f standards/qes/tools/validate_qes_contracts.py ]; then python3 standards/qes/tools/validate_qes_contracts.py || ok=0; else echo "WARN: standards/qes/tools/validate_qes_contracts.py missing (skipping)"; fi; test $$ok -eq 1

# --- registry targets ---
.PHONY: registry-validate ontology-validate dep-cycles

registry-validate:
	@echo "==> Validating registry ontology roles and layers..."
	python3 engines/ontology_engine.py validate
	@echo "==> Checking dependency graph for cycles..."
	python3 engines/propagation_engine.py cycles
	@echo "OK: registry-validate passed"

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

# --- merge order ---
.PHONY: merge-order

merge-order:
	python3 engines/propagation_engine.py merge-order

# --- full workspace check (run in CI) ---
.PHONY: workspace-check

workspace-check: validate registry-validate compliance-check
	@echo "OK: workspace-check passed"

