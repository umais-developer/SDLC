---
name: create-product
description: |
  Orchestrate the full SDLC pipeline from PRD to deployment.
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
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` |
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |
| `{{tech_stack_json}}` | Full contents of `.agents/artifacts/stage-2/tech_stack.json` |
| `{{components_json}}` | Full contents of `.agents/artifacts/stage-2/components.json` |
| `{{flows_json}}` | Full contents of `.agents/artifacts/stage-3/flows.json` |
| `{{stories_json}}` | Full contents of `.agents/artifacts/stage-4/stories.json` |
| `{{tasks_json}}` | Full contents of `.agents/artifacts/stage-5/tasks.json` |
| `{{source_files_list}}` | List of all files under `src/` with relative paths |
| `{{test_plan_json}}` | Full contents of `.agents/artifacts/stage-7.5/test_plan.json` |
| `{{app_url}}` | URL of the running app — start the dev server using `build_command` from `tech_stack.json` if not running |
| `{{repo_name}}` | Value of `name` in `package.json`, otherwise derive from the project folder name |

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
| `.agents/artifacts/stage-7.5/uat-results_final.md` missing | **Stage 7 UAT** |
| All present | **Stage 8** |

Announce:
> "Detected resume point: Stage N — [name]. Artifacts present: [list]. Proceeding from Stage N."

---

## Step 2 — Execute the Pipeline

For each stage from the resume point onward, follow the SKILL.md for that stage exactly:

### Stage 1: PRD
Follow: `.agents/skills/stage-1-prd/SKILL.md`
Gate: `python .agents/skills/stage-1-prd/verify/prd_structure.py .agents/artifacts/stage-1/goals.json`

### Stage 2: Architecture
Follow: `.agents/skills/stage-2-architecture/SKILL.md`
Gate: `python .agents/skills/stage-2-architecture/verify/architecture_completeness.py .agents/artifacts/stage-2/components.json`

### Stage 3: UX Design
Follow: `.agents/skills/stage-3-ux/SKILL.md`
Gate: `python .agents/skills/stage-3-ux/verify/flows_structure.py .agents/artifacts/stage-3/flows.json .agents/artifacts/stage-1/goals.json`

### Stage 4: Epics & Stories
Follow: `.agents/skills/stage-4-epics/SKILL.md`
Gate: `python .agents/skills/stage-4-epics/verify/story_traceability.py .agents/artifacts/stage-4/stories.json .agents/artifacts/stage-1/goals.json`

### Stage 5: Implementation Plan
Follow: `.agents/skills/stage-5-plan/SKILL.md`
Gate: `python .agents/skills/stage-5-plan/verify/tasks_structure.py .agents/artifacts/stage-5/tasks.json .agents/artifacts/stage-4/stories.json`

### Stage 6: Implementation
Follow: `.agents/skills/stage-6-implement/SKILL.md`
Gate: `<build_command> && <test_command> && python .agents/skills/stage-6-implement/verify/implementation_completeness.py src/ .agents/artifacts/stage-4/stories.json`

### Stage 7: Code Review
Follow: `.agents/skills/stage-7-review/SKILL.md`
Gate: `python .agents/skills/stage-7-review/verify/code_review_verdict.py .agents/artifacts/stage-7/review.json`

### Stage 7 UAT: User Acceptance Testing
Follow: `.agents/skills/stage-7-uat/SKILL.md`
Gate: `python .agents/skills/stage-7-uat/verify/uat_gate.py .agents/artifacts/stage-7.5/uat_results.json`

### Stage 8: Deploy
Follow: `.agents/skills/stage-8-deploy/SKILL.md`
Gate: Human confirms deployment URL is accessible

---

## Error Handling

**Any non-zero gate exit:**
1. Halt pipeline immediately
2. Display the stage name, error type, and exact message in chat
3. Do not auto-fix or skip the failure
4. User resolves the issue and re-invokes from that stage:
   ```
   Follow instructions in #file:.agents/skills/stage-N-name/SKILL.md
   ```

**Typed errors from verify scripts:**
- `StructureError` — JSON schema mismatch
- `TraceabilityError` — Reference integrity failure
- `CompletionError` — Required items missing
- `GateError` — Gate condition not met

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
├── stage-7/
│   ├── review.json
│   └── CODE_REVIEW.md
├── stage-7.5/
│   ├── test_plan.json
│   ├── uat-test-plan_final.md
│   ├── uat_results.json
│   └── uat-results_final.md
└── stage-8/
    └── deployment_config.json
```
