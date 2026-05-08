#!/usr/bin/env python3
"""
Verification script for Stage 3 (UX): User Flow Structure

Validates flows.json — every FR from goals.json has at least one flow,
every flow has steps and error_paths, states are defined.

Exit code: 0 = pass, 1 = fail
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exceptions import StructureError, TraceabilityError, CompletionError

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def load(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StructureError("Stage 3", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 3", f"File not found: {path}")


def verify_schema(data: dict, schema_path: str) -> None:
    if not HAS_JSONSCHEMA:
        print("⚠️  jsonschema not installed — skipping schema validation")
        return
    schema = load(schema_path)
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        raise StructureError("Stage 3", f"Schema validation failed: {e.message}")


def verify_flows_completeness(flows_json: dict) -> None:
    flows = flows_json.get("flows", [])
    if not flows:
        raise CompletionError("Stage 3", "At least one user flow is required")

    for flow in flows:
        fid = flow.get("id", "?")
        if not flow.get("steps") or len(flow["steps"]) == 0:
            raise CompletionError("Stage 3", f"Flow {fid} has no steps")
        if "error_paths" not in flow:
            raise CompletionError("Stage 3", f"Flow {fid} is missing 'error_paths' (may be empty list)")
        if not flow.get("links_to"):
            raise TraceabilityError("Stage 3", f"Flow {fid} does not link to any FR/goal")
        if not flow.get("keyboard_path"):
            raise CompletionError("Stage 3", f"Flow {fid} is missing 'keyboard_path' (accessibility requirement)")


def verify_states_defined(flows_json: dict) -> None:
    states = flows_json.get("states", [])
    if not states:
        raise CompletionError("Stage 3", "At least one UI state must be defined in 'states[]'")
    for state in states:
        if not state.get("name") or not state.get("ui_condition"):
            raise StructureError("Stage 3", f"State '{state.get('name', '?')}' missing 'ui_condition'")


def verify_fr_coverage(flows_json: dict, goals_path: str) -> None:
    """Every P0 FR in goals.json must be referenced in at least one flow."""
    if not Path(goals_path).exists():
        print(f"⚠️  goals.json not found at {goals_path} — skipping FR coverage check")
        return

    goals = load(goals_path)
    p0_frs = {fr["id"] for fr in goals.get("functional_requirements", []) if fr.get("priority") == "P0"}

    all_links = set()
    for flow in flows_json.get("flows", []):
        links = flow.get("links_to", [])
        if isinstance(links, list):
            all_links.update(links)
        elif isinstance(links, str):
            all_links.add(links)

    uncovered = p0_frs - all_links
    if uncovered:
        raise TraceabilityError(
            "Stage 3",
            f"P0 functional requirements not covered by any flow: {sorted(uncovered)}"
        )


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python flows_structure.py <flows.json> [goals.json]")
        return 1

    flows_path = sys.argv[1]
    goals_path = sys.argv[2] if len(sys.argv) > 2 else ".agents/artifacts/stage-1/goals.json"
    schema_path = Path(__file__).parent.parent / "schemas" / "flows.json"

    try:
        flows_json = load(flows_path)
        if schema_path.exists():
            verify_schema(flows_json, str(schema_path))
        verify_flows_completeness(flows_json)
        verify_states_defined(flows_json)
        verify_fr_coverage(flows_json, goals_path)

        print(f"✅ Stage 3 verification passed: {len(flows_json.get('flows', []))} flows, "
              f"{len(flows_json.get('states', []))} states")
        return 0

    except (StructureError, TraceabilityError, CompletionError) as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
