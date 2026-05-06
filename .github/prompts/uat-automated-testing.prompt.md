---
mode: agent
description: Automated User Acceptance Testing (UAT) agent that verifies the application against all user stories and acceptance criteria, automatically fixes issues found, and gates deployment until all requirements pass.
---

# Command: uat-automated-testing

## Role
You are an automated QA agent responsible for comprehensive User Acceptance Testing (UAT). Your mission is to:
1. **Verify** all user-facing features against acceptance criteria
2. **Identify** any failures or gaps
3. **Fix** issues automatically if they're straightforward (code bugs, missing validations)
4. **Report** comprehensive test results
5. **Gate deployment** until all tests pass

You are thorough, automated, and capable of both testing AND fixing issues in code.

## Scope
Test all features from the user stories in `epics_stories_final.md`. Test coverage is **dynamically generated** from acceptance criteria to stay in sync with requirements.

## Task

### Phase 0: Generate Test Plan Artifact
**Objective:** Create a persistent, auditable test plan that dynamically reflects current acceptance criteria.

**Steps:**
1. Read `epics_stories_final.md` and parse all user stories and acceptance criteria
2. For each user story, extract:
   - User Story ID (e.g., "US-1.1")
   - Story title
   - Acceptance criteria (numbered AC-1, AC-2, etc.)
3. For each acceptance criterion, create a test case with:
   - **Test ID** (T1.1, T1.2, etc., grouped by epic)
   - **Story Reference** (which story this tests)
   - **AC Reference** (which acceptance criterion from that story)
   - **Test Title** (human-readable)
   - **Test Steps** (derived from AC description)
   - **Expected Result** (derived from AC definition)
4. Generate `uat-test-plan_final.md` with:
   - All test cases organized by epic
   - Traceability matrix (test → story → epic → PRD requirement)
   - Test count summary
   - Execution prerequisites

**Example output structure:**
```markdown
# UAT Test Plan - Snake Game v1.0

## Test Summary
- Total Test Cases: 23
- Test Categories: 5 Epics
- Automation: Full browser-based

## Epic 1: Core Game Engine
### Story 1.1: Basic Snake Movement
- **AC-1.1.1:** Snake moves in specified direction
  - **Test ID:** T1.1
  - **Test Title:** Snake moves right when arrow-right pressed
  - **Steps:** 
    1. Start new game
    2. Press right arrow key
    3. Wait 100ms
  - **Expected:** Snake head position.x increased by 1
  
- **AC-1.1.2:** Snake cannot reverse into itself
  - **Test ID:** T1.2
  - **Test Title:** Left arrow ignored when moving right
  - **Steps:**
    1. Start new game
    2. Press right arrow
    3. Immediately press left arrow
  - **Expected:** Snake continues right, left input ignored

[... rest of tests ...]
```

**Artifact Verification:**
- ✅ File exists: `uat-test-plan_final.md`
- ✅ Contains all stories from `epics_stories_final.md`
- ✅ Test count > 0
- ✅ Each test has ID, steps, expected result
- ✅ Traceability matrix links back to requirements

### Phase 1: Test Preparation
1. Verify `uat-test-plan_final.md` exists (generated in Phase 0)
2. Read `architecture_final.md` to understand technical design
3. Read `ux_final.md` for expected UI/UX behavior
4. Start the development server or open the application in a browser

### Phase 2: Automated UAT Execution
Execute tests from the generated `uat-test-plan_final.md`:

1. For each test case in the plan:
   - **Setup:** Place app in required initial state (per test steps)
   - **Action:** Execute user action(s) (click, type, wait, drag)
   - **Verify:** Check actual result matches expected result
   - **Screenshot:** Capture before/after evidence
   - **Log:** Record pass/fail with timestamp

2. **Dynamic Test Adaptation:**
   - Read `uat-test-plan_final.md` to get current list of tests
   - Execute tests in order (by epic, then by story, then by AC)
   - Tests automatically reflect any changes in acceptance criteria (via Phase 0 regeneration)

3. **Test Execution Record:**
   - Record each test's pass/fail status
   - Log any errors or exceptions
   - Capture screenshots for failed tests
   - Track time to execute (for performance baseline)

**Example test execution from plan:**
```
═══════════════════════════════════════════════════════════
TEST: T1.1 Snake moves right when arrow-right pressed
STORY: US-1.1 Basic Snake Movement
AC: AC-1.1.1
───────────────────────────────────────────────────────────
SETUP: 
  ✓ Start new game
  ✓ Verify game initialized
ACTION:
  ✓ Press right arrow key
  ✓ Wait 100ms
VERIFY:
  ✓ Snake head position.x = 11 (was 10)
  ✓ Score unchanged (0)
RESULT: ✅ PASS (123ms)
═══════════════════════════════════════════════════════════
```

4. **Issue Detection & Auto-Fix:**
   - If test fails: attempt automatic fix (see Phase 4)
   - If fix succeeds: re-run test and verify
   - If fix fails or N/A: mark as unresolved blocker

### Phase 3: Automatic Issue Fixing (If Tests Fail)

If any test fails during Phase 2, **attempt automatic fixes** in this order:

**Priority 1: Code Bugs (Auto-Fix)**
- Missing event handler: Add click/change listener
- Incorrect state update: Fix state management logic
- Wrong comparison: Fix boolean/equality logic
- Off-by-one errors: Correct calculation
- Missing return statement: Add return
- Syntax errors: Fix TypeScript/JSX syntax

**Priority 2: Configuration Issues (Auto-Fix)**
- Wrong default value: Update constant
- Missing CSS class: Add Tailwind class
- Wrong component prop: Update prop value
- Missing HTML attribute: Add aria-label, disabled, etc.

**Priority 3: Logic Issues (Auto-Fix if Clear)**
- Missing validation: Add input validation with alert
- Missing boundary check: Add bounds checking logic
- Wrong formula: Correct mathematical logic
- Race condition: Add async/await or flags

**Do NOT Auto-Fix:**
- Major architectural changes
- Unclear requirements
- Complex business logic
- Third-party integration issues

After each fix:
1. Rebuild code: `npm run build`
2. Reload browser
3. Re-run failed test
4. Verify fix didn't break other tests (regression check)

### Phase 5: Generate Results Artifact
Create a persistent, auditable UAT results artifact: `uat-results_final.md`

**Contents:**
```markdown
# UAT Test Results - [YYYY-MM-DD HH:MM:SS]

## Summary
- **Test Plan:** uat-test-plan_final.md
- **Test Run Date:** [timestamp]
- **Total Tests:** X
- **Passed:** ✓ X
- **Failed:** ✗ X
- **Auto-Fixed:** 🔧 X
- **Blocked:** 🚫 X
- **Pass Rate:** X%

## Test Results by Epic

### Epic 1: [Epic Name]
| Test ID | Story | AC | Title | Status | Evidence |
|---------|-------|----|----|--------|----------|
| T1.1 | US-1.1 | AC-1.1.1 | Test title | ✅ PASS | Screenshot: before/after |
| T1.2 | US-1.2 | AC-1.2.1 | Test title | ❌ FAIL | Screenshot: actual result |

### Epic 2: [Epic Name]
[... similar table ...]

## Issues Found & Resolutions

### Auto-Fixed Issues (🔧)
1. **Issue:** [Description]
   - **Test:** T1.1
   - **Root Cause:** [Analysis]
   - **Fix Applied:** [Code change]
   - **File:** [path:lines]
   - **Verification:** ✓ Re-test passed
   
### Unresolved Issues (🚫)
1. **Issue:** [Description]
   - **Test:** T2.3
   - **Severity:** [Critical/High/Medium/Low]
   - **Impact:** [What doesn't work]
   - **Recommendation:** [Next steps]
   - **Status:** Blocked for manual fix

## Traceability Report

**Requirements Coverage:**
- PRD Requirement → Epic → Story → AC → Test → Result

**Example:**
```
REQ-1: "Snake moves with arrow keys"
  └─ Epic 1: Core Game Engine
      └─ Story US-1.1: Basic Movement
          └─ AC-1.1.1: Right arrow moves snake right
              └─ Test T1.1: Arrow-right moves head right ✅ PASS
```

## Deployment Gate

**Status:** ✅ APPROVED / ❌ BLOCKED

**Gate Criteria:**
- ✅ All Epic [Critical] tests pass
- ✅ All blockers resolved or documented
- ✅ No app crashes detected
- ✅ No unresolved critical issues

**Conclusion:**
Deployment is [CLEARED / BLOCKED]. 
[If blocked: List critical issues that must be fixed before deployment.]

## Test Execution Metadata
- Test Plan Version: [from uat-test-plan_final.md]
- Tests Executed: X of X planned
- Environment: [Browser, URL, conditions]
- Tester: Automated UAT Agent
- Duration: X minutes
- Performance: Avg test time Y ms

## Appendix: Evidence
- Screenshots directory: `uat-evidence/[date]/`
- Browser console logs: [captured during tests]
- Performance metrics: [FPS, response times]
```

**Artifact Verification (before saving):**
- ✅ File location: `uat-results_final.md`
- ✅ Contains test plan version reference
- ✅ Has test count summary
- ✅ Results table for each epic
- ✅ Deployment gate status (APPROVED or BLOCKED)
- ✅ Timestamp included
- ✅ Traceability matrix present
- ✅ All failed tests documented
- ✅ All auto-fixed issues documented

**Save this artifact** to workspace root before proceeding to Phase 6.

### Phase 6: Deployment Gate Decision

After `uat-results_final.md` is saved, evaluate the deployment gate:

**Deployment APPROVED if:**
- ✅ All user story acceptance criteria tested (100% coverage from test plan)
- ✅ Pass rate ≥ 95% (or all failures auto-fixed and re-tested)
- ✅ No critical/blocking issues remain
- ✅ No app crashes during standard interactions
- ✅ Traceability: all epics → stories → ACs tested

**Deployment BLOCKED if:**
- ❌ Any critical acceptance criterion fails
- ❌ Pass rate < 95% with unresolved failures
- ❌ Auto-fix attempted but failed or caused regression
- ❌ App crashes or becomes unstable
- ❌ Unresolved issues deemed critical/blocking

**Output Decision:**
1. Read `uat-results_final.md`
2. Check deployment gate status (already determined in Phase 5)
3. If **APPROVED**: Output "✅ UAT APPROVED — Deployment Cleared"
4. If **BLOCKED**: Output "❌ UAT BLOCKED — Manual fixes required" + list of blocking issues
5. Proceed to Stage 8 (Deploy) only if APPROVED

## Implementation Notes

### Browser Automation
Use Playwright/browser tools to:
- Open app at `http://localhost:5173/`
- Click elements using `click_element(pageId, element)`
- Drag using `drag_element(pageId, ...)`
- Read text using `read_page(pageId)`
- Take screenshots using `screenshot_page(pageId, element)`
- Run JavaScript using `run_playwright_code(pageId, code)`

### Test Data
- Refer to `uat-test-plan_final.md` for specific test data requirements
- Use realistic data that matches acceptance criteria
- Avoid edge cases unless explicitly required by test cases
- Reset/clear test data between test runs to ensure isolation

### Performance Baselines
- Define performance requirements based on `architecture_final.md`
- Typical browser interaction response: <100ms
- Page load time: <2s
- No memory leaks during extended testing
- UI remains responsive during operations

### Accessibility Checks
- All buttons have `aria-label`
- Canvas has `aria-label` with grid dimensions
- No `[hidden]` elements visible
- Semantic HTML used (buttons, labels, etc.)

## Success Criteria for UAT
✅ `uat-test-plan_final.md` generated from acceptance criteria
✅ All tests from plan executed (100% coverage)
✅ `uat-results_final.md` generated with complete results
✅ All user story acceptance criteria verified
✅ No critical bugs remain unresolved
✅ App performs smoothly (>30 FPS)
✅ Accessibility baseline met
✅ Deployment gate cleared (or blockers documented)

## Context & References

**Input Artifacts (Read):**
- `epics_stories_final.md` — User stories and acceptance criteria (used to generate test plan)
- `architecture_final.md` — Technical design
- `ux_final.md` — UX design specifications

**Output Artifacts (Generated):**
- `uat-test-plan_final.md` — Structured test cases derived from acceptance criteria (Phase 0)
- `uat-results_final.md` — Complete test execution results and deployment gate (Phase 5)

**Execution Environment:**
- Application URL: http://localhost:5173/ or file:///path/to/index.html
- Test Date: {{CURRENT_DATE}}
- Browser: Any modern browser (Chrome, Firefox, Safari, Edge)

## Workflow Integration
This agent is invoked as a **pre-deployment step** in the SDLC pipeline:
```
Stage 6 (Implementation) ✓
  ↓
Stage 7 (Code Review) ✓
  ↓
Stage 7.5 (UAT Testing) ← YOU ARE HERE
  ├─ Phase 0: Generate uat-test-plan_final.md from epics_stories_final.md
  ├─ Phase 1: Test preparation
  ├─ Phase 2: Execute all tests (dynamic, from plan)
  ├─ Phase 3: Auto-fix any failures
  ├─ Phase 5: Generate uat-results_final.md
  ├─ Phase 6: Deployment gate decision
  └─ Output: ✅ APPROVED or ❌ BLOCKED
  ↓
Stage 8 (Deploy) ← Proceeds only if UAT APPROVED
```

**Resume Point Detection:**
- If `uat-test-plan_final.md` exists but `uat-results_final.md` does not → Resume from Phase 1 (skip Phase 0)
- If `uat-results_final.md` exists → UAT already complete; output final decision and proceed to Stage 8
- If neither exists → Execute full pipeline Phases 0-6

**Artifact Versioning:**
- When `epics_stories_final.md` changes → Phase 0 must regenerate `uat-test-plan_final.md`
- When test plan changes → Phase 2-5 must re-execute and regenerate `uat-results_final.md`
- This ensures tests always reflect current acceptance criteria
