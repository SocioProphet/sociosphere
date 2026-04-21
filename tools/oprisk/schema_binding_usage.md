# Canonical Schema Binding Checks

This note explains how to verify that the software operational-risk registry lane is pointing at the intended canonical schema artifacts.

## Purpose

The lightweight validation lane now has two layers:

1. local shape validation of normalized JSONL outputs;
2. local binding checks against the canonical schema and example paths declared in `SourceOS-Linux/sourceos-spec`.

## Usage

```bash
python tools/oprisk/check_schema_bindings.py \
  --contracts-root /path/to/sourceos-spec
```

To check a single target:

```bash
python tools/oprisk/check_schema_bindings.py \
  --contracts-root /path/to/sourceos-spec \
  --target outage_corpus
```

## What this does

It verifies that each declared schema target in `schema_registry.py` resolves to:

- a canonical schema file;
- and a corresponding example payload

inside a local checkout of `SourceOS-Linux/sourceos-spec`.

## What this does not do

This helper does **not** perform full JSON Schema validation of registry outputs.
That remains a follow-on step once schema loading is bound directly into the validation path.
