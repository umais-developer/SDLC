#!/usr/bin/env python3
"""
Verification script for Stage 5 (Implementation Plan): Tasks Structure

Validates tasks.json — tasks have file/test/DoD fields, links resolve to
goals/components/stories, and dependency graph is acyclic. Supports --trivial.

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
        raise StructureError("Stage 5", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 5", f"File not found: {path}")


def verify_tasks_completeness(tasks_json: dict) -> None:
    tasks = tasks_json.get("tasks", [])
    if not tasks:
        raise CompletionError("Stage 5", "At least one task is required")

    for task in tasks:
        tid = task.get("id", "?")
        if not task.get("file"):
            raise CompletionError("Stage 5", f"Task {tid} has no 'file' specified")
        if not task.get("tests"):
            raise CompletionError("Stage 5", f"Task {tid} has no 'tests' specified")
        if not task.get("definition_of_done"):
            raise CompletionError("Stage 5", f"Task {tid} has no 'definition_of_done'")


def extract_goal_ids(goals: dict) -> set[str]:
    ids = set()
    ids.update({g.get("id") for g in goals.get("goals", []) if g.get("id")})
    ids.update({fr.get("id") for fr in goals.get("functional_requirements", []) if fr.get("id")})
    ids.update({nfr.get("id") for nfr in goals.get("non_functional_requirements", []) if nfr.get("id")})
    ids.update({c.get("id") for c in goals.get("constraints", []) if c.get("id")})
    return {i for i in ids if i}


def extract_story_ids(stories: dict) -> set[str]:
    return {s.get("id") for s in stories.get("stories", []) if s.get("id")}


def extract_component_files(components: dict) -> set[str]:
    return {c.get("file") for c in components.get("components", []) if c.get("file")}


def extract_component_names(components: dict) -> set[str]:
    return {c.get("name") for c in components.get("components", []) if c.get("name")}


def verify_story_coverage(tasks_json: dict, stories_path: str) -> None:
    """Every story must have at least one task referencing it."""
    if not Path(stories_path).exists():
        print(f"⚠️  stories.json not found at {stories_path} — skipping story coverage check")
        return

    stories = load(stories_path)
    story_ids = extract_story_ids(stories)
    tasks = tasks_json.get("tasks", [])

    covered = {t.get("story") for t in tasks if t.get("story")}
    missing = story_ids - covered
    if missing:
        raise CompletionError("Stage 5", f"Stories with no tasks: {sorted(missing)}")


def verify_task_links(tasks_json: dict, goal_ids: set[str]) -> None:
    for task in tasks_json.get("tasks", []):
        tid = task.get("id", "?")
        links = task.get("links_to", {})
        if not isinstance(links, dict):
            raise StructureError("Stage 5", f"Task {tid} links_to must be an object")
        all_links = []
        for key in ["fr", "nfr", "con", "goal"]:
            vals = links.get(key, [])
            if isinstance(vals, str):
                vals = [vals]
            if not isinstance(vals, list):
                raise StructureError("Stage 5", f"Task {tid} links_to.{key} must be a list")
            all_links.extend(vals)
        if not all_links:
            raise TraceabilityError("Stage 5", f"Task {tid} does not link to any FR/NFR/CON/GOAL")
        missing = [link for link in all_links if link not in goal_ids]
        if missing:
            raise TraceabilityError("Stage 5", f"Task {tid} links_to contains unknown IDs: {missing}")


def verify_task_story_refs(tasks_json: dict, story_ids: set[str]) -> None:
    for task in tasks_json.get("tasks", []):
        tid = task.get("id", "?")
        story = task.get("story")
        if not story:
            raise TraceabilityError("Stage 5", f"Task {tid} must reference a story")
        if story not in story_ids:
            raise TraceabilityError("Stage 5", f"Task {tid} references unknown story: {story}")


def verify_task_files(tasks_json: dict, component_files: set[str]) -> None:
    for task in tasks_json.get("tasks", []):
        tid = task.get("id", "?")
        file_path = task.get("file", "")
        if not file_path:
            continue
        if file_path.startswith("src/"):
            if file_path not in component_files:
                # allow new files under an existing component directory
                component_dirs = {str(Path(p).parent).replace("\\", "/") for p in component_files}
                if not any(file_path.startswith(f"{d}/") for d in component_dirs):
                    raise TraceabilityError(
                        "Stage 5",
                        f"Task {tid} file '{file_path}' does not match components.json"
                    )
        elif any(
            pattern in file_path.lower()
            for pattern in ["__tests__", ".test.", ".spec.", ".d.ts", ".config."]
        ):
            continue
        elif file_path.startswith("tests/"):
            continue


def verify_task_components(tasks_json: dict, component_names: set[str]) -> None:
    for task in tasks_json.get("tasks", []):
        tid = task.get("id", "?")
        components = task.get("components", [])
        if isinstance(components, str):
            components = [components]
        if not components:
            raise TraceabilityError("Stage 5", f"Task {tid} must list components")
        unknown = [c for c in components if c not in component_names]
        if unknown:
            raise TraceabilityError("Stage 5", f"Task {tid} references unknown components: {unknown}")


def verify_definition_of_done(tasks_json: dict) -> None:
    command_re = re.compile(r"`[^`]+`")
    test_re = re.compile(r"(\.test\.|\.spec\.|tests/|test/)", re.IGNORECASE)
    for task in tasks_json.get("tasks", []):
        tid = task.get("id", "?")
        dod = task.get("definition_of_done")
        dod_items = dod if isinstance(dod, list) else [dod]
        ok = False
        for item in dod_items:
            if not isinstance(item, str):
                continue
            if command_re.search(item) or test_re.search(item):
                ok = True
                break
        if not ok:
            raise CompletionError(
                "Stage 5",
                f"Task {tid} definition_of_done must reference a command or test file"
            )


def verify_no_circular_deps(tasks_json: dict) -> None:
    """Detect cycles in task dependency graph using DFS."""
    tasks = tasks_json.get("tasks", [])
    task_ids = {t["id"] for t in tasks}
    graph = {t["id"]: t.get("depends_on", []) for t in tasks}

    # Validate all depends_on refs are real task IDs
    for tid, deps in graph.items():
        for dep in deps:
            if dep not in task_ids:
                raise TraceabilityError(
                    "Stage 5",
                    f"Task {tid} depends on '{dep}' which does not exist"
                )

    visited = set()
    in_stack = set()

    def dfs(node: str) -> None:
        if node in in_stack:
            raise StructureError("Stage 5", f"Circular dependency detected involving task: {node}")
        if node in visited:
            return
        visited.add(node)
        in_stack.add(node)
        for dep in graph.get(node, []):
            dfs(dep)
        in_stack.remove(node)

    for task_id in task_ids:
        dfs(task_id)


def verify_execution_order(tasks_json: dict) -> None:
    order = tasks_json.get("execution_order", [])
    if not isinstance(order, list) or not order:
        raise CompletionError("Stage 5", "execution_order must be a non-empty list")
    task_ids = {t.get("id") for t in tasks_json.get("tasks", []) if t.get("id")}
    seen = set()
    for batch in order:
        if not isinstance(batch, list) or not batch:
            raise CompletionError("Stage 5", "execution_order must be a list of non-empty lists")
        for tid in batch:
            if tid not in task_ids:
                raise TraceabilityError("Stage 5", f"execution_order references unknown task: {tid}")
            seen.add(tid)
    if seen != task_ids:
        missing = task_ids - seen
        extra = seen - task_ids
        if missing:
            raise CompletionError("Stage 5", f"execution_order missing tasks: {sorted(missing)}")
        if extra:
            raise CompletionError("Stage 5", f"execution_order has unknown tasks: {sorted(extra)}")


def verify_trivial(tasks_json: dict, plan_path: str, goal_ids: set[str], component_files: set[str]) -> None:
    tasks = tasks_json.get("tasks", [])
    if len(tasks) < 1:
        raise CompletionError("Stage 5", "Trivial plans must have at least one task")
    verify_tasks_completeness(tasks_json)
    verify_task_links(tasks_json, goal_ids)
    verify_task_files(tasks_json, component_files)
    verify_definition_of_done(tasks_json)

    try:
        text = Path(plan_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise CompletionError("Stage 5", f"plan_story_final.md not found at {plan_path}")
    if len(text.strip()) < 50:
        raise CompletionError("Stage 5", "plan_story_final.md is too short")
    if not re.search(r"\b(FR|NFR|CON|GOAL)-\d+\b", text):
        raise CompletionError("Stage 5", "plan_story_final.md must cite at least one FR/NFR/CON/GOAL ID")


def main() -> int:
    args = [a for a in sys.argv[1:]]
    trivial = "--trivial" in args
    require_deps = "--require-deps" in args
    require_order = "--require-order" in args
    args = [a for a in args if a not in ["--trivial", "--require-deps", "--require-order"]]

    if len(args) < 1:
        print("Usage: python tasks_structure.py <tasks.json> [stories.json] [goals.json] [components.json] [--trivial] [--require-deps] [--require-order]")
        return 1

    tasks_path = args[0]
    stories_path = args[1] if len(args) > 1 else ".agents/artifacts/stage-4/stories.json"
    goals_path = args[2] if len(args) > 2 else ".agents/artifacts/stage-1/goals.json"
    components_path = args[3] if len(args) > 3 else ".agents/artifacts/stage-2/components.json"

    try:
        tasks_json = load(tasks_path)
        validate_schema(tasks_json, "tasks", "Stage 5")

        goals = load(goals_path) if Path(goals_path).exists() else {}
        goal_ids = extract_goal_ids(goals) if goals else set()
        components = load(components_path) if Path(components_path).exists() else {}
        component_files = extract_component_files(components) if components else set()
        component_names = extract_component_names(components) if components else set()

        if trivial:
            plan_path = args[1] if len(args) > 1 else ".agents/artifacts/stage-5/plan_story_final.md"
            verify_trivial(tasks_json, plan_path, goal_ids, component_files)
            print("✅ Stage 5 verification PASSED (Trivial — plan confirmed)")
            return 0

        verify_tasks_completeness(tasks_json)
        verify_definition_of_done(tasks_json)
        verify_task_links(tasks_json, goal_ids)
        if Path(stories_path).exists():
            stories = load(stories_path)
            story_ids = extract_story_ids(stories)
            verify_task_story_refs(tasks_json, story_ids)
            verify_story_coverage(tasks_json, stories_path)
        if component_files:
            verify_task_files(tasks_json, component_files)
        if component_names:
            verify_task_components(tasks_json, component_names)
        verify_no_circular_deps(tasks_json)

        if require_order:
            if not tasks_json.get("execution_order"):
                raise CompletionError("Stage 5", "execution_order required for Large requests")
            verify_execution_order(tasks_json)

        print(f"✅ Stage 5 verification passed: {len(tasks_json.get('tasks', []))} tasks")
        return 0

    except (StructureError, TraceabilityError, CompletionError) as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
