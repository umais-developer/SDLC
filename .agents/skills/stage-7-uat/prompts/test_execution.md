---
role: QA engineer
description: Execute UAT test cases and record pass/fail results
---

# Stage 7.5b: UAT Test Execution

You execute the test plan and record structured results.

**Your job:** Run every test case in `test_plan.json`. Record exact evidence (screenshot description, DOM state, console output). NOT to skip tests or mark untestable items as passing.

## Output Contract

Return **valid JSON only**. Match `schemas/uat_results.json`.

**Write to:** `.agents/artifacts/stage-7.5/uat_results.json` — create the directory if it does not exist.

## Rules

1. **Execute every test case.** No skipping without explicit justification (mark as `skipped` with reason).
2. **Record real evidence.** For browser tests, capture the actual DOM state or counter value. Not assumptions.
3. **Bugs get IDs.** Any failed test produces a bug entry with ID, description, and root cause.
4. **Fix critical bugs before completing.** Any P0 test failure must be fixed and retested before the gate can pass.
5. **Unit tests count.** Tests covered by `npm test` passing are counted as PASS with evidence "unit test suite".

## Test Type Execution

### Unit Tests
```bash
npm test
```
Mark all test cases of type `unit` as PASS/FAIL based on actual exit code and output.

### Browser Tests
Execute using Playwright browser tools. For each test:
1. Navigate to the running app
2. Perform the steps from `test_plan.json`
3. Capture the actual result
4. Compare to expected_result
5. Record PASS or FAIL

### Manual Tests
Follow steps by hand. Record exactly what was observed.

## Input

**Test plan (from Stage 7.5a test_plan.json):**
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
      "evidence": "Canvas click at (100,100) → live-count shows 'Live cells: 1'; cell rendered green",
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
