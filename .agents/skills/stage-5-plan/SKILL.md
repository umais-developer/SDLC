---
name: stage-5-plan
description: |
  Decompose user stories into ordered implementation tasks with dependencies and effort estimates.
  Outputs tasks.json and plan_story_final.md to .agents/artifacts/stage-5/.
  Can be invoked independently after Stages 1–4 are complete.
---

# Stage 5: Implementation Plan

You are a Tech Lead. Decompose user stories into concrete, ordered implementation tasks. Define what files to create or modify, in what order, and with what tests.

## Independent Invocation

To run this stage alone (requires Stage 1–4 artifacts):
```
Follow instructions in #file:.agents/skills/stage-5-plan/SKILL.md
```

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{stories_json}}` | Full contents of `.agents/artifacts/stage-4/stories.json` |
| `{{components_json}}` | Full contents of `.agents/artifacts/stage-2/components.json` |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

## Execution Steps

### Step 1 — Implementation Plan Generation
- Load prompt: `.agents/skills/stage-5-plan/prompts/implementation_plan.md`
- Substitute: `{{stories_json}}`, `{{components_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-5/tasks.json`

### Step 2 — Verify Gate
```bash
python .agents/skills/stage-5-plan/verify/tasks_structure.py .agents/artifacts/stage-5/tasks.json .agents/artifacts/stage-4/stories.json
```
- Exit non-zero → **HALT** — report the specific error, do not proceed
- Exit 0 → continue

### Step 3 — Compile Final Plan Document
- Compile `tasks.json` into `.agents/artifacts/stage-5/plan_story_final.md`
- Include: tasks grouped by story, execution order, dependency graph, effort estimates

## Outputs

| Artifact | Path |
|---|---|
| Implementation tasks | `.agents/artifacts/stage-5/tasks.json` |
| Final plan document | `.agents/artifacts/stage-5/plan_story_final.md` |

## Gate

```bash
python .agents/skills/stage-5-plan/verify/tasks_structure.py .agents/artifacts/stage-5/tasks.json .agents/artifacts/stage-4/stories.json
```

**Pass criteria:** Every story has at least one implementation task and one test task, dependency graph is acyclic, every task has a file and definition_of_done.
