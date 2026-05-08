#!/usr/bin/env python3
"""
Verification script for Stage 7 (Code Review): Review Verdict

Validates review.json, enforces evidence-based citations, and runs
deterministic structural checks to prevent fabricated approvals.

Exit code: 0 = APPROVE, 1 = CHANGES_REQUIRED or error
"""

import json
import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).parent))
from exceptions import GateError, StructureError


def load(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StructureError("Stage 7", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 7", f"File not found: {path}")


def verify_verdict(review: dict) -> None:
    verdict = review.get("verdict", "")
    if verdict not in ("APPROVE", "CHANGES_REQUIRED"):
        raise StructureError(
            "Stage 7",
            f"verdict must be 'APPROVE' or 'CHANGES_REQUIRED', got: '{verdict}'"
        )


def verify_verdict_consistency(review: dict) -> None:
    """Critical or High findings must result in CHANGES_REQUIRED."""
    verdict = review.get("verdict", "")
    findings = review.get("findings", [])

    blocking = [
        f for f in findings
        if f.get("severity") in ("Critical", "High")
    ]

    if blocking and verdict == "APPROVE":
        ids = [f["id"] for f in blocking]
        raise GateError(
            "Stage 7",
            f"verdict is APPROVE but Critical/High findings exist: {ids}. "
            "Fix all Critical and High findings before approving."
        )

    if verdict == "CHANGES_REQUIRED":
        must_fix = review.get("must_fix_before_proceeding", [])
        if not isinstance(must_fix, list) or not must_fix:
            raise StructureError(
                "Stage 7",
                "verdict is CHANGES_REQUIRED but must_fix_before_proceeding is empty"
            )
        must_fix_ids = []
        for item in must_fix:
            if not isinstance(item, dict):
                raise StructureError("Stage 7", "must_fix_before_proceeding entries must be objects")
            for key in ["id", "severity", "file", "line_range", "links_to", "suggested_fix"]:
                if key not in item:
                    raise StructureError("Stage 7", f"must_fix entry missing {key}")
                if key != "links_to" and not item.get(key):
                    raise StructureError("Stage 7", f"must_fix entry missing {key}")
            must_fix_ids.append(item.get("id"))

        blocking_ids = [f.get("id") for f in blocking if f.get("id")]
        missing_blockers = [bid for bid in blocking_ids if bid not in must_fix_ids]
        if missing_blockers:
            raise GateError(
                "Stage 7",
                f"must_fix_before_proceeding missing Critical/High findings: {missing_blockers}"
            )

    if verdict == "APPROVE":
        must_fix = review.get("must_fix_before_proceeding", [])
        if must_fix:
            raise StructureError(
                "Stage 7",
                "verdict is APPROVE but must_fix_before_proceeding is not empty"
            )


def parse_line_range(value: str) -> tuple[int, int]:
    match = re.match(r"^L(\d+)(-L?(\d+))?$", value.strip())
    if not match:
        raise ValueError("line_range must be 'L<start>' or 'L<start>-L<end>'")
    start = int(match.group(1))
    end = int(match.group(3)) if match.group(3) else start
    if start <= 0 or end <= 0 or end < start:
        raise ValueError("line_range values must be positive and start <= end")
    return start, end


def read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []


def validate_file_and_range(repo_root: Path, file_path: str, line_range: str) -> None:
    if file_path.startswith("/") or ":\\" in file_path:
        raise StructureError("Stage 7", f"File path must be relative: {file_path}")
    abs_path = (repo_root / file_path).resolve()
    if not abs_path.exists():
        raise StructureError("Stage 7", f"File not found: {file_path}")
    lines = read_lines(abs_path)
    start, end = parse_line_range(line_range)
    if end > len(lines):
        raise StructureError(
            "Stage 7",
            f"Line range {line_range} exceeds file length ({len(lines)}): {file_path}"
        )


def validate_links(links: list) -> None:
    if not isinstance(links, list):
        raise StructureError("Stage 7", "links_to must be a list")
    if not links:
        return
    pattern = re.compile(r"^(FR|NFR|CON|GOAL|S|T)-\d+", re.IGNORECASE)
    for link in links:
        if not isinstance(link, str) or not pattern.match(link):
            raise StructureError("Stage 7", f"Invalid links_to entry: {link}")


def verify_findings_complete(review: dict, repo_root: Path) -> None:
    for finding in review.get("findings", []):
        if not finding.get("id"):
            raise StructureError("Stage 7", "Finding missing id")
        if finding.get("severity") not in ("Critical", "High", "Medium", "Low"):
            raise StructureError("Stage 7", f"Invalid severity for {finding.get('id')}")
        if not finding.get("file") or not finding.get("line_range"):
            raise StructureError("Stage 7", f"Finding {finding.get('id')} missing file/line_range")
        if not finding.get("suggested_fix"):
            raise StructureError("Stage 7", f"Finding {finding.get('id')} missing suggested_fix")
        if "links_to" not in finding:
            raise StructureError("Stage 7", f"Finding {finding.get('id')} missing links_to")
        validate_links(finding.get("links_to", []))
        validate_file_and_range(repo_root, finding["file"], finding["line_range"])


def verify_must_fix_entries(review: dict, repo_root: Path) -> None:
    must_fix = review.get("must_fix_before_proceeding", [])
    if not must_fix:
        return
    for item in must_fix:
        if not isinstance(item, dict):
            raise StructureError("Stage 7", "must_fix_before_proceeding entries must be objects")
        if item.get("severity") not in ("Critical", "High", "Medium", "Low"):
            raise StructureError("Stage 7", f"Invalid severity in must_fix: {item.get('id')}")
        if "links_to" not in item:
            raise StructureError("Stage 7", f"must_fix entry missing links_to: {item.get('id')}")
        validate_links(item.get("links_to", []))
        if item.get("file") and item.get("line_range"):
            validate_file_and_range(repo_root, item["file"], item["line_range"])


def verify_checks_complete(review: dict, repo_root: Path, required_dimensions: set) -> None:
    checks = review.get("checks_performed", [])
    if not isinstance(checks, list) or not checks:
        raise StructureError("Stage 7", "checks_performed must be a non-empty list")

    seen_dimensions: set[str] = set()
    for check in checks:
        if not check.get("id"):
            raise StructureError("Stage 7", "Check missing id")
        dimension = check.get("dimension")
        if dimension not in {"spec", "architecture", "test", "quality", "security", "performance"}:
            raise StructureError("Stage 7", f"Invalid check dimension: {dimension}")
        seen_dimensions.add(dimension)
        if not check.get("file") or not check.get("line_range"):
            raise StructureError("Stage 7", f"Check {check.get('id')} missing file/line_range")
        if "links_to" not in check:
            raise StructureError("Stage 7", f"Check {check.get('id')} missing links_to")
        validate_links(check.get("links_to", []))
        validate_file_and_range(repo_root, check["file"], check["line_range"])
        if check.get("result") not in ("pass", "fail"):
            raise StructureError("Stage 7", f"Invalid check result for {check.get('id')}")
def verify_strengths(review: dict, repo_root: Path) -> None:
    strengths = review.get("strengths", [])
    if not isinstance(strengths, list):
        raise StructureError("Stage 7", "strengths must be a list")
    for item in strengths:
        if not isinstance(item, dict):
            raise StructureError("Stage 7", "strengths entries must be objects")
        if not item.get("id") or not item.get("file") or not item.get("line_range"):
            raise StructureError("Stage 7", "strengths entry missing id/file/line_range")
        if not item.get("description"):
            raise StructureError("Stage 7", "strengths entry missing description")
        validate_file_and_range(repo_root, item["file"], item["line_range"])

    missing = required_dimensions - seen_dimensions
    if missing:
        raise GateError("Stage 7", f"Missing required review dimensions: {sorted(missing)}")


def get_size(problem_path: Path) -> str:
    try:
        data = load(str(problem_path))
        size = data.get("size")
        if isinstance(size, str):
            return size.strip().lower()
    except Exception:
        pass
    return "medium"


def gather_task_paths(tasks_path: Path) -> tuple[set, set, list]:
    tasks_json = load(str(tasks_path))
    tasks = tasks_json.get("tasks", [])
    task_files = set()
    test_files = set()
    task_ids = []
    for task in tasks:
        task_id = task.get("id")
        if task_id:
            task_ids.append(task_id)
        file_path = task.get("file")
        if isinstance(file_path, str) and file_path.strip():
            task_files.add(file_path.strip())
        for test_entry in task.get("tests", []) or []:
            if not isinstance(test_entry, str):
                continue
            test_path = test_entry.split(":", 1)[0].strip()
            if test_path:
                test_files.add(test_path)
    return task_files, test_files, task_ids


def verify_structural_checks(repo_root: Path, artifacts_root: Path) -> None:
    components_path = artifacts_root / "stage-2" / "components.json"
    stories_path = artifacts_root / "stage-4" / "stories.json"
    tasks_path = artifacts_root / "stage-5" / "tasks.json"
    progress_path = artifacts_root / "stage-6" / "progress.json"

    components = load(str(components_path))
    stories = load(str(stories_path))
    progress = load(str(progress_path))

    task_files, test_files, _ = gather_task_paths(tasks_path)

    missing_test_files = [p for p in test_files if not (repo_root / p).exists()]
    if missing_test_files:
        raise GateError("Stage 7", f"Missing test files listed in tasks.json: {missing_test_files}")

    modified_files = progress.get("modified_files", []) or []
    out_of_scope = [f for f in modified_files if f not in task_files and f not in test_files]
    if out_of_scope:
        raise GateError("Stage 7", f"progress.json references files not in tasks.json: {out_of_scope}")

    component_entries = components.get("components", []) if isinstance(components, dict) else []
    missing_components = []
    for comp in component_entries:
        if not isinstance(comp, dict):
            continue
        file_path = comp.get("file") or comp.get("path")
        if isinstance(file_path, str) and file_path.strip():
            if not (repo_root / file_path.strip()).exists():
                missing_components.append(file_path.strip())
    if missing_components:
        raise GateError("Stage 7", f"Components with missing files: {missing_components}")

    story_ids = [s.get("id") for s in stories.get("stories", []) if isinstance(s, dict)]
    if story_ids:
        if not test_files:
            raise GateError("Stage 7", "No test files found to satisfy story coverage")
        test_contents = ""
        for test_path in test_files:
            test_file = repo_root / test_path
            if test_file.exists():
                test_contents += "\n" + test_file.read_text(encoding="utf-8", errors="ignore")
        uncovered = [sid for sid in story_ids if sid and sid not in test_contents]
        if uncovered:
            raise GateError("Stage 7", f"Stories missing test references: {uncovered}")


def main(stage_7_dir: str) -> None:
    stage_dir = Path(stage_7_dir).resolve()
    if not stage_dir.exists():
        raise StructureError("Stage 7", f"Stage 7 artifacts directory not found: {stage_dir}")

    artifacts_root = stage_dir.parent
    repo_root = artifacts_root.parent.parent
    review_json_path = stage_dir / "review.json"

    review = load(str(review_json_path))
    problem_path = artifacts_root / "stage-1" / "problem.json"

    size = get_size(problem_path)
    required_dimensions = {
        "trivial": {"spec", "test"},
        "medium": {"spec", "architecture", "test", "quality"},
        "large": {"spec", "architecture", "test", "quality", "security", "performance"},
    }.get(size, {"spec", "architecture", "test", "quality"})

    verify_verdict(review)
    verify_findings_complete(review, repo_root)
    verify_checks_complete(review, repo_root, required_dimensions)
    verify_must_fix_entries(review, repo_root)
    verify_strengths(review, repo_root)
    verify_structural_checks(repo_root, artifacts_root)
    verify_verdict_consistency(review)

    if size == "trivial":
        if review.get("findings", []):
            raise StructureError("Stage 7", "Trivial reviews must not include findings")
        if review.get("strengths", []):
            raise StructureError("Stage 7", "Trivial reviews must not include strengths")
        if review.get("must_fix_before_proceeding", []):
            raise StructureError("Stage 7", "Trivial reviews must not include must_fix items")

    verdict = review["verdict"]
    finding_count = len(review.get("findings", []))
    critical = sum(1 for f in review.get("findings", []) if f.get("severity") == "Critical")
    high = sum(1 for f in review.get("findings", []) if f.get("severity") == "High")

    if verdict == "APPROVE":
        print(f"✅ Stage 7 verification PASSED — verdict: APPROVE")
        print(f"   • {finding_count} finding(s), {critical} critical, {high} high")
    else:
        must_fix = review.get("must_fix_before_proceeding", [])
        raise GateError(
            "Stage 7",
            f"verdict is CHANGES_REQUIRED — must fix: {must_fix} before proceeding to Stage 7.5"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify/code_review_verdict.py <stage_7_artifacts_dir>")
        sys.exit(1)
    try:
        main(sys.argv[1])
        sys.exit(0)
    except GateError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except (StructureError,) as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
