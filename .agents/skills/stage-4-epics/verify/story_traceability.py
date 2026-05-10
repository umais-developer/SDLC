#!/usr/bin/env python3
"""
Verification script for Stage 4 (Epics/Stories): Story Traceability

Validates stories.json — stories have acceptance criteria, links resolve to
goals/flows/components, and (optionally) dependency graph and matrix checks.
Supports --trivial to validate epics_stories_final.md only.

Exit code: 0 = pass, 1 = fail
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "_shared"))
from console import setup as setup_console
setup_console()
from exceptions import StructureError, TraceabilityError, CompletionError
from schemas import validate as validate_schema


def load(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StructureError("Stage 4", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 4", f"File not found: {path}")


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
    """Validate every story reference in traceability_matrix exists in stories[].

    Accepts two shapes:
      (1) list of dicts: ``[{"stories": ["S-1", "S-2"]}, ...]``
      (2) FR-keyed dict: ``{"FR-1": ["S-1"], "FR-2": ["S-2", "S-3"], ...}``
    """
    story_ids = {s["id"] for s in stories_json.get("stories", [])}
    matrix = stories_json.get("traceability_matrix", [])

    story_refs: list[str] = []
    if isinstance(matrix, dict):
        for refs in matrix.values():
            if isinstance(refs, list):
                story_refs.extend(r for r in refs if isinstance(r, str))
    elif isinstance(matrix, list):
        for entry in matrix:
            if isinstance(entry, dict):
                story_refs.extend(
                    r for r in entry.get("stories", []) if isinstance(r, str)
                )
    else:
        raise StructureError(
            "Stage 4",
            f"traceability_matrix must be a list or dict, got {type(matrix).__name__}",
        )

    for story_ref in story_refs:
        if story_ref not in story_ids:
            raise TraceabilityError(
                "Stage 4",
                f"Traceability matrix references story '{story_ref}' which does not exist",
            )


def extract_goal_ids(goals: dict) -> set[str]:
    ids = set()
    ids.update({g.get("id") for g in goals.get("goals", []) if g.get("id")})
    ids.update({fr.get("id") for fr in goals.get("functional_requirements", []) if fr.get("id")})
    ids.update({nfr.get("id") for nfr in goals.get("non_functional_requirements", []) if nfr.get("id")})
    ids.update({c.get("id") for c in goals.get("constraints", []) if c.get("id")})
    return {i for i in ids if i}


def extract_flow_ids(flows: dict) -> set[str]:
    return {f.get("id") for f in flows.get("flows", []) if f.get("id")}


def map_fr_to_flows(flows: dict) -> dict[str, set[str]]:
    mapping: dict[str, set[str]] = {}
    for flow in flows.get("flows", []):
        flow_id = flow.get("id")
        if not flow_id:
            continue
        links = flow.get("links_to", [])
        if isinstance(links, str):
            links = [links]
        for link in links:
            if isinstance(link, str) and link.startswith("FR-"):
                mapping.setdefault(link, set()).add(flow_id)
    return mapping


def extract_component_names(components: dict) -> set[str]:
    return {c.get("name") for c in components.get("components", []) if c.get("name")}


def verify_story_links(stories_json: dict, goal_ids: set[str]) -> None:
    for story in stories_json.get("stories", []):
        links = story.get("links_to", {})
        if not isinstance(links, dict):
            raise StructureError("Stage 4", f"Story {story.get('id', '?')} links_to must be an object")
        all_links = []
        for key in ["fr", "nfr", "con", "goal"]:
            vals = links.get(key, [])
            if isinstance(vals, str):
                vals = [vals]
            if not isinstance(vals, list):
                raise StructureError("Stage 4", f"Story {story.get('id', '?')} links_to.{key} must be a list")
            all_links.extend(vals)
        if not all_links:
            raise TraceabilityError("Stage 4", f"Story {story.get('id', '?')} does not link to any FR/NFR/CON/GOAL")
        missing = [link for link in all_links if link not in goal_ids]
        if missing:
            raise TraceabilityError("Stage 4", f"Story {story.get('id', '?')} links_to contains unknown IDs: {missing}")


def verify_story_flow_links(stories_json: dict, fr_to_flows: dict[str, set[str]], flow_ids: set[str]) -> None:
    for story in stories_json.get("stories", []):
        links = story.get("links_to", {})
        fr_links = links.get("fr", []) if isinstance(links, dict) else []
        if isinstance(fr_links, str):
            fr_links = [fr_links]
        expected_flow_ids = set()
        for fr_id in fr_links:
            expected_flow_ids.update(fr_to_flows.get(fr_id, set()))

        flow_links = links.get("flow", []) if isinstance(links, dict) else []
        if isinstance(flow_links, str):
            flow_links = [flow_links]
        if expected_flow_ids and not flow_links:
            raise TraceabilityError("Stage 4", f"Story {story.get('id', '?')} must link to FLOW IDs for user-facing FRs")
        for flow_id in flow_links:
            if flow_id not in flow_ids:
                raise TraceabilityError("Stage 4", f"Story {story.get('id', '?')} links_to.flow contains unknown ID: {flow_id}")


def verify_story_components(stories_json: dict, component_names: set[str]) -> None:
    for story in stories_json.get("stories", []):
        components = story.get("components", [])
        if isinstance(components, str):
            components = [components]
        if not components:
            raise TraceabilityError("Stage 4", f"Story {story.get('id', '?')} must list at least one component")
        unknown = [c for c in components if c not in component_names]
        if unknown:
            raise TraceabilityError("Stage 4", f"Story {story.get('id', '?')} references unknown components: {unknown}")


def verify_dependencies_acyclic(stories_json: dict) -> None:
    story_ids = {s.get("id") for s in stories_json.get("stories", []) if s.get("id")}
    graph = {sid: set() for sid in story_ids}
    for story in stories_json.get("stories", []):
        sid = story.get("id")
        deps = story.get("depends_on", [])
        if isinstance(deps, str):
            deps = [deps]
        if not isinstance(deps, list):
            raise StructureError("Stage 4", f"Story {sid} depends_on must be a list")
        for dep in deps:
            if dep not in story_ids:
                raise TraceabilityError("Stage 4", f"Story {sid} depends_on references unknown story: {dep}")
            graph[sid].add(dep)

    visiting = set()
    visited = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise TraceabilityError("Stage 4", f"Dependency cycle detected at story {node}")
        if node in visited:
            return
        visiting.add(node)
        for dep in graph.get(node, set()):
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def verify_trivial(path: str) -> None:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise CompletionError("Stage 4", f"epics_stories_final.md not found at {path}")
    if len(text.strip()) < 50:
        raise CompletionError("Stage 4", "epics_stories_final.md is too short")
    if not re.search(r"\b(FR|NFR|CON|GOAL)-\d+\b", text):
        raise CompletionError("Stage 4", "epics_stories_final.md must cite at least one FR/NFR/CON/GOAL ID")


def verify_fr_coverage(stories_json: dict, goals_json_path: str, user_facing_frs: set[str] | None = None) -> None:
    """All P0 user-facing FRs must be covered by at least one story."""
    if not Path(goals_json_path).exists():
        print("⚠️  goals.json not found — skipping FR coverage check")
        return

    goals = load(goals_json_path)
    p0_frs = {
        fr["id"]
        for fr in goals.get("functional_requirements", [])
        if fr.get("priority") == "P0"
    }

    if user_facing_frs is not None:
        p0_frs = p0_frs.intersection(user_facing_frs)

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


def main() -> None:
    args = [a for a in sys.argv[1:]]
    trivial = "--trivial" in args
    require_deps = "--require-deps" in args
    require_matrix = "--require-matrix" in args
    args = [a for a in args if a not in ["--trivial", "--require-deps", "--require-matrix"]]

    if trivial:
        path = args[0] if args else ".agents/artifacts/stage-4/epics_stories_final.md"
        verify_trivial(path)
        print("✅ Stage 4 verification PASSED (Trivial — story note confirmed)")
        return

    if len(args) < 1:
        print("Usage: python verify/story_traceability.py <stories.json> [goals.json] [flows.json] [components.json]")
        sys.exit(1)

    stories_json_path = args[0]
    goals_json_path = args[1] if len(args) > 1 else None
    flows_json_path = args[2] if len(args) > 2 else None
    components_json_path = args[3] if len(args) > 3 else None

    data = load(stories_json_path)

    validate_schema(data, "stories", "Stage 4")
    verify_stories_have_criteria(data)
    verify_epic_story_references(data)

    if goals_json_path:
        goals = load(goals_json_path)
        goal_ids = extract_goal_ids(goals)
        verify_story_links(data, goal_ids)
    else:
        goals = {}
        goal_ids = set()

    if flows_json_path and Path(flows_json_path).exists():
        flows = load(flows_json_path)
        flow_ids = extract_flow_ids(flows)
        fr_to_flows = map_fr_to_flows(flows)
        user_facing_frs = set(fr_to_flows.keys())
        verify_story_flow_links(data, fr_to_flows, flow_ids)
        if goals_json_path:
            verify_fr_coverage(data, goals_json_path, user_facing_frs)
    elif goals_json_path:
        verify_fr_coverage(data, goals_json_path)

    if components_json_path and Path(components_json_path).exists():
        components = load(components_json_path)
        component_names = extract_component_names(components)
        if component_names:
            verify_story_components(data, component_names)

    if require_deps:
        verify_dependencies_acyclic(data)

    matrix = data.get("traceability_matrix", [])
    if require_matrix and not matrix:
        raise CompletionError("Stage 4", "Traceability matrix is required for Large requests")
    if matrix:
        verify_traceability_matrix(data)

    print(f"✅ Stage 4 verification PASSED")
    print(f"   • {len(data.get('epics', []))} epic(s)")
    print(f"   • {len(data.get('stories', []))} story/stories")
    print(f"   • {len(data.get('traceability_matrix', []))} traceability entries")


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except (StructureError, TraceabilityError, CompletionError) as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
