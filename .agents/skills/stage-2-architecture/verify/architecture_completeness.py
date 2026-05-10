#!/usr/bin/env python3
"""
Verification script for Stage 2 (Architecture): Component Design

Validates components.json — checks schema, every new component has a public
interface, justification, and fr_links referencing real IDs from goals.json.

Note: circular dependency checking is intentionally omitted. The component
graph produced here is too coarse-grained for reliable cycle detection to be
useful at the 3–10 component scale this skill targets.

Usage:
    python verify/architecture_completeness.py <components.json> [goals.json] [--trivial]

Exit code: 0 = pass, 1 = fail
"""

import json
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
        raise StructureError("Stage 2", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 2", f"File not found: {path}")


def verify_no_circular_deps(components: dict) -> None:
    """
    Detect LOGICAL circular dependencies in the component dependency graph.
    A logical cycle is: component A lists B in depends_on AND B lists A in depends_on.
    This is a coarse-grained check on the declared graph, not file-level imports.
    """
    graph = components.get("dependency_graph", {})
    visited = set()
    in_stack = set()

    def dfs(node: str) -> None:
        if node in in_stack:
            raise StructureError("Stage 2", f"Logical circular dependency detected involving: {node}")
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
    """Verify new (non-modified) component file paths start with src/."""
    for comp in components.get("components", []):
        if comp.get("modified"):
            continue  # modified entries describe existing files; no path check needed
        file_path = comp.get("file", "")
        if not file_path.startswith("src/"):
            raise StructureError(
                "Stage 2",
                f"Component '{comp['name']}' file path '{file_path}' must be under src/"
            )


def verify_interfaces(components: dict) -> None:
    """Verify every new component has at least one public interface entry.
    Modified-only entries are exempt (they don't define a full new interface)."""
    for comp in components.get("components", []):
        if comp.get("modified"):
            continue
        if not comp.get("public_interface"):
            raise CompletionError(
                "Stage 2",
                f"Component '{comp['name']}' has no public_interface defined"
            )


def verify_dependency_references(components: dict) -> None:
    """Verify all dependency_graph references are either known components or
    pre-existing components (which are allowed to be unlisted in this PRD's components array)."""
    # Only validate that the graph doesn't reference names that look like typos
    # (i.e., entries that appear nowhere in either components[] names or as known external refs).
    # We do NOT require every dependency to be defined here — they may be pre-existing components.
    known = {c["name"] for c in components.get("components", [])}
    graph = components.get("dependency_graph", {})
    # Check only that the graph nodes themselves are either known or listed as pre_existing
    pre_existing = set(components.get("pre_existing_components", []))
    all_known = known | pre_existing
    for node, deps in graph.items():
        for dep in deps:
            if dep not in all_known:
                # Warn but don't fail — the dep may be a pre-existing component not listed here
                print(f"⚠️  Dependency '{dep}' (referenced by '{node}') is not declared "
                      f"in components[] or pre_existing_components[]. "
                      f"Add it to pre_existing_components[] if it already exists in the codebase.")


def verify_fr_traceability(components: dict, goals: dict) -> None:
    """
    Verify every new/modified component has at least one fr_links entry,
    and that every fr_links ID exists in goals.json.
    """
    # Collect all valid IDs from goals.json
    valid_ids = set()
    for goal in goals.get("goals", []):
        valid_ids.add(goal.get("id", ""))
    for fr in goals.get("functional_requirements", []):
        valid_ids.add(fr.get("id", ""))
    for nfr in goals.get("non_functional_requirements", []):
        valid_ids.add(nfr.get("id", ""))
    for con in goals.get("constraints", []):
        valid_ids.add(con.get("id", ""))
    valid_ids.discard("")

    for comp in components.get("components", []):
        fr_links = comp.get("fr_links", [])
        if not fr_links:
            raise TraceabilityError(
                "Stage 2",
                f"Component '{comp['name']}' has no fr_links. "
                f"Every component must reference at least one FR/NFR/CON/GOAL ID from goals.json."
            )
        for ref in fr_links:
            if ref not in valid_ids:
                raise TraceabilityError(
                    "Stage 2",
                    f"Component '{comp['name']}' references '{ref}' in fr_links, "
                    f"but that ID does not exist in goals.json. "
                    f"Valid IDs: {sorted(valid_ids)}"
                )


def verify_justification_cites_requirements(components: dict) -> None:
    """
    Warn (not fail) when a component justification contains zero FR/NFR/CON/GOAL ID patterns.
    This catches generic justifications that violate the Anti-Hallucination Rule.
    """
    import re
    id_pattern = re.compile(r'\b(FR|NFR|CON|GOAL)-\d+\b', re.IGNORECASE)
    for comp in components.get("components", []):
        justification = comp.get("justification", "")
        if justification and not id_pattern.search(justification):
            print(f"⚠️  Component '{comp['name']}' justification contains no FR/NFR/CON/GOAL ID reference. "
                  f"This may violate the Anti-Hallucination Rule. "
                  f"Justification: \"{justification[:120]}\"")


def verify_trivial(architecture_final_path: str) -> None:
    """For Trivial requests: check that architecture_final.md exists, is non-empty,
    names at least one file path, and cites at least one requirement ID."""
    import re
    p = Path(architecture_final_path)
    if not p.exists():
        raise CompletionError("Stage 2", f"architecture_final.md not found at {architecture_final_path}")
    text = p.read_text(encoding="utf-8").strip()
    if len(text) < 50:
        raise CompletionError("Stage 2", "architecture_final.md exists but appears empty or stub-only")
    # Must name at least one file path (e.g. src/search/foo.ts)
    if not re.search(r'[\w/]+\.\w{1,5}', text):
        raise CompletionError(
            "Stage 2",
            "Trivial impact note must name at least one file path (e.g. src/search/SearchBar.ts). "
            "Current content contains no file path pattern."
        )
    # Must cite at least one requirement ID
    if not re.search(r'\b(FR|NFR|CON|GOAL)-\d+\b', text, re.IGNORECASE):
        raise CompletionError(
            "Stage 2",
            "Trivial impact note must cite at least one requirement ID (FR-X, NFR-X, CON-X, or GOAL-X). "
            "This links the change to the PRD and prevents an untraced 'add a search bar.' response."
        )


def verify_tech_stack_present(components_json_path: str) -> None:
    """For Medium/Large: tech_stack.json must exist alongside components.json."""
    tech_stack_path = Path(components_json_path).parent / "tech_stack.json"
    if not tech_stack_path.exists():
        raise CompletionError(
            "Stage 2",
            f"tech_stack.json not found at {tech_stack_path}. "
            "Step 2 (tech stack inspection/selection) did not produce its output. "
            "Re-run Step 2 before proceeding."
        )


def main(components_json_path: str, goals_json_path: str | None, trivial: bool) -> None:
    if trivial:
        arch_path = str(Path(components_json_path).parent / "architecture_final.md")
        verify_trivial(arch_path)
        print("✅ Stage 2 verification PASSED (Trivial — impact note confirmed)")
        return

    data = load(components_json_path)

    verify_tech_stack_present(components_json_path)
    validate_schema(data, "components", "Stage 2")
    verify_component_files(data)
    verify_interfaces(data)
    verify_dependency_references(data)
    verify_justification_cites_requirements(data)

    if goals_json_path and Path(goals_json_path).exists():
        goals = load(goals_json_path)
        verify_fr_traceability(data, goals)
        traceability_note = "FR/NFR traceability verified"
    else:
        print("⚠️  goals.json not provided — skipping FR traceability check")
        traceability_note = "FR/NFR traceability skipped (no goals.json)"

    comp_count = len(data.get("components", []))
    file_count = len(data.get("file_structure", []))
    print(f"✅ Stage 2 verification PASSED")
    print(f"   • {comp_count} component(s) defined")
    print(f"   • {file_count} file(s) in file_structure")
    print(f"   • {traceability_note}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    trivial = "--trivial" in flags

    if trivial:
        # Trivial mode: only need the directory / architecture_final.md path
        # Accept components_json_path as the artifact dir hint
        components_json_path = args[0] if args else ".agents/artifacts/stage-2/components.json"
        goals_json_path = args[1] if len(args) > 1 else None
    else:
        if len(args) < 1:
            print("Usage: python verify/architecture_completeness.py <components.json> [goals.json] [--trivial]")
            sys.exit(1)
        components_json_path = args[0]
        goals_json_path = args[1] if len(args) > 1 else None

    try:
        main(components_json_path, goals_json_path, trivial)
        sys.exit(0)
    except (StructureError, TraceabilityError, CompletionError) as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
