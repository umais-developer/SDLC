#!/usr/bin/env python3
"""
Verification script for Stage 6 (Implementation): Completeness Check

Validates that src/ directory is non-empty and every story in stories.json
has at least one source file referencing its ID in a test file.

Usage: python implementation_completeness.py <src_dir> <stories.json>

Exit code: 0 = pass, 1 = fail
"""

import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exceptions import CompletionError, TraceabilityError, StructureError


def load(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StructureError("Stage 6", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 6", f"File not found: {path}")


def verify_src_exists(src_dir: str) -> list:
    p = Path(src_dir)
    if not p.exists():
        raise CompletionError("Stage 6", f"src/ directory does not exist: {src_dir}")
    all_files = list(p.rglob("*"))
    source_files = [f for f in all_files if f.is_file()]
    if not source_files:
        raise CompletionError("Stage 6", f"src/ directory is empty — no source files found")
    return source_files


def verify_no_empty_files(source_files: list) -> None:
    empty = [str(f) for f in source_files if f.stat().st_size == 0]
    if empty:
        raise CompletionError("Stage 6", f"Empty source files found (placeholders not filled): {empty}")


def verify_story_test_coverage(stories_path: str, source_files: list) -> None:
    """Every story ID must appear in at least one test file."""
    stories_json = load(stories_path)
    story_ids = [s["id"] for s in stories_json.get("stories", [])]

    # Collect all test file contents
    test_files = [f for f in source_files if ".test." in f.name or "test" in f.parts]
    test_contents = ""
    for tf in test_files:
        try:
            test_contents += tf.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            pass

    if not test_files:
        raise CompletionError("Stage 6", "No test files found under src/. Every story must have test coverage.")

    uncovered = [sid for sid in story_ids if sid not in test_contents]
    if uncovered:
        raise TraceabilityError(
            "Stage 6",
            f"Stories with no test file referencing their ID: {uncovered}. "
            f"Add a comment like '// Story {uncovered[0]}' in the test file."
        )


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python implementation_completeness.py <src_dir> <stories.json>")
        return 1

    src_dir = sys.argv[1]
    stories_path = sys.argv[2]

    try:
        source_files = verify_src_exists(src_dir)
        verify_no_empty_files(source_files)
        verify_story_test_coverage(stories_path, source_files)

        print(f"✅ Stage 6 verification passed: {len(source_files)} source files, "
              f"all stories have test coverage")
        return 0

    except (CompletionError, TraceabilityError, StructureError) as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
