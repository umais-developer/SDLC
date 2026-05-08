#!/usr/bin/env python3
"""
Verification script for Stage 5 (Implementation Plan): Tasks Structure

Validates tasks.json — every story has at least one implementation task and
one test task, dependency graph is acyclic, all tasks reference valid stories.

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
        raise StructureError("Stage 5", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 5", f"File not found: {path}")


def verify_schema(data: dict, schema_path: str) -> None:
    if not HAS_JSONSCHEMA:
        print("⚠️  jsonschema not installed — skipping schema validation")
        return
    schema = load(schema_path)
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        raise StructureError("Stage 5", f"Schema validation failed: {e.message}")


def verify_tasks_completeness(tasks_json: dict) -> None:
    tasks = tasks_json.get("tasks", [])
    if not tasks:
        raise CompletionError("Stage 5", "At least one task is required")

    for task in tasks:
        tid = task.get("id", "?")
        if not task.get("story"):
            raise TraceabilityError("Stage 5", f"Task {tid} has no 'story' reference")
        if not task.get("file"):
            raise CompletionError("Stage 5", f"Task {tid} has no 'file' specified")
        if not task.get("definition_of_done"):
            raise CompletionError("Stage 5", f"Task {tid} has no 'definition_of_done'")


def verify_every_story_has_impl_and_test(tasks_json: dict, stories_path: str) -> None:
    """Every story must have at least one implementation task and one test task."""
    if not Path(stories_path).exists():
        print(f"⚠️  stories.json not found at {stories_path} — skipping story coverage check")
        return

    stories = load(stories_path)
    story_ids = {s["id"] for s in stories.get("stories", [])}
    tasks = tasks_json.get("tasks", [])

    stories_with_impl = set()
    stories_with_test = set()

    for task in tasks:
        story = task.get("story")
        if not story:
            continue
        title_lower = task.get("title", "").lower()
        file_lower = task.get("file", "").lower()
        # A task is a test task if its file is under tests/ or has .test. in name
        if ".test." in file_lower or "test" in file_lower.split("/")[0]:
            stories_with_test.add(story)
        else:
            stories_with_impl.add(story)

    missing_impl = story_ids - stories_with_impl
    missing_test = story_ids - stories_with_test

    if missing_impl:
        raise CompletionError(
            "Stage 5",
            f"Stories with no implementation task: {sorted(missing_impl)}"
        )
    if missing_test:
        raise CompletionError(
            "Stage 5",
            f"Stories with no test task: {sorted(missing_test)}"
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


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python tasks_structure.py <tasks.json> [stories.json]")
        return 1

    tasks_path = sys.argv[1]
    stories_path = sys.argv[2] if len(sys.argv) > 2 else ".agents/artifacts/stage-4/stories.json"
    schema_path = Path(__file__).parent.parent / "schemas" / "tasks.json"

    try:
        tasks_json = load(tasks_path)
        if schema_path.exists():
            verify_schema(tasks_json, str(schema_path))
        verify_tasks_completeness(tasks_json)
        verify_every_story_has_impl_and_test(tasks_json, stories_path)
        verify_no_circular_deps(tasks_json)

        print(f"✅ Stage 5 verification passed: {len(tasks_json.get('tasks', []))} tasks, "
              f"dependency graph acyclic")
        return 0

    except (StructureError, TraceabilityError, CompletionError) as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
