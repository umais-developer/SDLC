#!/usr/bin/env python3
"""
Verification script for Stage 8 (UAT): Deployment Gate

Validates UAT artifacts, verifies evidence files exist, and computes
the deployment gate deterministically from test results.

Exit code: 0 = APPROVED, 1 = BLOCKED or error
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "_shared"))
from exceptions import GateError, StructureError


def load(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StructureError("Stage 8", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 8", f"File not found: {path}")


def load_json(path: Path) -> dict:
    return load(str(path))


def normalize_results(results: dict) -> dict:
    if "results" not in results or not isinstance(results.get("results"), list):
        raise StructureError("Stage 8", "uat_results.json missing results[]")
    return results


def verify_no_unfixed_critical_bugs(results: dict) -> None:
    unfixed = [
        b["id"]
        for b in results.get("bugs", [])
        if b.get("severity") == "Critical" and not b.get("fix_verified", False)
    ]
    if unfixed:
        raise GateError(
            "Stage 8",
            f"Unfixed Critical bugs: {unfixed}. Must be fixed and verified before deploy."
        )


def verify_summary_consistency(results: dict) -> None:
    """passed + failed + skipped should equal total."""
    summary = results.get("execution_summary", {})
    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    skipped = summary.get("skipped", 0)
    actual_results = len(results.get("results", []))

    if passed + failed + skipped != total:
        raise StructureError(
            "Stage 8",
            f"Summary inconsistency: passed({passed}) + failed({failed}) + skipped({skipped}) "
            f"= {passed+failed+skipped}, but total = {total}"
        )
    if actual_results != total:
        raise StructureError(
            "Stage 8",
            f"results[] has {actual_results} entries but execution_summary.total = {total}"
        )

    status_counts = {"PASS": 0, "FAIL": 0, "SKIPPED": 0}
    for entry in results.get("results", []):
        status = entry.get("status")
        if status in status_counts:
            status_counts[status] += 1

    if status_counts["PASS"] != passed:
        raise StructureError("Stage 8", "execution_summary.passed does not match results")
    if status_counts["FAIL"] != failed:
        raise StructureError("Stage 8", "execution_summary.failed does not match results")
    if status_counts["SKIPPED"] != skipped:
        raise StructureError("Stage 8", "execution_summary.skipped does not match results")


def verify_app_health(stage_dir: Path) -> None:
    health = stage_dir / "app_health.json"
    if not health.exists():
        raise StructureError("Stage 8", "Missing app_health.json")
    data = load_json(health)
    for key in ["url", "started_at", "health_check_command", "exit_code", "response_excerpt"]:
        if key not in data:
            raise StructureError("Stage 8", f"app_health.json missing {key}")
    if data.get("exit_code") != 0:
        raise GateError("Stage 8", "app_health.json exit_code is non-zero")
    if not str(data.get("response_excerpt", "")).strip():
        raise StructureError("Stage 8", "app_health.json response_excerpt is empty")


def verify_evidence(stage_dir: Path, repo_root: Path, test_plan: dict, results: dict) -> None:
    plan_by_id = {t.get("id"): t for t in test_plan.get("test_cases", []) if t.get("id")}
    missing_results = [tid for tid in plan_by_id.keys() if tid not in {r.get("test_id") for r in results.get("results", [])}]
    if missing_results:
        raise StructureError("Stage 8", f"Missing results for test cases: {missing_results}")

    for entry in results.get("results", []):
        test_id = entry.get("test_id")
        if not test_id or test_id not in plan_by_id:
            raise StructureError("Stage 8", f"Result references unknown test_id: {test_id}")
        plan = plan_by_id[test_id]
        test_type = plan.get("type")
        status = entry.get("status")
        if test_type not in ("unit", "browser"):
            raise StructureError("Stage 8", f"Invalid test type for {test_id}: {test_type}")
        if test_type in ("unit", "browser"):
            test_path = plan.get("test_path")
            if not isinstance(test_path, str) or not test_path.strip():
                raise StructureError("Stage 8", f"Missing test_path for {test_id}")
            if not (repo_root / test_path.strip()).exists():
                raise GateError("Stage 8", f"Test file not found for {test_id}: {test_path}")
        if status not in ("PASS", "FAIL", "SKIPPED"):
            raise StructureError("Stage 8", f"Invalid status for {test_id}: {status}")
        evidence = entry.get("evidence", {})
        if test_type == "unit" and status == "PASS":
            artifacts = evidence.get("artifacts", []) if isinstance(evidence, dict) else []
            if not artifacts:
                raise GateError("Stage 8", f"Unit test {test_id} missing evidence artifacts")
            for path in artifacts:
                artifact_path = Path(path)
                if not artifact_path.exists() or artifact_path.stat().st_size == 0:
                    raise GateError("Stage 8", f"Missing or empty unit test evidence for {test_id}: {path}")

        if test_type == "browser" and status == "PASS":
            artifacts = evidence.get("artifacts", []) if isinstance(evidence, dict) else []
            if not artifacts:
                raise GateError("Stage 8", f"Browser test {test_id} missing artifact paths")
            for path in artifacts:
                artifact_path = Path(path)
                if not artifact_path.exists() or artifact_path.stat().st_size == 0:
                    raise GateError("Stage 8", f"Missing or empty artifact for {test_id}: {path}")


def verify_bug_schema(results: dict) -> None:
    valid_upstream = {"stage-4", "stage-5"}
    for bug in results.get("bugs", []):
        for key in [
            "id",
            "severity",
            "title",
            "description",
            "related_test_id",
            "evidence",
            "steps_to_reproduce",
            "root_cause",
            "fix_applied",
            "fix_verified",
        ]:
            if key not in bug:
                raise StructureError("Stage 8", f"Bug entry missing {key}")
        if bug.get("severity") not in ("Critical", "High", "Medium", "Low"):
            raise StructureError("Stage 8", f"Bug severity invalid: {bug.get('severity')}")
        if not isinstance(bug.get("steps_to_reproduce"), list):
            raise StructureError("Stage 8", "Bug steps_to_reproduce must be a list")
        if not isinstance(bug.get("fix_verified"), bool):
            raise StructureError("Stage 8", "Bug fix_verified must be boolean")
        upstream = bug.get("upstream_target")
        if upstream is not None and upstream not in valid_upstream:
            raise StructureError(
                "Stage 8",
                f"Bug {bug.get('id')} upstream_target invalid: {upstream} (must be 'stage-4', 'stage-5', or omitted)",
            )


def verify_progress_consistency(stage_dir: Path, test_plan: dict, results: dict) -> None:
    """Validate uat_progress.json (if present) matches the current test_plan and results."""
    progress_path = stage_dir / "uat_progress.json"
    if not progress_path.exists():
        return

    progress = load_json(progress_path)

    plan_ids = {t.get("id") for t in test_plan.get("test_cases", []) if t.get("id")}
    completed = set(progress.get("completed_test_ids", []) or [])
    failed = set(progress.get("failed_test_ids", []) or [])
    in_progress = progress.get("in_progress_test_id")

    overlap = completed & failed
    if overlap:
        raise StructureError(
            "Stage 8",
            f"uat_progress.json: test ids in both completed and failed: {sorted(overlap)}",
        )
    unknown = (completed | failed) - plan_ids
    if unknown:
        raise StructureError(
            "Stage 8",
            f"uat_progress.json references test ids not in test_plan.json: {sorted(unknown)}",
        )
    if in_progress is not None and in_progress not in plan_ids:
        raise StructureError(
            "Stage 8",
            f"uat_progress.json in_progress_test_id not in test_plan.json: {in_progress}",
        )

    result_ids = {r.get("test_id") for r in results.get("results", []) if r.get("test_id")}
    missing_results = (completed | failed) - result_ids
    if missing_results:
        raise GateError(
            "Stage 8",
            f"uat_progress.json marks tests complete but uat_results.json has no entry: {sorted(missing_results)}",
        )


def verify_coverage(artifacts_root: Path, test_plan: dict) -> None:
    stories_path = artifacts_root / "stage-4" / "stories.json"
    stories = load_json(stories_path)
    criteria = []
    for story in stories.get("stories", []):
        for item in story.get("acceptance_criteria", []) or []:
            if isinstance(item, str):
                criteria.append(item.strip())

    test_case_criteria = [t.get("criterion", "").strip() for t in test_plan.get("test_cases", [])]
    missing = [c for c in criteria if c and c not in test_case_criteria]
    if missing:
        raise GateError("Stage 8", f"Acceptance criteria missing from test_plan.json: {missing}")



def compute_gates(test_plan: dict, results: dict) -> tuple[str, str]:
    plan_by_id = {t.get("id"): t for t in test_plan.get("test_cases", []) if t.get("id")}
    automated_failed = []

    for entry in results.get("results", []):
        test_id = entry.get("test_id")
        status = entry.get("status")
        plan = plan_by_id.get(test_id, {})
        test_type = plan.get("type")
        priority = plan.get("priority", "P1")

        if test_type in ("unit", "browser") and priority == "P0" and status != "PASS":
            automated_failed.append(test_id)

    automated_gate = "PASSED" if not automated_failed else "FAILED"
    deployment_gate = "APPROVED" if automated_gate == "PASSED" else "BLOCKED"
    return automated_gate, deployment_gate


def main(stage_dir_path: str) -> None:
    stage_dir = Path(stage_dir_path).resolve()
    if not stage_dir.exists():
        raise StructureError("Stage 8", f"Stage 8 artifacts directory not found: {stage_dir}")

    results_path = stage_dir / "uat_results.json"
    test_plan_path = stage_dir / "test_plan.json"
    repo_root = stage_dir.parent.parent.parent
    artifacts_root = stage_dir.parent

    results = normalize_results(load_json(results_path))
    test_plan = load_json(test_plan_path)

    verify_app_health(stage_dir)
    verify_summary_consistency(results)
    verify_coverage(artifacts_root, test_plan)
    verify_bug_schema(results)
    verify_no_unfixed_critical_bugs(results)
    verify_evidence(stage_dir, repo_root, test_plan, results)
    verify_progress_consistency(stage_dir, test_plan, results)

    automated_gate, deployment_gate = compute_gates(test_plan, results)
    if results.get("automated_gate") and results.get("automated_gate") != automated_gate:
        raise StructureError("Stage 8", "automated_gate does not match computed result")
    if results.get("deployment_gate") and results.get("deployment_gate") != deployment_gate:
        raise StructureError("Stage 8", "deployment_gate does not match computed result")

    if deployment_gate != "APPROVED":
        raise GateError("Stage 8", "Deployment gate is BLOCKED")

    summary = results["execution_summary"]
    print(f"✅ Stage 8 verification PASSED — gate: APPROVED")
    print(f"   • {summary['passed']}/{summary['total']} tests passed")
    print(f"   • {summary.get('bugs_fixed', 0)} bug(s) found and fixed")
    if summary.get("skipped"):
        print(f"   • {summary['skipped']} test(s) skipped")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify/uat_gate.py <stage_8_artifacts_dir>")
        sys.exit(1)
    try:
        main(sys.argv[1])
        sys.exit(0)
    except (GateError, StructureError) as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
