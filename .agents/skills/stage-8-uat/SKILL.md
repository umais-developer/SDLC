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

Requires Stage 1–7 artifacts and a running app. Pick the form that matches your environment:

- **Claude Code:** `/stage-8`
- **GitHub Copilot:** `Follow instructions in #file:.agents/skills/stage-8-uat/SKILL.md`
- **Other agents:** Read this file and follow it.

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{stories_json}}` | Full contents of `.agents/artifacts/stage-4/stories.json` |
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` |
| `{{flows_json}}` | Full contents of `.agents/artifacts/stage-3/flows.json` |
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
| **Trivial** | Reuse Stage 6 unit test evidence + at least one P0 browser test per user-facing FR (min 1). |
| **Medium** | Full automated suite + at least one P0 browser test per flow in `flows.json` referenced by affected stories. |
| **Large** | Full automated suite + at least one P0 browser test per flow in `flows.json`. |

> **Browser tests are no longer optional for Medium/Large.** The verifier
> (`verify_browser_coverage_per_flow`) refuses to APPROVE the deployment gate
> unless every user-facing flow has a P0 browser test that links to it via
> `links_to_flow: ["<FLOW-X>"]`, AND that test produces real pixel/video/trace
> evidence (screenshot, video, or Playwright trace zip). A `.log` file is **not**
> sufficient evidence for a browser test.

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

### Step 1a — Resume Check
Before starting Step 2, look for `.agents/artifacts/stage-8/uat_progress.json`. If present and the `test_plan_id` matches the current `test_plan.json`, treat the run as a resume:

- Skip test cases whose `id` is in `completed_test_ids[]` (their `evidence` and `status` from the prior run are reused).
- Re-run test cases in `failed_test_ids[]` only when the operator has indicated the underlying issue is fixed (look for entries in `uat_results.json.bugs[]` with `fix_verified: true`); otherwise leave them as failed and proceed.
- If `test_plan_id` does **not** match (the plan has been regenerated), discard `uat_progress.json` and run all cases from scratch.

`uat_progress.json` format:
```json
{
  "test_plan_id": "<sha256 prefix of test_plan.json bytes>",
  "completed_test_ids": ["TC-1", "TC-2"],
  "failed_test_ids": ["TC-3"],
  "in_progress_test_id": null,
  "started_at": "2026-05-09T10:00:00Z",
  "last_updated": "2026-05-09T10:25:00Z"
}
```

### Step 2 — Test Execution
- Load prompt: `.agents/skills/stage-8-uat/prompts/test_execution.md`
- Substitute: `{{test_plan_json}}`, `{{app_url}}`
- Execute:
  - **Unit tests:** if Stage 6 logs exist (e.g., `.agents/artifacts/stage-6/test.log`, `.agents/artifacts/stage-6/test.exit`), copy them into `.agents/artifacts/stage-8/unit/`; otherwise re-run `test_command` and write logs to `.agents/artifacts/stage-8/unit/`.
  - **Browser tests (mandatory for Medium/Large):**
    1. If `@playwright/test` is not in `node_modules`: `npm install -D @playwright/test`.
    2. If Chromium is not installed: `npx playwright install chromium`.
    3. Make sure the app is running at `{{app_url}}` (Step 0 should have started it).
    4. Run with full evidence capture:
       `npx playwright test --reporter=list,html --trace on --screenshot on --video retain-on-failure`
    5. After the run, **map each Playwright test to a `test_id` in `test_plan.json`** (by test title or `test.info().annotations`) and copy its artifacts into `.agents/artifacts/stage-8/playwright/<test-id>/`. Required per case: at least one `.png` (screenshot), one `.zip` (trace), or one `.webm`/`.mp4` (video). The Playwright HTML report under `playwright-report/` is also accepted as evidence.
    6. Record the resulting paths in `uat_results.json` under `results[].evidence.artifacts[]`.
- Write output to: `.agents/artifacts/stage-8/uat_results.json`

**Atomic resume update:** for each test case, the order is (1) write evidence file(s) to disk, (2) append the result to `uat_results.json`, (3) update `uat_progress.json` (move the test from `in_progress_test_id` into `completed_test_ids[]` or `failed_test_ids[]`, refresh `last_updated`). If the run is interrupted mid-test, `in_progress_test_id` lets the next invocation re-attempt that test only.

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
| Resume progress | `.agents/artifacts/stage-8/uat_progress.json` |
| Amendment requests (when bugs trace upstream) | `.agents/artifacts/stage-8/amendment_requests.json` |
| Escalation report (after 3 amendment cycles) | `.agents/artifacts/stage-8/escalation_report.json` |

## Gate

```bash
python .agents/skills/stage-8-uat/verify/uat_gate.py .agents/artifacts/stage-8/
```

**Pass criteria:** All P0 automated tests pass, no unfixed Critical bugs, computed `deployment_gate` is `APPROVED`, summary counts are consistent, **every user-facing flow in `flows.json` has at least one P0 browser test with `links_to_flow: [<FLOW-X>]`** (Medium/Large), and **every browser test marked PASS has at least one screenshot / video / trace artifact** (no `.log`-only evidence).

Bug schema (for `uat_results.json`):
- `id`, `severity`, `title`, `description`, `related_test_id`, `evidence`, `steps_to_reproduce`, `root_cause`, `fix_applied`, `fix_verified`, `upstream_target` (optional: `"stage-4"` or `"stage-5"` when the root cause is an upstream gap).

## Stage 8 → Upstream Amendment Loop

When a bug's `root_cause` indicates a gap in stories or tasks (a missing acceptance criterion, an under-specified flow path, an absent task), Stage 8 cannot fix it by re-running tests alone — the upstream artifacts must change. In that case the bug entry sets `upstream_target` to `"stage-4"` (story gap) or `"stage-5"` (task gap), and Stage 8 writes `.agents/artifacts/stage-8/amendment_requests.json` instead of attempting a fix.

`amendment_requests.json` format:
```json
{
  "cycle": 1,
  "requests": [
    {
      "id": "AR-1",
      "target_stage": "stage-4",
      "affected_id": "FR-3",
      "related_bug_id": "BUG-2",
      "related_test_id": "TC-7",
      "reason": "TC-7 fails because the empty-state behavior in FR-3 has no acceptance criterion covering keyboard activation.",
      "proposed_change": "Add story 'Keyboard activation of empty-state CTA' under FR-3 with acceptance criterion: pressing Enter while focus is on the empty-state link triggers the same action as click."
    }
  ]
}
```

The operator (or an upstream stage skill) merges these into `stories.json` or `tasks.json`, re-runs the affected stage forward through Stage 8, and increments `cycle`.

**Amendment cycle cap: 3.** On the third cycle, do not write a new `amendment_requests.json`. Write `.agents/artifacts/stage-8/escalation_report.json` with the remaining unfixed bugs and a summary of repeated failures, then HALT. Stage 8 does not modify upstream artifacts directly.

## Pipeline leakage rule (reminder)

Bug fixes that are *within* Stage 6's task scope (a code defect, not an upstream-spec defect) belong in `uat_results.json.bugs[]` with `upstream_target` omitted, and the operator re-runs Stage 6 to fix the code. Only use the amendment loop when the failing test reveals a gap in `stories.json` or `tasks.json` that no Stage 6 code change can satisfy.
