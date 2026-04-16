from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
import json
from typing import Any


class ValidationError(Exception):
    pass


def _py_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _normalize(value: Any) -> Any:
    if is_dataclass(value):
        return asdict(value)
    return value


def load_schema(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    instance = _normalize(instance)
    errors: list[str] = []

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")
        return errors

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}, got {instance!r}")

    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        allowed = schema_type
    elif isinstance(schema_type, str):
        allowed = [schema_type]
    else:
        allowed = []

    if allowed:
        actual = _py_type_name(instance)
        if actual not in allowed:
            errors.append(f"{path}: expected type {allowed!r}, got {actual!r}")
            return errors

    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required key {key!r}")
        properties = schema.get("properties", {})
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(validate_instance(instance[key], subschema, f"{path}.{key}"))
        if schema.get("additionalProperties") is False:
            for key in instance.keys():
                if key not in properties:
                    errors.append(f"{path}: unexpected key {key!r}")

    elif isinstance(instance, list):
        item_schema = schema.get("items")
        if item_schema:
            for idx, item in enumerate(instance):
                errors.extend(validate_instance(item, item_schema, f"{path}[{idx}]"))

    return errors


def validate_file(instance_path: str | Path, schema_path: str | Path) -> list[str]:
    instance = json.loads(Path(instance_path).read_text(encoding="utf-8"))
    schema = load_schema(schema_path)
    return validate_instance(instance, schema)
