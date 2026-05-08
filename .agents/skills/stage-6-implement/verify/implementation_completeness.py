#!/usr/bin/env python3
"""
Verification script for Stage 6 (Implementation): Completeness Check

Validates that src/ directory is non-empty, build/test evidence exists,
and every story in stories.json has at least one substantive test file with
assertions that imports implementation code. Also enforces no placeholder
content, regression/new-test separation, and scope discipline based on
tasks.json, progress.json, and test_snapshot.json.

Usage:
    python implementation_completeness.py .agents/artifacts/stage-6/

Exit code: 0 = pass, 1 = fail
"""

import json
import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent))
from exceptions import CompletionError, TraceabilityError, StructureError


def load_json(path: str) -> dict:
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


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def parse_tasks(tasks_path: str) -> tuple[list, dict, dict, dict, set]:
    tasks_json = load_json(tasks_path)
    tasks = tasks_json.get("tasks", [])
    story_to_tests: dict[str, set] = {}
    story_to_files: dict[str, set] = {}
    task_ids = []
    allowed_files: set[str] = set()

    for task in tasks:
        task_id = task.get("id")
        if task_id:
            task_ids.append(task_id)

        story_id = task.get("story")
        if story_id:
            story_to_tests.setdefault(story_id, set())

        file_path = task.get("file")
        if isinstance(file_path, str) and file_path.strip():
            allowed_files.add(file_path.strip())
            if story_id:
                story_to_files.setdefault(story_id, set()).add(file_path.strip())

        for test_entry in task.get("tests", []) or []:
            if not isinstance(test_entry, str):
                continue
            test_path = test_entry.split(":", 1)[0].strip()
            if not test_path:
                continue
            allowed_files.add(test_path)
            if story_id:
                story_to_tests.setdefault(story_id, set()).add(test_path)

    return tasks, story_to_tests, story_to_files, {"task_ids": set(task_ids)}, allowed_files


def story_links_map(stories_path: str) -> dict:
    stories_json = load_json(stories_path)
    links_map: dict[str, set] = {}
    for story in stories_json.get("stories", []):
        sid = story.get("id")
        if not sid:
            continue
        links = set([sid])
        links_to = story.get("links_to", {}) or {}
        for key in ["fr", "goal", "nfr", "con", "flow"]:
            links.update(links_to.get(key, []) or [])
        links_map[sid] = links
    return links_map


def find_import_matches(content: str, impl_files: set[str]) -> bool:
    for impl in impl_files:
        impl_path = Path(impl)
        base = impl_path.stem
        if base and re.search(rf"from\s+['\"](.*/)?{re.escape(base)}['\"]", content):
            return True
        if base and re.search(rf"require\(\s*['\"](.*/)?{re.escape(base)}['\"]\s*\)", content):
            return True
        if impl in content:
            return True
    return False


def has_assertions(content: str) -> bool:
    patterns = [r"\bexpect\s*\(", r"\bassert\b", r"\btoBe\b", r"\bshould\b", r"\bassertThat\b"]
    return any(re.search(p, content) for p in patterns)


def verify_story_test_coverage(stories_path: str, tasks_path: str) -> None:
    stories_json = load_json(stories_path)
    story_ids = [s["id"] for s in stories_json.get("stories", []) if s.get("id")]
    _, story_to_tests, story_to_files, _, _ = parse_tasks(tasks_path)
    links_map = story_links_map(stories_path)

    uncovered = []
    for sid in story_ids:
        test_files = list(story_to_tests.get(sid, set()))
        if not test_files:
            uncovered.append(sid)
            continue

        link_tokens = links_map.get(sid, {sid})
        impl_files = story_to_files.get(sid, set())
        found = False
        for test_path in test_files:
            test_file = Path(test_path)
            if not test_file.exists():
                continue
            content = read_text(test_file)
            if not has_assertions(content):
                continue
            is_e2e = "e2e" in test_file.parts or "integration" in test_file.parts
            if impl_files and not is_e2e and not find_import_matches(content, impl_files):
                continue
            if any(token in content for token in link_tokens):
                found = True
                break

        if not found:
            uncovered.append(sid)

    if uncovered:
        raise TraceabilityError(
            "Stage 6",
            f"Stories with no substantive test coverage: {uncovered}. "
            "Tests must include assertions, reference the story/linked IDs, and (for non-e2e) import the implementation."
        )


def verify_logs(build_log: str, build_exit: str, test_log: str, test_exit: str) -> None:
    for log_path in [build_log, test_log]:
        path = Path(log_path)
        if not path.exists() or path.stat().st_size == 0:
            raise CompletionError("Stage 6", f"Missing or empty log file: {log_path}")

    for exit_path, label in [(build_exit, "build"), (test_exit, "test")]:
        path = Path(exit_path)
        if not path.exists():
            raise CompletionError("Stage 6", f"Missing {label} exit code file: {exit_path}")
        content = read_text(path).strip()
        if not content.isdigit():
            raise CompletionError("Stage 6", f"Invalid {label} exit code in {exit_path}: {content}")
        if int(content) != 0:
            raise CompletionError("Stage 6", f"{label.capitalize()} exit code is non-zero: {content}")


def verify_test_snapshot(snapshot_path: str) -> list[str]:
    path = Path(snapshot_path)
    if not path.exists():
        raise CompletionError("Stage 6", f"Missing test snapshot: {snapshot_path}")
    snapshot = load_json(snapshot_path)
    files = snapshot.get("test_files", []) if isinstance(snapshot, dict) else []
    if not isinstance(files, list) or not files:
        raise CompletionError("Stage 6", "test_snapshot.json must include non-empty test_files list")
    return [f for f in files if isinstance(f, str)]


def verify_test_runs(progress: dict, test_pre_log: str, test_pre_exit: str, test_new_log: str, test_new_exit: str) -> None:
    test_mode = progress.get("test_mode")
    if test_mode not in ["split", "full-suite"]:
        raise CompletionError("Stage 6", "progress.json must set test_mode to 'split' or 'full-suite'")

    if test_mode == "full-suite":
        return

    for log_path in [test_pre_log, test_new_log]:
        path = Path(log_path)
        if not path.exists() or path.stat().st_size == 0:
            raise CompletionError("Stage 6", f"Missing or empty log file: {log_path}")

    for exit_path, label in [(test_pre_exit, "pre-test"), (test_new_exit, "new-test")]:
        path = Path(exit_path)
        if not path.exists():
            raise CompletionError("Stage 6", f"Missing {label} exit code file: {exit_path}")
        content = read_text(path).strip()
        if not content.isdigit():
            raise CompletionError("Stage 6", f"Invalid {label} exit code in {exit_path}: {content}")
        if int(content) != 0:
            raise CompletionError("Stage 6", f"{label.capitalize()} exit code is non-zero: {content}")


def verify_progress(progress_path: str, tasks_path: str, allowed_files: set) -> dict:
    path = Path(progress_path)
    if not path.exists():
        raise CompletionError("Stage 6", f"Missing progress record: {progress_path}")
    progress = load_json(progress_path)
    completed = progress.get("completed_tasks", []) or []
    verified = progress.get("tasks_verified", []) or []
    modified = progress.get("modified_files", []) or []

    if not isinstance(completed, list) or not isinstance(verified, list) or not isinstance(modified, list):
        raise CompletionError(
            "Stage 6",
            "progress.json must include lists: completed_tasks, tasks_verified, modified_files"
        )

    _, _, _, meta, _ = parse_tasks(tasks_path)
    task_ids = meta.get("task_ids", set())

    unknown_tasks = [t for t in completed if t not in task_ids]
    if unknown_tasks:
        raise CompletionError("Stage 6", f"progress.json lists unknown tasks: {unknown_tasks}")

    unknown_verified = [t for t in verified if t not in task_ids]
    if unknown_verified:
        raise CompletionError("Stage 6", f"progress.json lists unknown verified tasks: {unknown_verified}")

    not_completed = [t for t in verified if t not in completed]
    if not_completed:
        raise CompletionError("Stage 6", "tasks_verified must be a subset of completed_tasks")

    out_of_scope = [f for f in modified if f not in allowed_files]
    if out_of_scope:
        raise CompletionError("Stage 6", f"progress.json lists files not in tasks.json: {out_of_scope}")

    return progress


def count_non_comment_non_import_lines(content: str) -> int:
    count = 0
    for raw in content.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("//") or line.startswith("#"):
            continue
        if line.startswith("/*") or line.startswith("*") or line.startswith("*/"):
            continue
        if line.startswith("import ") or line.startswith("from "):
            continue
        count += 1
    return count


def verify_no_placeholders(paths: list[Path]) -> None:
    patterns = [
        re.compile(r"\bTODO\b", re.IGNORECASE),
        re.compile(r"\bFIXME\b", re.IGNORECASE),
        re.compile(r"\bTBD\b", re.IGNORECASE),
        re.compile(r"NotImplementedError"),
        re.compile(r"IMPLEMENT ME", re.IGNORECASE),
        re.compile(r"not implemented", re.IGNORECASE),
        re.compile(r"throw new Error\(['\"]not implemented['\"]\)", re.IGNORECASE),
        re.compile(r"lorem ipsum", re.IGNORECASE),
    ]
    offenders = []
    for path in paths:
        content = read_text(path)
        if any(p.search(content) for p in patterns):
            offenders.append(str(path))
            continue
        is_test = "test" in path.parts or ".test." in path.name or ".spec." in path.name
        min_lines = 3 if is_test else 5
        if count_non_comment_non_import_lines(content) < min_lines:
            offenders.append(str(path))
    if offenders:
        raise CompletionError("Stage 6", f"Placeholder content found in files: {offenders}")


def verify_test_files_exist(tasks_path: str) -> list[Path]:
    _, _, _, _, allowed_files = parse_tasks(tasks_path)
    test_files = [Path(p) for p in allowed_files if "test" in Path(p).parts or ".test." in Path(p).name]
    missing = [str(p) for p in test_files if not p.exists()]
    if missing:
        raise CompletionError("Stage 6", f"Test files listed in tasks.json are missing: {missing}")
    return test_files


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python implementation_completeness.py <stage_6_artifacts_dir>")
        return 1

    stage_dir = Path(sys.argv[1]).resolve()
    if not stage_dir.exists():
        print(f"❌ [Stage 6] Stage 6 artifacts directory not found: {stage_dir}")
        return 1
    artifacts_root = stage_dir.parent
    repo_root = artifacts_root.parent.parent

    src_dir = str(repo_root / "src")
    stories_path = str(artifacts_root / "stage-4" / "stories.json")
    tasks_path = str(artifacts_root / "stage-5" / "tasks.json")

    build_log = str(stage_dir / "build.log")
    build_exit = str(stage_dir / "build.exit")
    test_log = str(stage_dir / "test.log")
    test_exit = str(stage_dir / "test.exit")
    progress_path = str(stage_dir / "progress.json")
    test_snapshot = str(stage_dir / "test_snapshot.json")
    test_pre_log = str(stage_dir / "test_pre.log")
    test_pre_exit = str(stage_dir / "test_pre.exit")
    test_new_log = str(stage_dir / "test_new.log")
    test_new_exit = str(stage_dir / "test_new.exit")

    try:
        source_files = verify_src_exists(src_dir)
        verify_no_empty_files(source_files)
        verify_logs(build_log, build_exit, test_log, test_exit)
        _, _, _, _, allowed_files = parse_tasks(tasks_path)
        progress = verify_progress(progress_path, tasks_path, allowed_files)
        verify_test_snapshot(test_snapshot)
        verify_test_runs(progress, test_pre_log, test_pre_exit, test_new_log, test_new_exit)
        verify_test_files_exist(tasks_path)
        verify_no_placeholders([Path(p) for p in allowed_files if Path(p).exists()])
        verify_story_test_coverage(stories_path, tasks_path)

        print(
            f"✅ Stage 6 verification passed: {len(source_files)} source files, "
            "logs present, progress in scope, all stories have test coverage"
        )
        return 0

    except (CompletionError, TraceabilityError, StructureError) as e:
        print(f"❌ {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
