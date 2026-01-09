SHELL := /bin/bash

UI_DIR := apps/ui-workbench

.PHONY: ui-dev ui-build ui-check ui-install

# (removed) @echo "OK: ui build passed"
# --- ui-workbench targets ---
UI_DIR := apps/ui-workbench

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
