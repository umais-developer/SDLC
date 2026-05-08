#!/usr/bin/env python3
"""
Verification script for Stage 7 (Code Review): Review Verdict

Validates review.json — ensures verdict is valid, Critical/High findings
block approval, and must_fix list is consistent with verdict.

Exit code: 0 = APPROVE, 1 = CHANGES_REQUIRED or error
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
        if not must_fix:
            raise StructureError(
                "Stage 7",
                "verdict is CHANGES_REQUIRED but must_fix_before_proceeding is empty"
            )


def verify_findings_complete(review: dict) -> None:
    for finding in review.get("findings", []):
        if not finding.get("fix"):
            raise StructureError(
                "Stage 7",
                f"Finding {finding.get('id')} has no 'fix' specified"
            )
        if not finding.get("file"):
            raise StructureError(
                "Stage 7",
                f"Finding {finding.get('id')} has no 'file' specified"
            )


def main(review_json_path: str) -> None:
    review = load(review_json_path)

    verify_verdict(review)
    verify_findings_complete(review)
    verify_verdict_consistency(review)

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
        print("Usage: python verify/code_review_verdict.py <review.json>")
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
