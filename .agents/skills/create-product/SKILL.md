---
name: create-product
description: |
  Orchestrate the full SDLC pipeline from PRD to UAT.
  Runs all stages in sequence (1–8), verifying each gate before proceeding.
  Auto-detects the resume point and continues from the first incomplete stage.
  Invoke this to build or continue building a complete product.
---

# Create Product — SDLC Pipeline Orchestrator

You are an AI SDLC orchestrator. You run the full pipeline by invoking each stage skill in sequence, running its verification gate, and halting on any failure.

## How to Invoke

```
Follow instructions in #file:.agents/skills/create-product/SKILL.md with: <feature or product description>
```

Optionally attach context files:
```
Follow instructions in #file:.agents/skills/create-product/SKILL.md with: build a todo app @Requirements.md @design-spec.md
```

All `@file` references are passed to Stage 1 as requirements context.

## Variable Substitution

Before executing any stage, resolve all `{{placeholder}}` values:

| Placeholder | Source |
|---|---|
| `{{user_request}}` | The plain-text description from the invocation arguments |
| `{{requirements_context}}` | Concatenated contents of all `@file` references, separated by `---`. If none, use `"No context files provided"` |
| `{{codebase_context}}` | List all files under `src/` with line counts. If `src/` does not exist, use `"No existing codebase"` |
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` (used to announce size classification) |
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |
| `{{tech_stack_json}}` | Full contents of `.agents/artifacts/stage-2/tech_stack.json` |
| `{{components_json}}` | Full contents of `.agents/artifacts/stage-2/components.json` |
| `{{flows_json}}` | Full contents of `.agents/artifacts/stage-3/flows.json` |
| `{{stories_json}}` | Full contents of `.agents/artifacts/stage-4/stories.json` |
| `{{tasks_json}}` | Full contents of `.agents/artifacts/stage-5/tasks.json` |
| `{{source_files_list}}` | List of all files under `src/` with relative paths |
| `{{test_plan_json}}` | Full contents of `.agents/artifacts/stage-8/test_plan.json` |
| `{{app_url}}` | URL of the running app — start the dev server using `dev_command` or `start_command` from `tech_stack.json` if not running |

**Rule:** Never leave a `{{placeholder}}` unreplaced. If the source file for a placeholder does not exist yet, that is a sequencing error — halt and report it.

---

## Step 1 — Auto-Detect Resume Point

Check for completed artifacts in order. Start from the **first missing** artifact:

| Check | Missing → Start Stage |
|---|---|
| `.agents/artifacts/stage-1/prd_final.md` missing | **Stage 1** |
| `.agents/artifacts/stage-2/architecture_final.md` missing | **Stage 2** |
| `.agents/artifacts/stage-3/ux_final.md` missing | **Stage 3** |
| `.agents/artifacts/stage-4/epics_stories_final.md` missing | **Stage 4** |
| `.agents/artifacts/stage-5/plan_story_final.md` missing | **Stage 5** |
| `src/` missing or build fails | **Stage 6** |
| `.agents/artifacts/stage-7/CODE_REVIEW.md` missing | **Stage 7 Review** |
| `.agents/artifacts/stage-8/uat-results_final.md` missing | **Stage 8 UAT** |
| All present | **Pipeline complete (Stage 8 done)** |

Announce:
> "Detected resume point: Stage N — [name]. Size classification: [Trivial|Medium|Large]. Artifacts present: [list]. Proceeding from Stage N."

---

## Step 2 — Execute the Pipeline

For each stage from the resume point onward, follow the SKILL.md for that stage exactly. The stage defines and runs its own gate command(s).

### Stage 1: PRD
Follow: `.agents/skills/stage-1-prd/SKILL.md`

### Stage 2: Architecture
Follow: `.agents/skills/stage-2-architecture/SKILL.md`

### Stage 3: UX Design
Follow: `.agents/skills/stage-3-ux/SKILL.md`

### Stage 4: Epics & Stories
Follow: `.agents/skills/stage-4-epics/SKILL.md`

### Stage 5: Implementation Plan
Follow: `.agents/skills/stage-5-plan/SKILL.md`

### Stage 6: Implementation
Follow: `.agents/skills/stage-6-implement/SKILL.md`

### Stage 7: Code Review
Follow: `.agents/skills/stage-7-review/SKILL.md`

### Stage 8: User Acceptance Testing
Follow: `.agents/skills/stage-8-uat/SKILL.md`

---

## Error Handling

**Any non-zero gate exit:**
1. Halt pipeline immediately
2. Display the stage name and exact error message in chat
3. Do not auto-fix or skip the failure
4. If the stage defines an internal retry/amendment loop, that stage handles it. Otherwise, the user resolves the issue and re-invokes from that stage:
  ```
  Follow instructions in #file:.agents/skills/stage-N-name/SKILL.md
  ```

---

## Artifact Reference

```
.agents/artifacts/
├── stage-1/
│   ├── problem.json
│   ├── goals.json
│   └── prd_final.md
├── stage-2/
│   ├── capabilities.json
│   ├── tech_stack.json
│   ├── components.json
│   └── architecture_final.md
├── stage-3/
│   ├── flows.json
│   └── ux_final.md
├── stage-4/
│   ├── stories.json
│   └── epics_stories_final.md
├── stage-5/
│   ├── tasks.json
│   └── plan_story_final.md
├── stage-6/
│   ├── build.log
│   ├── build.exit
│   ├── test.log
│   ├── test.exit
│   ├── progress.json
│   └── test_snapshot.json
├── stage-7/
│   ├── review.json
│   └── CODE_REVIEW.md
├── stage-8/
│   ├── test_plan.json
│   ├── uat-test-plan_final.md
│   ├── uat_results.json
│   └── uat-results_final.md
```
