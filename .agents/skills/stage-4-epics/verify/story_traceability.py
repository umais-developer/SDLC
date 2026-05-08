#!/usr/bin/env python3
"""
Verification script for Stage 4 (Epics/Stories): Story Traceability

Validates stories.json — every story has acceptance criteria, every FR in
goals.json is covered by at least one story, traceability matrix is complete.

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
        raise StructureError("Stage 4", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 4", f"File not found: {path}")


def verify_schema(data: dict, schema_path: str) -> None:
    if not HAS_JSONSCHEMA:
        return
    schema = load(schema_path)
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        raise StructureError("Stage 4", f"Schema validation failed: {e.message}")


def verify_stories_have_criteria(stories_json: dict) -> None:
    for story in stories_json.get("stories", []):
        criteria = story.get("acceptance_criteria", [])
        if not criteria:
            raise CompletionError(
                "Stage 4",
                f"Story {story['id']} '{story['title']}' has no acceptance criteria"
            )
        for i, criterion in enumerate(criteria):
            vague = ["work correctly", "function properly", "be better", "improve"]
            for v in vague:
                if v in criterion.lower():
                    raise CompletionError(
                        "Stage 4",
                        f"Story {story['id']} criterion {i+1} is too vague: '{criterion}'"
                    )


def verify_epic_story_references(stories_json: dict) -> None:
    story_ids = {s["id"] for s in stories_json.get("stories", [])}
    for epic in stories_json.get("epics", []):
        for story_ref in epic.get("stories", []):
            if story_ref not in story_ids:
                raise TraceabilityError(
                    "Stage 4",
                    f"Epic {epic['id']} references story '{story_ref}' which does not exist"
                )


def verify_traceability_matrix(stories_json: dict) -> None:
    story_ids = {s["id"] for s in stories_json.get("stories", [])}
    for entry in stories_json.get("traceability_matrix", []):
        for story_ref in entry.get("stories", []):
            if story_ref not in story_ids:
                raise TraceabilityError(
                    "Stage 4",
                    f"Traceability matrix references story '{story_ref}' which does not exist"
                )


def verify_fr_coverage(stories_json: dict, goals_json_path: str) -> None:
    """All P0 FRs must be covered by at least one story."""
    if not Path(goals_json_path).exists():
        print("⚠️  goals.json not found — skipping FR coverage check")
        return

    goals = load(goals_json_path)
    p0_frs = {
        fr["id"]
        for fr in goals.get("functional_requirements", [])
        if fr.get("priority") == "P0"
    }

    covered_frs = set()
    for story in stories_json.get("stories", []):
        for fr_id in story.get("links_to", {}).get("fr", []):
            covered_frs.add(fr_id)

    uncovered = p0_frs - covered_frs
    if uncovered:
        raise TraceabilityError(
            "Stage 4",
            f"P0 FRs not covered by any story: {sorted(uncovered)}"
        )


def main(stories_json_path: str, goals_json_path: str = None) -> None:
    data = load(stories_json_path)
    schema_path = Path(__file__).parent.parent / "schemas" / "stories.json"

    verify_schema(data, str(schema_path))
    verify_stories_have_criteria(data)
    verify_epic_story_references(data)
    verify_traceability_matrix(data)

    if goals_json_path:
        verify_fr_coverage(data, goals_json_path)

    print(f"✅ Stage 4 verification PASSED")
    print(f"   • {len(data.get('epics', []))} epic(s)")
    print(f"   • {len(data.get('stories', []))} story/stories")
    print(f"   • {len(data.get('traceability_matrix', []))} traceability entries")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify/story_traceability.py <stories.json> [goals.json]")
        sys.exit(1)
    try:
        goals_path = sys.argv[2] if len(sys.argv) > 2 else None
        main(sys.argv[1], goals_path)
        sys.exit(0)
    except (StructureError, TraceabilityError, CompletionError) as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
