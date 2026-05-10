"""
Centralized JSON Schema loading and validation for the SDLC pipeline.

Schemas live in `.agents/schemas/<name>.json` and are loaded by name.

Validation is a no-op (with a stderr warning) if `jsonschema` is not installed,
and a silent no-op if the named schema file does not exist. This lets the
pipeline run without optional dependencies; structural checks elsewhere in each
verify script will still catch real issues.
"""

import json
import sys
from pathlib import Path

SCHEMA_ROOT = Path(__file__).resolve().parent.parent.parent / "schemas"

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def load_schema(name: str) -> dict | None:
    """Load `<name>.json` from `.agents/schemas/`. Returns None if absent."""
    path = SCHEMA_ROOT / f"{name}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def validate(data: dict, schema_name: str, stage: str) -> None:
    """Validate `data` against the named schema. Raises StructureError on failure.

    Silently skips when `jsonschema` is not installed or the schema is not yet
    defined under `.agents/schemas/`.
    """
    if not HAS_JSONSCHEMA:
        print(
            f"[{stage}] jsonschema not installed — skipping schema validation for '{schema_name}'",
            file=sys.stderr,
        )
        return
    schema = load_schema(schema_name)
    if schema is None:
        return
    from exceptions import StructureError
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        path_str = ".".join(str(p) for p in e.path) if e.path else "<root>"
        raise StructureError(
            stage,
            f"Schema validation failed for '{schema_name}' at {path_str}: {e.message}",
        )
