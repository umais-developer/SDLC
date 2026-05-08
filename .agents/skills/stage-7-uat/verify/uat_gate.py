#!/usr/bin/env python3
"""
Verification script for Stage 7.5 (UAT): Deployment Gate

Validates uat_results.json — checks that all P0 tests passed,
no unfixed Critical bugs exist, and the deployment_gate is APPROVED.

Exit code: 0 = APPROVED, 1 = BLOCKED or error
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exceptions import GateError, StructureError


def load(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StructureError("Stage 7.5", f"Invalid JSON in {path}: {e}")
    except FileNotFoundError:
        raise StructureError("Stage 7.5", f"File not found: {path}")


def verify_gate(results: dict) -> None:
    gate = results.get("deployment_gate", "")
    if gate not in ("APPROVED", "BLOCKED"):
        raise StructureError(
            "Stage 7.5",
            f"deployment_gate must be 'APPROVED' or 'BLOCKED', got: '{gate}'"
        )
    if gate == "BLOCKED":
        reason = results.get("gate_reason", "no reason given")
        raise GateError("Stage 7.5", f"Deployment gate is BLOCKED: {reason}")


def verify_no_failed_p0(results: dict) -> None:
    """Fail if any result is FAIL — P0 failures must be fixed before gate passes."""
    failed = [
        r["test_id"]
        for r in results.get("results", [])
        if r.get("status") == "FAIL"
    ]
    if failed:
        raise GateError(
            "Stage 7.5",
            f"The following test cases failed and must be fixed: {failed}"
        )


def verify_no_unfixed_critical_bugs(results: dict) -> None:
    unfixed = [
        b["id"]
        for b in results.get("bugs", [])
        if b.get("severity") == "Critical" and not b.get("fix_verified", False)
    ]
    if unfixed:
        raise GateError(
            "Stage 7.5",
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
            "Stage 7.5",
            f"Summary inconsistency: passed({passed}) + failed({failed}) + skipped({skipped}) "
            f"= {passed+failed+skipped}, but total = {total}"
        )
    if actual_results != total:
        raise StructureError(
            "Stage 7.5",
            f"results[] has {actual_results} entries but execution_summary.total = {total}"
        )


def main(results_json_path: str) -> None:
    results = load(results_json_path)

    verify_summary_consistency(results)
    verify_no_failed_p0(results)
    verify_no_unfixed_critical_bugs(results)
    verify_gate(results)

    summary = results["execution_summary"]
    print(f"✅ Stage 7.5 verification PASSED — gate: APPROVED")
    print(f"   • {summary['passed']}/{summary['total']} tests passed")
    print(f"   • {summary.get('bugs_fixed', 0)} bug(s) found and fixed")
    if summary.get("skipped"):
        print(f"   • {summary['skipped']} test(s) skipped")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify/uat_gate.py <uat_results.json>")
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
