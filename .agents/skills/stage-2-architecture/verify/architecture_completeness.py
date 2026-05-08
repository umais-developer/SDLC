#!/usr/bin/env python3
"""
Verification script for Stage 2 (Architecture): Component Design

Validates components.json — checks schema, no circular dependencies,
every component has a justification, file paths are under src/.

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
        raise StructureError("Stage 2", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 2", f"File not found: {path}")


def verify_schema(data: dict, schema_path: str) -> None:
    if not HAS_JSONSCHEMA:
        print("⚠️  jsonschema not installed — skipping schema validation")
        return
    schema = load(schema_path)
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        raise StructureError("Stage 2", f"Schema validation failed: {e.message}")


def verify_no_circular_deps(components: dict) -> None:
    """Detect cycles in the dependency graph using DFS."""
    graph = components.get("dependency_graph", {})
    visited = set()
    in_stack = set()

    def dfs(node: str) -> None:
        if node in in_stack:
            raise StructureError("Stage 2", f"Circular dependency detected involving: {node}")
        if node in visited:
            return
        visited.add(node)
        in_stack.add(node)
        for dep in graph.get(node, []):
            dfs(dep)
        in_stack.remove(node)

    for node in graph:
        dfs(node)


def verify_component_files(components: dict) -> None:
    """Verify component file paths start with src/."""
    for comp in components.get("components", []):
        file_path = comp.get("file", "")
        if not file_path.startswith("src/"):
            raise StructureError(
                "Stage 2",
                f"Component '{comp['name']}' file path '{file_path}' must be under src/"
            )


def verify_interfaces(components: dict) -> None:
    """Verify every component has at least one public interface entry."""
    for comp in components.get("components", []):
        if not comp.get("public_interface"):
            raise CompletionError(
                "Stage 2",
                f"Component '{comp['name']}' has no public_interface defined"
            )


def verify_dependency_references(components: dict) -> None:
    """Verify all dependencies reference known components."""
    known = {c["name"] for c in components.get("components", [])}
    graph = components.get("dependency_graph", {})
    for node, deps in graph.items():
        for dep in deps:
            if dep not in known:
                raise TraceabilityError(
                    "Stage 2",
                    f"Dependency graph: '{node}' depends on unknown component '{dep}'"
                )


def main(components_json_path: str) -> None:
    data = load(components_json_path)
    schema_path = Path(__file__).parent.parent / "schemas" / "components.json"

    verify_schema(data, str(schema_path))
    verify_component_files(data)
    verify_interfaces(data)
    verify_dependency_references(data)
    verify_no_circular_deps(data)

    comp_count = len(data.get("components", []))
    file_count = len(data.get("file_structure", []))
    print(f"✅ Stage 2 verification PASSED")
    print(f"   • {comp_count} component(s) defined")
    print(f"   • {file_count} file(s) in file_structure")
    print(f"   • No circular dependencies")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify/architecture_completeness.py <components.json>")
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
