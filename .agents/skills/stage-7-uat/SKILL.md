---
name: stage-7-uat
description: |
  Execute User Acceptance Testing — generate a test plan from story acceptance criteria,
  run all tests (unit, browser, manual), and record structured results.
  Outputs test_plan.json, uat_results.json, and uat-results_final.md to .agents/artifacts/stage-7.5/.
  Can be invoked independently after Stage 7 Review is approved.
---

# Stage 7 UAT: User Acceptance Testing

You are a QA Engineer. Generate a complete test plan from story acceptance criteria, then execute every test case and record structured results with real evidence.

## Independent Invocation

To run this stage alone (requires Stage 1–7 artifacts and a running app):
```
Follow instructions in #file:.agents/skills/stage-7-uat/SKILL.md
```

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{stories_json}}` | Full contents of `.agents/artifacts/stage-4/stories.json` |
| `{{test_plan_json}}` | Full contents of `.agents/artifacts/stage-7.5/test_plan.json` (available after Step 1) |
| `{{app_url}}` | URL of the running app — start the dev server using `build_command` from `tech_stack.json` if not running |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

## Sub-agent Strategy

For projects with large test suites, use the parallel sub-agent strategy defined in:
`.agents/skills/stage-7-uat/prompts/subagent_strategy.md`

This partitions tests into independent groups that can run simultaneously.

## Execution Steps

### Step 1 — Test Plan Generation
- Load prompt: `.agents/skills/stage-7-uat/prompts/test_plan_generation.md`
- Substitute: `{{stories_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-7.5/test_plan.json`
- Compile `.agents/artifacts/stage-7.5/uat-test-plan_final.md` from `test_plan.json`

### Step 2 — Test Execution
- Load prompt: `.agents/skills/stage-7-uat/prompts/test_execution.md`
- Substitute: `{{test_plan_json}}`, `{{app_url}}`
- Execute:
  - Unit tests: `npm test` (or equivalent from `tech_stack.json`)
  - Browser tests: Playwright
  - Manual tests: follow steps, record observations
- Write output to: `.agents/artifacts/stage-7.5/uat_results.json`

### Step 3 — Verify Gate
```bash
python .agents/skills/stage-7-uat/verify/uat_gate.py .agents/artifacts/stage-7.5/uat_results.json
```
- Exit non-zero → **HALT** — output blocking issues, do not proceed to deploy
- Exit 0 → continue

### Step 4 — Compile Final Results Document
- Compile `uat_results.json` into `.agents/artifacts/stage-7.5/uat-results_final.md`
- Include: execution timestamp, summary table, per-test result rows, bugs list, gate decision

## Outputs

| Artifact | Path |
|---|---|
| Test plan | `.agents/artifacts/stage-7.5/test_plan.json` |
| Test plan document | `.agents/artifacts/stage-7.5/uat-test-plan_final.md` |
| Test results | `.agents/artifacts/stage-7.5/uat_results.json` |
| Final UAT document | `.agents/artifacts/stage-7.5/uat-results_final.md` |

## Gate

```bash
python .agents/skills/stage-7-uat/verify/uat_gate.py .agents/artifacts/stage-7.5/uat_results.json
```

**Pass criteria:** All P0 tests pass, no unfixed Critical bugs, `deployment_gate` is `APPROVED`, summary counts are consistent.
