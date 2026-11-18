#!/usr/bin/env python3
"""Validate issue JSON against the workflow schemas. Stdlib only.

Supports the JSON Schema subset the schemas use: type (string or list),
enum, required, properties, additionalProperties: false, items, pattern.

Usage:
  validate_issue_json.py <schema.json> <file.json>...
  validate_issue_json.py --readme <issues/README.md>
      Validates the README examples: the first ```json block against
      issue-report.schema.json, the second against issue-response.schema.json.
Exit code 0 if everything is valid, 1 otherwise.
"""
import json
import re
import sys
from pathlib import Path

LEGACY_NAME = re.compile(r"^legacy[\w.-]*\.json$")

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"
TYPES = {
    "object": dict, "array": list, "string": str, "null": type(None),
    "boolean": bool, "integer": int, "number": (int, float),
}


def check(value, schema, path="$"):
    errors = []
    types = schema.get("type")
    if types is not None:
        types = [types] if isinstance(types, str) else types
        ok = any(isinstance(value, TYPES[t]) and not (t in ("integer", "number") and isinstance(value, bool))
                 for t in types)
        if not ok:
            return [f"{path}: expected {'|'.join(types)}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in {schema['enum']}")
    if isinstance(value, str) and "pattern" in schema and not re.search(schema["pattern"], value):
        errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required key {key!r}")
        for key, sub in value.items():
            if key in props:
                errors += check(sub, props[key], f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected key {key!r}")
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors += check(item, schema["items"], f"{path}[{i}]")
    return errors


def validate(schema_path, data, label):
    schema = json.loads(Path(schema_path).read_text())
    errors = check(data, schema)
    print(f"{'OK  ' if not errors else 'FAIL'} {label} against {Path(schema_path).name}")
    for e in errors:
        print(f"     {e}")
    return not errors


def main(argv):
    if len(argv) == 2 and argv[0] == "--readme":
        blocks = re.findall(r"```json\n(.*?)```", Path(argv[1]).read_text(), re.S)
        if len(blocks) != 2:
            print(f"FAIL expected 2 json blocks in {argv[1]}, found {len(blocks)}")
            return 1
        ok = validate(SCHEMA_DIR / "issue-report.schema.json", json.loads(blocks[0]), "README review example")
        ok &= validate(SCHEMA_DIR / "issue-response.schema.json", json.loads(blocks[1]), "README response example")
        return 0 if ok else 1
    if len(argv) < 2:
        print(__doc__)
        return 1
    ok = True
    for f in argv[1:]:
        try:
            data = json.loads(Path(f).read_text())
        except json.JSONDecodeError as e:
            print(f"FAIL {f}: invalid JSON: {e}")
            ok = False
            continue
        ok &= validate(argv[0], data, f)
        if not LEGACY_NAME.match(Path(f).name) and any(isinstance(i, dict) and "status" in i
                                                       for i in (data.get("issues") or [] if isinstance(data, dict) else [])):
            print(f"FAIL {f}: `status` is allowed only in legacy files (legacy*.json)")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
