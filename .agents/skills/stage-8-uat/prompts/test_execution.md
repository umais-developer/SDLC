---
role: QA engineer
description: Execute UAT test cases and record pass/fail results
---

# Stage 8b: UAT Test Execution

You execute the test plan and record structured results.

**Your job:** Run every test case in `test_plan.json`. Record exact evidence (screenshot description, DOM state, console output). NOT to skip tests or mark untestable items as passing.

## Output Contract

Return **valid JSON only**. Match `schemas/uat_results.json`.

**Write to:** `.agents/artifacts/stage-8/uat_results.json` — create the directory if it does not exist.

## Rules

1. **Execute every test case.** No skipping without explicit justification (mark as `skipped` with reason).
2. **Record real evidence.** For browser tests, capture Playwright artifacts (screenshot/video/trace).
3. **Bugs get IDs.** Any failed test produces a bug entry with ID, description, and root cause.
4. **Fix critical bugs before completing.** Any P0 test failure must be fixed and retested before the gate can pass.
5. **Unit tests count.** If Stage 6 logs exist (e.g., `.agents/artifacts/stage-6/test.log` and `.agents/artifacts/stage-6/test.exit`), copy them into `.agents/artifacts/stage-8/unit/` and cite those paths; otherwise re-run `test_command` and write logs to `.agents/artifacts/stage-8/unit/`.
6. **Gates are derived.** Set `automated_gate` and `deployment_gate` based on results; do not assert approval without evidence.
7. **Bug schema.** Every bug entry must include all required fields.

## Test Type Execution

### Unit Tests
```bash
<test_command>
```
Mark all test cases of type `unit` as PASS/FAIL based on actual exit code and output. Capture logs to `.agents/artifacts/stage-8/unit/test.log` and exit code to `.agents/artifacts/stage-8/unit/test.exit`.

### Browser Tests
Execute using Playwright browser tools. For each test:
1. Navigate to the running app
2. Perform the steps from `test_plan.json`
3. Capture the actual result
4. Compare to expected_result
5. Record PASS or FAIL with artifact paths

## Input

**Test plan (from Stage 8a test_plan.json):**
```
{{test_plan_json}}
```

**Running app URL:**
```
{{app_url}}
```

## Output Format

```json
{
  "execution_summary": {
    "total": 40,
    "passed": 38,
    "failed": 0,
    "skipped": 2,
    "bugs_found": 1,
    "bugs_fixed": 1
  },

  "results": [
    {
      "test_id": "T1.1.1",
      "story": "S-1.1",
      "status": "PASS | FAIL | SKIPPED",
      "evidence": {
        "notes": "Canvas click at (100,100) → live-count shows 'Live cells: 1'",
        "artifacts": [
          ".agents/artifacts/stage-8/playwright/T1.1.1/screenshot.png",
          ".agents/artifacts/stage-8/playwright/T1.1.1/trace.zip"
        ]
      },
      "bug_id": null
    },
    {
      "test_id": "T1.1.2",
      "story": "S-1.1",
      "status": "PASS",
      "evidence": {
        "notes": "Unit test suite passed",
        "artifacts": [
          ".agents/artifacts/stage-8/unit/test.log",
          ".agents/artifacts/stage-8/unit/test.exit"
        ]
      },
      "bug_id": null
    },
    {
      "test_id": "T2.1.4",
      "story": "S-2.1",
      "status": "FAIL",
      "evidence": "Step button remains disabled after canvas click; live-count shows 'Live cells: 1' but button.disabled=true",
      "bug_id": "B-02"
    }
  ],

  "bugs": [
    {
      "id": "B-02",
      "severity": "Critical",
      "title": "Step button disabled after canvas click on empty grid",
      "description": "updatePlayButtonDisabled() is not called in handleDraw(); button state stale after canvas click",
      "related_test_id": "T2.1.4",
      "evidence": ".agents/artifacts/stage-8/playwright/T2.1.4/screenshot.png",
      "steps_to_reproduce": [
        "Load app (empty grid)",
        "Click a canvas cell",
        "Observe Step button — still disabled despite live-count = 1"
      ],
      "root_cause": "UIController.handleDraw() does not call updatePlayButtonDisabled(); called only in onPointerUp()",
      "fix_applied": "Added updatePlayButtonDisabled() call at end of handleDraw()",
      "fix_verified": true,
      "fixed_in_test": "T2.1.4 re-run → PASS"
    }
  ],

  "automated_gate": "PASSED | FAILED",
  "deployment_gate": "APPROVED | BLOCKED",
  "gate_reason": "All P0 tests pass. 2 P1 tests skipped (file export — covered by unit tests)."
}
```

## Gate Rules

| Condition | Gate |
|---|---|
| All P0 tests PASS | `APPROVED` |
| Any P0 test FAIL (unfixed) | `BLOCKED` |
| P1/P2 tests FAIL | `APPROVED` (document in gate_reason) |
| Any unfixed Critical bug | `BLOCKED` |
