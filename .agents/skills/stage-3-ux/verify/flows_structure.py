#!/usr/bin/env python3
"""
Verification script for Stage 3 (UX): User Flow Structure

Validates flows.json — user-facing P0 FRs are covered, flows have steps and
links_to IDs that resolve to goals.json, and states are defined. Supports
--trivial to validate ux_final.md only.

Exit code: 0 = pass, 1 = fail
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "_shared"))
from exceptions import StructureError, TraceabilityError, CompletionError
from schemas import validate as validate_schema


def load(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StructureError("Stage 3", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 3", f"File not found: {path}")


def verify_flows_completeness(flows_json: dict, accessibility_required: bool) -> None:
    flows = flows_json.get("flows", [])
    if not flows:
        raise CompletionError("Stage 3", "At least one user flow is required")

    for flow in flows:
        fid = flow.get("id", "?")
        if not flow.get("steps") or len(flow["steps"]) == 0:
            raise CompletionError("Stage 3", f"Flow {fid} has no steps")
        if not flow.get("links_to"):
            raise TraceabilityError("Stage 3", f"Flow {fid} does not link to any FR/goal")
        if accessibility_required and not flow.get("keyboard_path"):
            raise CompletionError("Stage 3", f"Flow {fid} is missing 'keyboard_path' (accessibility requirement)")


def verify_states_defined(flows_json: dict) -> None:
    states = flows_json.get("states", [])
    if not states:
        raise CompletionError("Stage 3", "At least one UI state must be defined in 'states[]'")
    for state in states:
        if not state.get("name") or not state.get("ui_condition"):
            raise StructureError("Stage 3", f"State '{state.get('name', '?')}' missing 'ui_condition'")


def extract_goal_ids(goals: dict) -> set[str]:
    ids = set()
    ids.update({g.get("id") for g in goals.get("goals", []) if g.get("id")})
    ids.update({fr.get("id") for fr in goals.get("functional_requirements", []) if fr.get("id")})
    ids.update({nfr.get("id") for nfr in goals.get("non_functional_requirements", []) if nfr.get("id")})
    ids.update({c.get("id") for c in goals.get("constraints", []) if c.get("id")})
    return {i for i in ids if i}


def is_accessibility_required(goals: dict) -> bool:
    keywords = re.compile(r"\b(accessibility|wcag|keyboard|aria|screen reader)\b", re.IGNORECASE)
    for nfr in goals.get("non_functional_requirements", []):
        text = " ".join([str(nfr.get("title", "")), str(nfr.get("description", ""))])
        if keywords.search(text):
            return True
    return False


def verify_links_resolve(flows_json: dict, goal_ids: set[str]) -> None:
    for flow in flows_json.get("flows", []):
        fid = flow.get("id", "?")
        links = flow.get("links_to", [])
        if isinstance(links, str):
            links = [links]
        if not isinstance(links, list):
            raise StructureError("Stage 3", f"Flow {fid} links_to must be a list of IDs")
        missing = [link for link in links if link not in goal_ids]
        if missing:
            raise TraceabilityError("Stage 3", f"Flow {fid} links_to contains unknown IDs: {missing}")


def verify_fr_coverage(flows_json: dict, goals_path: str) -> None:
    """Every P0 FR in goals.json must be referenced in at least one flow."""
    if not Path(goals_path).exists():
        print(f"⚠️  goals.json not found at {goals_path} — skipping FR coverage check")
        return

    goals = load(goals_path)
    p0_frs = {
        fr["id"] for fr in goals.get("functional_requirements", [])
        if fr.get("priority") == "P0" and fr.get("user_facing", True)
    }

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


def verify_trivial(ux_path: str) -> None:
    try:
        text = Path(ux_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise CompletionError("Stage 3", f"ux_final.md not found at {ux_path}")

    if len(text.strip()) < 50:
        raise CompletionError("Stage 3", "ux_final.md is too short for a Trivial flow note")
    if not re.search(r"\b(FR|NFR|CON|GOAL)-\d+\b", text):
        raise CompletionError("Stage 3", "ux_final.md must cite at least one FR/NFR/CON/GOAL ID")
    if not re.search(r"\b(click|type|tap|press|select|navigate|view|focus)\b", text, re.IGNORECASE):
        raise CompletionError("Stage 3", "ux_final.md must mention at least one user action (click/type/tap/etc.)")
    if not re.search(r"\b(shows|displays|filters|clears|updates|restores|renders)\b", text, re.IGNORECASE):
        raise CompletionError("Stage 3", "ux_final.md must mention at least one system response (shows/filters/updates/etc.)")


def main() -> int:
    args = [a for a in sys.argv[1:]]
    trivial = False
    if "--trivial" in args:
        trivial = True
        args.remove("--trivial")

    if trivial:
        ux_path = args[0] if len(args) > 0 else ".agents/artifacts/stage-3/ux_final.md"
        try:
            verify_trivial(ux_path)
            print("✅ Stage 3 verification PASSED (Trivial — flow note confirmed)")
            return 0
        except (StructureError, TraceabilityError, CompletionError) as e:
            print(f"❌ {e}")
            return 1

    if len(args) < 1:
        print("Usage: python flows_structure.py <flows.json> [goals.json]")
        return 1

    flows_path = args[0]
    goals_path = args[1] if len(args) > 1 else ".agents/artifacts/stage-1/goals.json"

    try:
        flows_json = load(flows_path)
        goals = load(goals_path) if Path(goals_path).exists() else {}
        accessibility_required = is_accessibility_required(goals)
        goal_ids = extract_goal_ids(goals) if goals else set()
        validate_schema(flows_json, "flows", "Stage 3")
        verify_flows_completeness(flows_json, accessibility_required)
        verify_states_defined(flows_json)
        if goal_ids:
            verify_links_resolve(flows_json, goal_ids)
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
