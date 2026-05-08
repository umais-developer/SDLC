#!/usr/bin/env python3
"""
Verification script for Stage 1 (PRD): Goals & Requirements

Validates that the goals.json output conforms to the schema and contains
required structure and traceability.

Exit code: 0 = pass, 1 = fail
"""

import json
import sys
import jsonschema
from pathlib import Path

# Add parent directory to path so we can import exceptions
sys.path.insert(0, str(Path(__file__).parent))

from exceptions import StructureError, TraceabilityError, CompletionError


def load_schema(schema_path: str) -> dict:
    """Load JSON schema."""
    with open(schema_path) as f:
        return json.load(f)


def load_json(file_path: str) -> dict:
    """Load and parse JSON file."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StructureError("Stage 1", f"Invalid JSON in {file_path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 1", f"File not found: {file_path}")


def verify_schema(goals_json: dict, schema: dict) -> None:
    """Validate JSON against schema."""
    try:
        jsonschema.validate(goals_json, schema)
    except jsonschema.ValidationError as e:
        raise StructureError(
            "Stage 1",
            f"JSON schema validation failed: {e.message} at {'.'.join(str(p) for p in e.path)}"
        )


def verify_goal_structure(goals_json: dict) -> None:
    """Verify goals section is well-formed."""
    goals = goals_json.get("goals", [])
    
    if not goals:
        raise CompletionError("Stage 1", "At least one goal (GOAL-*) is required")
    
    for idx, goal in enumerate(goals):
        if not goal.get("success_criteria") or len(goal["success_criteria"]) == 0:
            raise CompletionError(
                "Stage 1",
                f"Goal {goal.get('id', f'[{idx}]')} has no success criteria"
            )


def verify_fr_structure(goals_json: dict) -> None:
    """Verify functional requirements section."""
    frs = goals_json.get("functional_requirements", [])
    
    if not frs:
        raise CompletionError("Stage 1", "At least one functional requirement (FR-*) is required")
    
    for idx, fr in enumerate(frs):
        if not fr.get("acceptance_criteria") or len(fr["acceptance_criteria"]) == 0:
            raise CompletionError(
                "Stage 1",
                f"FR {fr.get('id', f'[{idx}]')} has no acceptance criteria"
            )
        
        # Check that acceptance criteria are not vague
        vague_phrases = ["make it", "improve", "better", "faster", "easier"]
        for criterion in fr["acceptance_criteria"]:
            if criterion.lower().startswith(tuple(vague_phrases)):
                raise CompletionError(
                    "Stage 1",
                    f"FR {fr.get('id')}: acceptance criterion is too vague: '{criterion}'. "
                    "Use measurable criteria (e.g., 'Reduce load time from 5s to <1s')"
                )


def verify_priority_distribution(goals_json: dict) -> None:
    """Verify that P0 requirements are specified."""
    all_reqs = (
        goals_json.get("goals", []) +
        goals_json.get("functional_requirements", []) +
        goals_json.get("non_functional_requirements", [])
    )
    
    p0_count = sum(1 for r in all_reqs if r.get("priority") == "P0")
    
    if p0_count == 0:
        raise CompletionError("Stage 1", "At least one P0 (must-have) requirement is required")


def verify_testing_strategy(goals_json: dict) -> None:
    """Verify testing strategy is defined."""
    testing = goals_json.get("testing_strategy", {})
    
    if not testing:
        raise CompletionError("Stage 1", "testing_strategy section is missing")
    
    unit = testing.get("unit_tests", [])
    integration = testing.get("integration_tests", [])
    browser = testing.get("browser_tests", [])
    
    if not unit and not integration and not browser:
        raise CompletionError(
            "Stage 1",
            "At least one testing category (unit_tests, integration_tests, browser_tests) "
            "must have entries"
        )


def main(goals_json_path: str) -> None:
    """
    Main verification entry point.
    
    Args:
        goals_json_path: Path to the generated goals.json file
        
    Raises:
        StructureError, TraceabilityError, CompletionError on validation failure
    """
    
    # Load JSON and schema
    goals_json = load_json(goals_json_path)
    schema_path = Path(__file__).parent.parent / "schemas" / "goals.json"
    schema = load_schema(str(schema_path))
    
    # Run all verifications
    verify_schema(goals_json, schema)
    verify_goal_structure(goals_json)
    verify_fr_structure(goals_json)
    verify_priority_distribution(goals_json)
    verify_testing_strategy(goals_json)
    
    print("✅ Stage 1 verification PASSED")
    print(f"   • {len(goals_json.get('goals', []))} goal(s)")
    print(f"   • {len(goals_json.get('functional_requirements', []))} functional requirement(s)")
    print(f"   • {len(goals_json.get('non_functional_requirements', []))} non-functional requirement(s)")
    print(f"   • {len(goals_json.get('constraints', []))} constraint(s)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify/prd_structure.py <path-to-goals.json>")
        sys.exit(1)
    
    try:
        main(sys.argv[1])
        sys.exit(0)
    except (StructureError, TraceabilityError, CompletionError) as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
