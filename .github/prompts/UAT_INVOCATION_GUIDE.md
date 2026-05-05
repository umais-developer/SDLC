# UAT Automated Testing - Agent Invocation Guide

## Overview
This document explains how to invoke the `uat-automated-testing` agent to perform comprehensive User Acceptance Testing before deployment.

## Quick Start

### Manual Invocation (Local Development)
```bash
# Start the development server
npm run dev

# Open VS Code chat and use the slash command:
/uat-automated-testing

# The agent will:
# 1. Test all user stories (30+ tests)
# 2. Auto-fix any issues found
# 3. Generate a comprehensive report
# 4. Gate deployment based on results
```

### CI/CD Invocation (Pre-Deployment)
The `uat-automated-testing` agent is automatically invoked as part of the Stage 8 deployment pipeline:
```
Code Push → Build → Unit Tests → [UAT Agent] → Deploy
```

## What the Agent Tests

### Epic 1: Simulation Engine (4 tests)
- Cell death with 0 neighbors
- Blinker oscillation (period 2)
- UI responsiveness during simulation
- Performance with large grids

### Epic 2: Grid UI (5 tests)
- Grid displays at 50×50 default
- Single cell click toggle
- Drag-to-draw multiple cells
- Grid updates with generation
- Empty state message shown

### Epic 3: Playback Controls (5 tests)
- Play button starts simulation
- Pause button freezes
- Step button advances 1 generation
- Speed slider adjusts 1-10 gen/sec
- Clear button resets grid

### Epic 4: Pattern Library (3 tests)
- Patterns visible in library
- Pattern selection shows preview
- Placement bounds validation

### Epic 5: Grid Resize (3 tests)
- Resize modal opens with current dims
- Valid resize works
- Invalid input validation

### Accessibility & Error Handling (3 tests)
- ARIA labels on controls
- Page structure correct
- Error boundary catches errors

**Total: 23 mandatory tests**

## Test Execution Flow

```
┌─────────────────────────────────────┐
│ 1. START DEV SERVER                 │
│    npm run dev                      │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 2. OPEN BROWSER                     │
│    http://localhost:5173/           │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 3. RUN ALL TESTS (23+ tests)        │
│    - T1.1 through T5.3              │
│    - Accessibility checks           │
│    - Error handling tests           │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 4. TEST FAILURES FOUND?             │
│    ├─ YES: Auto-fix attempt         │
│    └─ NO: Proceed                   │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 5. AUTO-FIX ISSUES                  │
│    - Code bugs                      │
│    - Config issues                  │
│    - Logic errors                   │
│    - Re-test after each fix         │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 6. REPORT RESULTS                   │
│    - Test summary (X/Y passed)      │
│    - Issues fixed (if any)          │
│    - Blockers identified (if any)   │
│    - Deployment gate status         │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│ 7. DEPLOYMENT DECISION              │
│    ├─ ALL PASS: Deploy ✓            │
│    └─ FAILS: Block & Report ✗       │
└─────────────────────────────────────┘
```

## Test Categories

### Critical Tests (Must Pass for Deployment)
- Epic 1 tests (simulation correctness)
- Epic 3 tests (play/pause/step functionality)
- Grid rendering and interaction
- Error boundary

### Important Tests (Should Pass)
- Epic 2 tests (UI interactions)
- Epic 4 tests (pattern library)
- Epic 5 tests (grid resize)

### Accessibility Tests (Baseline)
- ARIA labels present
- Page structure semantic
- No major accessibility violations

## Auto-Fix Capabilities

The agent automatically fixes these issue types:

✅ **Auto-Fixed:**
- Missing event handlers
- Incorrect state logic
- Wrong default values
- CSS class issues
- Missing ARIA labels
- Simple syntax errors
- Input validation gaps
- Boundary checking

❌ **Not Auto-Fixed:**
- Major architectural changes
- Unclear requirements
- Complex business logic
- Third-party integration issues

## Troubleshooting

### Test Fails to Execute
**Symptom:** Agent can't click elements or load page
**Solution:**
1. Verify dev server running: `npm run dev`
2. Check localhost:5173 is accessible
3. Clear browser cache
4. Re-invoke agent

### Test Passes Locally but Fails in CI
**Symptom:** Works on local but CI shows failure
**Solution:**
1. CI environment might be headless
2. Timing issues (add page.waitForTimeout)
3. Asset loading delays
4. Browser version differences

### Fix Attempt Breaks Other Tests
**Symptom:** Fix passes one test but breaks another
**Solution:**
1. Agent runs regression check after each fix
2. If regression detected, fix is rolled back
3. Issue marked as "needs manual review"
4. Deployment blocked until resolved

## Report Interpretation

### Perfect Run (All Pass)
```
✓ Summary: 23/23 tests passed
✓ Issues fixed: 0
✓ Deployment gate: CLEARED
```
→ **Action:** Proceed with deployment

### Issues Found & Fixed
```
✓ Summary: 22/23 tests passed (1 fixed)
✓ Issues fixed: 1 (Play/Pause button state)
✓ Deployment gate: CLEARED
```
→ **Action:** Proceed with deployment (issues auto-fixed)

### Blocker Found
```
✗ Summary: 20/23 tests passed
✗ Issues fixed: 0
✗ Blocker: T3.1 Play button doesn't start simulation
✗ Deployment gate: BLOCKED
```
→ **Action:** Fix manually, then re-invoke UAT agent

## Integration with Deployment Pipeline

### GitHub Actions Workflow
The UAT agent runs as part of `.github/workflows/deploy.yml`:

```yaml
jobs:
  build:
    # ... build steps ...
    
  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Run unit tests
        run: npm test
      
      - name: Run UAT tests (via agent)
        # Agent invoked automatically
        # Tests 30+ user story acceptance criteria
        # Auto-fixes issues if found
        # Gates deployment on results
```

## Best Practices

### Before Committing Code
1. Run UAT locally: `/uat-automated-testing`
2. Review report for failures
3. Auto-fixed issues are committed
4. Push with confidence

### In CI/CD Pipeline
1. UAT runs automatically after build
2. If UAT passes: deployment proceeds
3. If UAT fails: CI blocks, sends report
4. Developer reviews and fixes
5. Re-push to trigger new UAT run

### For Quick Iteration
1. Make code change
2. Run `/uat-automated-testing` 
3. Review report
4. Let agent auto-fix if applicable
5. Commit fixed code
6. Repeat for next change

## Monitoring & Metrics

### Test Pass Rate Tracking
- Target: 100% pass rate
- Alert if <95% pass rate
- Trend analysis over time

### Auto-Fix Rate
- Track fixes per run
- Monitor fix types
- Identify systematic issues

### Performance Metrics
- Generation computation time
- UI response time
- Grid render performance

## Slack/Email Alerts

When UAT completes:
- ✅ **All Pass:** Green status, deployment proceeds
- ⚠️ **Issues Fixed:** Yellow status, auto-fixes applied, deploy proceeds
- ❌ **Blocker:** Red status, deployment blocked, review required

## References

- Agent Definition: `.github/prompts/uat-automated-testing.prompt.md`
- User Stories: `epics_stories_final.md`
- Architecture: `architecture_final.md`
- UX Design: `ux_final.md`
- Workflow: `.github/workflows/deploy.yml`

## Contact & Support

For issues with UAT:
1. Check test logs in agent output
2. Review failed test's acceptance criteria
3. Examine screenshots captured during test
4. Check browser console errors
5. File issue with reproduction steps

---

**Status:** UAT agent integrated into deployment pipeline  
**Last Updated:** May 5, 2026
