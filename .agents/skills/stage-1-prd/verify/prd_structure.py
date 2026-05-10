#!/usr/bin/env python3
"""
Verification script for Stage 1 (PRD): Problem Statement + Goals & Requirements

Validates that both problem.json and goals.json conform to their schemas and
contain the required structure, traceability, and completeness.

Exit code: 0 = pass, 1 = fail
"""

import json
import sys
from pathlib import Path

# Import shared exception classes and schema helper from _shared/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "_shared"))

from console import setup as setup_console
setup_console()
from exceptions import StructureError, TraceabilityError, CompletionError
from schemas import validate as validate_schema


def load_json(file_path: str) -> dict:
    """Load and parse JSON file."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StructureError("Stage 1", f"Invalid JSON in {file_path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 1", f"File not found: {file_path}")


def verify_problem_structure(problem_json: dict) -> None:
    """Verify problem statement is sufficiently complete."""
    primary_goal = problem_json.get("primary_goal", "")
    if len(primary_goal.strip()) < 10:
        raise CompletionError("Stage 1", "primary_goal is too short — must be a clear 1-2 sentence statement")

    in_scope = problem_json.get("scope_boundaries", {}).get("in_scope", [])
    if not in_scope:
        raise CompletionError("Stage 1", "scope_boundaries.in_scope must have at least one entry")

    affected = problem_json.get("affected_areas", [])
    if not affected:
        raise CompletionError("Stage 1", "affected_areas must have at least one entry")

    ambiguities = problem_json.get("ambiguities", [])
    ambiguous_scope = problem_json.get("scope_boundaries", {}).get("ambiguous", [])
    if not ambiguities and not ambiguous_scope:
        raise CompletionError(
            "Stage 1",
            "ambiguities array is empty — document at least one assumption or default applied"
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


def verify_nfr_measurability(goals_json: dict) -> None:
    """
    Verify that every NFR acceptance criterion contains at least one measurable
    threshold — a concrete number, unit, or comparative phrase.
    Hand-wavy criteria like 'feels instant' or 'noticeably fast' are rejected.
    """
    import re
    nfrs = goals_json.get("non_functional_requirements", [])
    MEASURABLE_PATTERN = re.compile(
        r"""
        \d+            # bare number
        | <\s*\d+      # < N
        | >\s*\d+      # > N
        | \d+\s*ms\b   # Nms
        | \d+\s*s\b    # Ns
        | \d+\s*%\b    # N%
        | \d+\s*fps\b  # Nfps
        | WCAG         # accessibility standard name counts
        | ARIA         # ARIA standard name counts
        """,
        re.VERBOSE | re.IGNORECASE,
    )
    for nfr in nfrs:
        criteria = nfr.get("acceptance_criteria", [])
        if not criteria:
            continue  # handled by FR structure check
        all_vague = all(not MEASURABLE_PATTERN.search(c) for c in criteria)
        if all_vague:
            raise CompletionError(
                "Stage 1",
                f"NFR {nfr.get('id')}: all acceptance criteria are vague — at least one must "
                "contain a concrete threshold (a number, unit, standard name, or comparative value). "
                f"Current criteria: {criteria}"
            )


def verify_volume_figures_justified(goals_json: dict) -> None:
    """
    Verify that any bare round-number capacity figure cited in an NFR description
    (e.g. '100 replays', '1000 users') is accompanied by a rationale field or
    documented in the constraints/ambiguities sections.

    This catches 'should handle 100 saved replays' appearing with no explanation
    of where '100' came from.
    """
    import re
    ROUND_NUMBER_RE = re.compile(
        r'\b(\d{2,})\s+(?:replays?|entries|items?|records?|users?|requests?|rows?)\b',
        re.IGNORECASE,
    )
    constraints = goals_json.get("constraints", [])
    ambiguities_text = " ".join(
        str(a) for a in goals_json.get("ambiguities", [])
    )
    constraint_text = " ".join(c.get("description", "") + c.get("rationale", "") for c in constraints)
    context_text = ambiguities_text + " " + constraint_text

    nfrs = goals_json.get("non_functional_requirements", [])
    for nfr in nfrs:
        description = nfr.get("description", "")
        for match in ROUND_NUMBER_RE.finditer(description):
            figure = match.group(0)
            # Accept if the same figure appears in constraints or ambiguities (justified)
            if not re.search(re.escape(match.group(1)), context_text):
                raise CompletionError(
                    "Stage 1",
                    f"NFR {nfr.get('id')}: capacity figure '{figure}' appears without justification. "
                    "Document where this number comes from in constraints[] or the problem's ambiguities[]. "
                    "Example: 'Based on localStorage ceiling of ~5 MB, estimated 100 replays at ~50 KB each.'"
                )


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

    Derives problem.json path from the same directory as goals.json.

    Args:
        goals_json_path: Path to the generated goals.json file

    Raises:
        StructureError, TraceabilityError, CompletionError on validation failure
    """
    goals_path = Path(goals_json_path)
    problem_json_path = goals_path.parent / "problem.json"

    # --- Step 1a: Validate problem.json ---
    problem_json = load_json(str(problem_json_path))
    validate_schema(problem_json, "problem", "Stage 1")
    verify_problem_structure(problem_json)
    print("✅ problem.json validation PASSED")
    print(f"   • request_type: {problem_json.get('request_type')}")
    print(f"   • {len(problem_json.get('scope_boundaries', {}).get('in_scope', []))} in-scope item(s)")
    print(f"   • {len(problem_json.get('ambiguities', []))} assumption(s) documented")

    # --- Step 1b: Validate goals.json ---
    goals_json = load_json(goals_json_path)
    validate_schema(goals_json, "goals", "Stage 1")
    verify_goal_structure(goals_json)
    verify_fr_structure(goals_json)
    verify_priority_distribution(goals_json)
    verify_nfr_measurability(goals_json)
    verify_volume_figures_justified(goals_json)
    verify_testing_strategy(goals_json)
    print("✅ goals.json validation PASSED")
    print(f"   • {len(goals_json.get('goals', []))} goal(s)")
    print(f"   • {len(goals_json.get('functional_requirements', []))} functional requirement(s)")
    print(f"   • {len(goals_json.get('non_functional_requirements', []))} non-functional requirement(s)")
    print(f"   • {len(goals_json.get('constraints', []))} constraint(s)")

    print("\n✅ Stage 1 verification PASSED")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify/prd_structure.py <path-to-goals.json>")
        print("       (problem.json is expected in the same directory as goals.json)")
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
