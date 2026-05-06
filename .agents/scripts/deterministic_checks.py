#!/usr/bin/env python3
"""Deterministic, non-LLM stage verification checks for SDLC artifacts.

Usage:
  python3 .agents/scripts/deterministic_checks.py --stage stage4 --artifact epics_stories_final.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List


STAGE_RULES: Dict[str, Dict[str, object]] = {
    "stage1": {
        "required_headings": [
            "## 2. Problem Statement",
            "## 3. Goals & Success Metrics",
            "## 6. Functional Requirements",
            "## 8. Scope",
        ],
    },
    "stage2": {
        "required_headings": [
            "## 4. Component Design",
            "## 5. Data Flow",
            "## 9. Security & Privacy Considerations",
            "## 10. Scalability & Performance",
        ],
    },
    "stage3": {
        "required_headings": [
            "## 4. User Flows",
            "## 6. States & Variations",
            "## 7. Accessibility Considerations",
        ],
    },
    "stage4": {
        "required_headings": [
            "## Epic 1",
            "### Stories",
            "**Acceptance Criteria:**",
            "## Traceability Matrix",
        ],
    },
    "stage5": {
        "required_headings": [
            "## Acceptance Criteria",
            "## Implementation Tasks",
            "## Task Dependency Order",
            "### Testing",
        ],
    },
    "stage7": {
        "required_headings": [
            "## Findings",
            "### 🔴 Blockers",
            "### 🟠 Major Issues",
            "**Verdict:**",
        ],
    },
    "stage7.5": {
        "required_headings": [
            "## Summary",
            "## Test Results by Epic",
            "## Deployment Gate Status",
        ],
    },
}


def _has_heading(text: str, heading: str) -> bool:
    return heading.lower() in text.lower()


def _check_story_format(text: str) -> bool:
    pattern = re.compile(
        r"\*\*As a\*\*\s+.+?,\s+\*\*I want\*\*\s+.+?\s+\*\*so that\*\*\s+.+?\.",
        flags=re.IGNORECASE | re.DOTALL,
    )
    return bool(pattern.search(text))


def _check_acceptance_checklists(text: str) -> bool:
    return bool(re.search(r"\*\*Acceptance Criteria:\*\*[\s\S]*?- \[ \]", text, flags=re.IGNORECASE))


def _check_traceability_matrix(text: str) -> bool:
    if "## Traceability Matrix".lower() not in text.lower():
        return False
    # Expect header + separator + at least one data row
    rows = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    matrix_rows = [r for r in rows if "Story ID" in r or re.match(r"\|\s*\d+\.\d+\s*\|", r)]
    return len(matrix_rows) >= 2


def run_checks(stage: str, artifact: Path) -> Dict[str, object]:
    failures: List[str] = []
    checks: List[str] = []

    if not artifact.exists():
        failures.append(f"Artifact not found: {artifact}")
        return {"passed": False, "checks": checks, "failures": failures}

    text = artifact.read_text(encoding="utf-8", errors="replace")

    if not text.strip():
        failures.append("Artifact is empty")

    rules = STAGE_RULES.get(stage)
    if rules is None:
        failures.append(f"Unknown stage: {stage}")
        return {"passed": False, "checks": checks, "failures": failures}

    for heading in rules.get("required_headings", []):
        if _has_heading(text, str(heading)):
            checks.append(f"Heading present: {heading}")
        else:
            failures.append(f"Missing heading: {heading}")

    if stage == "stage4":
        if _check_story_format(text):
            checks.append("User story format found")
        else:
            failures.append("No valid user story format found")

        if _check_acceptance_checklists(text):
            checks.append("Acceptance criteria checklist found")
        else:
            failures.append("Acceptance criteria checklists missing")

        if _check_traceability_matrix(text):
            checks.append("Traceability matrix with at least one story mapping found")
        else:
            failures.append("Traceability matrix missing or incomplete")

    return {"passed": not failures, "checks": checks, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic stage verification checks.")
    parser.add_argument("--stage", required=True, help="Stage id, for example: stage1, stage4, stage7.5")
    parser.add_argument("--artifact", required=True, help="Path to artifact file")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output")
    args = parser.parse_args()

    result = run_checks(args.stage.strip().lower(), Path(args.artifact))

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"Deterministic checks: {status}")
        for item in result["checks"]:
            print(f"  + {item}")
        for item in result["failures"]:
            print(f"  - {item}")

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
