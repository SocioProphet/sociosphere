#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validate_registry_schema(registry: Any, schema: Any) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(registry), key=lambda e: list(e.absolute_path))
    rendered: list[str] = []
    for err in errors:
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        rendered.append(f"schema error at {path}: {err.message}")
    return rendered


def validate_plane_ids(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for plane in registry.get("planes", []):
        pid = plane.get("id")
        if pid in seen:
            errors.append(f"duplicate plane id in registry: {pid}")
        else:
            seen.add(pid)
    return errors


def validate_matrix(registry: dict[str, Any], matrix_rows: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    registry_ids = {plane.get("id") for plane in registry.get("planes", []) if plane.get("id")}
    matrix_ids = {row.get("plane_id", "").strip() for row in matrix_rows if row.get("plane_id", "").strip()}

    missing_in_matrix = sorted(registry_ids - matrix_ids)
    extra_in_matrix = sorted(matrix_ids - registry_ids)

    if missing_in_matrix:
        errors.append("registry plane ids missing from matrix: " + ", ".join(missing_in_matrix))
    if extra_in_matrix:
        errors.append("matrix plane ids missing from registry: " + ", ".join(extra_in_matrix))

    required_columns = {
        "plane_id",
        "plane_name",
        "canonical_question",
        "canonical_repo",
        "owner_role",
        "release_source_of_truth",
        "primary_gate",
        "leading_metrics",
        "main_risks",
        "next_two_steps",
    }
    if matrix_rows:
        header = set(matrix_rows[0].keys())
        missing_columns = sorted(required_columns - header)
        if missing_columns:
            errors.append("matrix missing required columns: " + ", ".join(missing_columns))
    else:
        errors.append("ownership matrix has no rows")

    registry_name_by_id = {
        plane.get("id"): plane.get("name")
        for plane in registry.get("planes", [])
        if plane.get("id")
    }
    for row in matrix_rows:
        pid = row.get("plane_id", "").strip()
        if not pid or pid not in registry_name_by_id:
            continue
        matrix_name = row.get("plane_name", "").strip()
        registry_name = str(registry_name_by_id[pid]).strip()
        if matrix_name and matrix_name != registry_name:
            warnings.append(
                f"plane name mismatch for {pid}: matrix={matrix_name!r} registry={registry_name!r}"
            )

    return errors, warnings


def build_reports(errors: list[str], warnings: list[str], registry: dict[str, Any], matrix_rows: list[dict[str, str]]) -> tuple[str, dict[str, Any]]:
    result = "pass" if not errors else "fail"
    plane_count = len(registry.get("planes", []))
    matrix_count = len(matrix_rows)

    md_lines = [
        "# Decision Planes Validation Report",
        "",
        f"- Result: **{result.upper()}**",
        f"- Registry planes: **{plane_count}**",
        f"- Matrix rows: **{matrix_count}**",
        f"- Errors: **{len(errors)}**",
        f"- Warnings: **{len(warnings)}**",
        "",
    ]
    if errors:
        md_lines.append("## Errors")
        md_lines.append("")
        md_lines.extend(f"- {err}" for err in errors)
        md_lines.append("")
    if warnings:
        md_lines.append("## Warnings")
        md_lines.append("")
        md_lines.extend(f"- {warn}" for warn in warnings)
        md_lines.append("")
    if not errors and not warnings:
        md_lines.append("No validation issues detected.")
        md_lines.append("")

    json_report = {
        "result": result,
        "registry_plane_count": plane_count,
        "matrix_row_count": matrix_count,
        "errors": errors,
        "warnings": warnings,
    }
    return "\n".join(md_lines), json_report


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate decision planes registry and ownership matrix.")
    p.add_argument("--registry", required=True)
    p.add_argument("--schema", required=True)
    p.add_argument("--matrix", required=True)
    p.add_argument("--report-md", required=True)
    p.add_argument("--report-json", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    registry_path = Path(args.registry)
    schema_path = Path(args.schema)
    matrix_path = Path(args.matrix)
    report_md_path = Path(args.report_md)
    report_json_path = Path(args.report_json)

    errors: list[str] = []
    warnings: list[str] = []

    registry = load_yaml(registry_path)
    schema = load_json(schema_path)
    matrix_rows = load_csv_rows(matrix_path)

    errors.extend(validate_registry_schema(registry, schema))
    errors.extend(validate_plane_ids(registry))
    matrix_errors, matrix_warnings = validate_matrix(registry, matrix_rows)
    errors.extend(matrix_errors)
    warnings.extend(matrix_warnings)

    report_md, report_json = build_reports(errors, warnings, registry, matrix_rows)
    report_md_path.parent.mkdir(parents=True, exist_ok=True)
    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    report_md_path.write_text(report_md + "\n", encoding="utf-8")
    report_json_path.write_text(json.dumps(report_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if errors:
        print(report_md)
        return 1
    print(report_md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
