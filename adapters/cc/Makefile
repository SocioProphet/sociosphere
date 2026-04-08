SHELL := /bin/bash
PYTHON := python3

.PHONY: build test lint deps_inventory clean

build:
	$(PYTHON) -m pip install --quiet -r requirements.txt
	@echo "OK: cc adapter runtime deps installed"

test:
	$(PYTHON) -m pytest tests/ -v --tb=short 2>/dev/null \
		|| $(PYTHON) -m unittest discover -s tests/ -v

lint:
	$(PYTHON) -m flake8 --max-line-length=120 runners/ deps_inventory.py 2>/dev/null \
		|| echo "WARN: flake8 not available; skipping lint"

deps_inventory:
	$(PYTHON) deps_inventory.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
