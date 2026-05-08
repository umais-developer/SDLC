---
name: stage-8-uat
description: |
  Execute User Acceptance Testing — generate a test plan from story acceptance criteria,
  run all tests (unit, browser), and record structured results.
  Outputs test_plan.json, uat_results.json, and uat-results_final.md to .agents/artifacts/stage-8/.
  Can be invoked independently after Stage 7 Review is approved.
---

# Stage 8: User Acceptance Testing

You are a QA Engineer. Generate a complete test plan from story acceptance criteria, then execute every test case and record structured results with real evidence.

Human review is outside this pipeline; this stage is fully automated.

## Independent Invocation

To run this stage alone (requires Stage 1–7 artifacts and a running app):
```
Follow instructions in #file:.agents/skills/stage-8-uat/SKILL.md
```

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{stories_json}}` | Full contents of `.agents/artifacts/stage-4/stories.json` |
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` |
| `{{tech_stack_json}}` | Full contents of `.agents/artifacts/stage-2/tech_stack.json` |
| `{{tasks_json}}` | Full contents of `.agents/artifacts/stage-5/tasks.json` |
| `{{test_plan_json}}` | Full contents of `.agents/artifacts/stage-8/test_plan.json` (available after Step 1) |
| `{{app_url}}` | URL of the running app — start the dev server using `dev_command` or `start_command` from `tech_stack.json` if not running |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

---

## Request Sizing

**Before executing Step 0**, read the `size` field from `problem.json` (set by Stage 1). If the field is absent, **default to whatever size Stage 1 used**.

| Size | UAT depth |
|------|-----------|
| **Trivial** | Reuse Stage 6 unit test evidence + at least one browser test per user-facing FR (min 1). |
| **Medium** | Full automated suite + at least one browser test per flow in `flows.json` referenced by affected stories. |
| **Large** | Full automated suite + at least one browser test per flow in `flows.json`. |

---

> Shared conventions (size classification, anti-hallucination rule, traceability chain, pipeline leakage rule): see `.agents/skills/STAGE-CONVENTIONS.md`.

**Stage 8 specialization of the anti-hallucination rule:**
- Do not claim test execution without artifact evidence.
- Browser tests must cite Playwright artifacts (screenshot/video/trace).
- No human approvals are collected in this stage.

**Deployment gate computation:**
- The verifier computes `deployment_gate` from results and evidence. The model must not assert approval without evidence.

**Pipeline leakage rule:** do not reference Stage 9 or deployment work.

## Sub-agent Strategy

For projects with large test suites, use the parallel sub-agent strategy defined in:
`.agents/skills/stage-8-uat/prompts/subagent_strategy.md`

This partitions tests into independent groups that can run simultaneously.

## Execution Steps

### Step 0 — App Readiness
- Use `dev_command` or `start_command` from `tech_stack.json` to start the app if not running.
- Confirm the app is reachable at `{{app_url}}` (health check).
- Write evidence to `.agents/artifacts/stage-8/app_health.json`.
- If the app cannot be started or reached, **HALT** and report the missing or incorrect `app_url`/command.

`app_health.json` format:
```json
{
  "url": "http://localhost:5173",
  "started_at": "2026-05-08T10:12:00Z",
  "health_check_command": "curl -I http://localhost:5173",
  "exit_code": 0,
  "response_excerpt": "HTTP/1.1 200 OK"
}
```

### Step 1 — Test Plan Generation
- Load prompt: `.agents/skills/stage-8-uat/prompts/test_plan_generation.md`
- Substitute: `{{stories_json}}`, `{{problem_json}}`, `{{tasks_json}}`, `{{flows_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-8/test_plan.json`
- Compile `.agents/artifacts/stage-8/uat-test-plan_final.md` from `test_plan.json`

Coverage requirements:
- Every acceptance criterion in `stories.json` must map to a test case in `test_plan.json`.
- Every test case in `test_plan.json` must have a corresponding result in `uat_results.json`.

### Step 2 — Test Execution
- Load prompt: `.agents/skills/stage-8-uat/prompts/test_execution.md`
- Substitute: `{{test_plan_json}}`, `{{app_url}}`
- Execute:
  - Unit tests: if Stage 6 logs exist (e.g., `.agents/artifacts/stage-6/test.log`, `.agents/artifacts/stage-6/test.exit`), copy them into `.agents/artifacts/stage-8/unit/`; otherwise re-run `test_command` and write logs to `.agents/artifacts/stage-8/unit/`
  - Browser tests: Playwright with captured artifacts (screenshot/video/trace)
- Write output to: `.agents/artifacts/stage-8/uat_results.json`

### Step 3 — Verify Gate
```bash
python .agents/skills/stage-8-uat/verify/uat_gate.py .agents/artifacts/stage-8/
```
- Exit non-zero → **HALT** — output blocking issues, do not proceed to deploy
- Exit 0 → continue

### Step 4 — Compile Final Results Document
- Compile `uat_results.json` into `.agents/artifacts/stage-8/uat-results_final.md`
- Include: execution timestamp, summary table, per-test result rows, bugs list, gate decision

## Outputs

| Artifact | Path |
|---|---|
| Test plan | `.agents/artifacts/stage-8/test_plan.json` |
| Test plan document | `.agents/artifacts/stage-8/uat-test-plan_final.md` |
| Test results | `.agents/artifacts/stage-8/uat_results.json` |
| Final UAT document | `.agents/artifacts/stage-8/uat-results_final.md` |
| App health check | `.agents/artifacts/stage-8/app_health.json` |
| Playwright artifacts | `.agents/artifacts/stage-8/playwright/<test-id>/...` |
| Unit test evidence | `.agents/artifacts/stage-8/unit/test.log`, `.agents/artifacts/stage-8/unit/test.exit` |

## Gate

```bash
python .agents/skills/stage-8-uat/verify/uat_gate.py .agents/artifacts/stage-8/
```

**Pass criteria:** All P0 automated tests pass, no unfixed Critical bugs, computed `deployment_gate` is `APPROVED`, and summary counts are consistent.

Bug schema (for `uat_results.json`):
- `id`, `severity`, `title`, `description`, `related_test_id`, `evidence`, `steps_to_reproduce`, `root_cause`, `fix_applied`, `fix_verified`.
