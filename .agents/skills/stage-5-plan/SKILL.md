---
name: stage-5-plan
description: |
  Decompose user stories into ordered implementation tasks with dependencies and effort estimates.
  Outputs tasks.json and plan_story_final.md to .agents/artifacts/stage-5/.
  Can be invoked independently after Stages 1–4 are complete.
---

# Stage 5: Implementation Plan

You are a Tech Lead. Decompose user stories into concrete, ordered implementation tasks. Define what files to create or modify, in what order, and with what tests.

Stage 5 outputs cover: file-level tasks, test specifics, task-level sequencing, and verifiable definitions of done. Out of scope: re-stating stories without file/test granularity or inventing file paths that don't match the codebase.

## Independent Invocation

Requires Stage 1–4 artifacts. Pick the form that matches your environment:

- **Claude Code:** `/stage-5`
- **GitHub Copilot:** `Follow instructions in #file:.agents/skills/stage-5-plan/SKILL.md`
- **Other agents:** Read this file and follow it.

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` |
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |
| `{{stories_json}}` | Full contents of `.agents/artifacts/stage-4/stories.json` |
| `{{components_json}}` | Full contents of `.agents/artifacts/stage-2/components.json` |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

---

## Request Sizing

**Before executing Step 1**, read the `size` field from `problem.json` (set by Stage 1). If the field is absent, **default to whatever size Stage 1 used** — use the same classification rather than re-deriving it from implementation criteria the PRD does not directly answer.

| Size | Stage 5 work required |
|------|------------------------|
| **Trivial** | 1–3 tasks with file paths and tests. No full task graph. Compile before gate. |
| **Medium** | Tasks per story with intra-story dependencies. Tests listed per task. |
| **Large** | Full task graph with cross-story dependencies and vertical-slice suggestions. |

**Execution order note:** Trivial runs Step 3 (compile) before Step 2 (gate). Medium/Large runs Step 2 (gate) before Step 3 (compile).

When in doubt, default to **Medium**.

---

> Shared conventions (size classification, anti-hallucination rule, traceability chain, pipeline leakage rule): see `.agents/skills/STAGE-CONVENTIONS.md`.

**Stage 5 specialization of the anti-hallucination rule:** do not invent file paths, test locations, or estimates that contradict the existing structure.
- **Do not write:** "Add src/utils/searchHelpers.js" when no utils folder exists / "Estimated 3 hours" with no concrete rationale
- **Do write:** file paths consistent with `components.json` and test paths consistent with the repo layout; omit estimates entirely

**Pipeline leakage rule:** do not reference Stage 6 execution steps in tasks or `plan_story_final.md`.
- **Do write:** concrete file-level tasks, tests, and verifiable definitions of done.

## Execution Steps

### Step 1 — Implementation Plan Generation
- Load prompt: `.agents/skills/stage-5-plan/prompts/implementation_plan.md`
- Substitute: `{{problem_json}}`, `{{goals_json}}`, `{{stories_json}}`, `{{components_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-5/tasks.json`

**Task requirements (all sizes):**
- Each task must cite a `story_id` (when `stories.json` exists) and `links_to` IDs (`FR/NFR/CON/GOAL`)
- Each task must include a concrete `file` path consistent with `components.json` (either the component file itself or a co-located test/config/type file such as `__tests__/`, `*.test.*`, `*.spec.*`, `*.d.ts`, or `*.config.*`)
- Each task must include `tests` (test file paths and/or test cases) and a verifiable `definition_of_done`
- Definition of done must reference a concrete command or test file (not prose like “looks good”)
- Dependencies only when a task is blocked by another task (stories with fully parallelizable tasks may have no dependencies)
- Tests are listed in each task’s `tests` field (do not create separate “test-only” tasks)

### Step 2 — Verify Gate
**Medium only:**
```bash
python .agents/skills/stage-5-plan/verify/tasks_structure.py \
  .agents/artifacts/stage-5/tasks.json \
  .agents/artifacts/stage-4/stories.json \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-2/components.json
```

**Large only (enforce dependencies + execution order):**
```bash
python .agents/skills/stage-5-plan/verify/tasks_structure.py \
  .agents/artifacts/stage-5/tasks.json \
  .agents/artifacts/stage-4/stories.json \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-2/components.json \
  --require-deps \
  --require-order
```

**Trivial:**
```bash
python .agents/skills/stage-5-plan/verify/tasks_structure.py --trivial \
  .agents/artifacts/stage-5/tasks.json \
  .agents/artifacts/stage-5/plan_story_final.md \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-2/components.json
```
- Exit non-zero → **HALT** — report the specific error, do not proceed
- Exit 0 → continue

### Step 3 — Compile Final Plan Document
- Compile `tasks.json` into `.agents/artifacts/stage-5/plan_story_final.md`

**Trivial format**
- 1+ tasks with file paths, tests, DoD statements, and `links_to` IDs surfaced in the text

**Medium format**
- Tasks grouped by story with intra-story ordering
- No cross-story dependency graph required

**Large format**
- Full task dependency graph
- Suggested vertical slices for incremental delivery (each slice is a named group of tasks that yields a demoable user-visible increment and cites the FRs it enables)

## Outputs

| Artifact | Path |
|---|---|
| Implementation tasks (all sizes) | `.agents/artifacts/stage-5/tasks.json` |
| Final plan document | `.agents/artifacts/stage-5/plan_story_final.md` |

## Gate

**Medium only:**

```bash
python .agents/skills/stage-5-plan/verify/tasks_structure.py \
  .agents/artifacts/stage-5/tasks.json \
  .agents/artifacts/stage-4/stories.json \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-2/components.json
```

**Large only (enforce dependencies + execution order):**

```bash
python .agents/skills/stage-5-plan/verify/tasks_structure.py \
  .agents/artifacts/stage-5/tasks.json \
  .agents/artifacts/stage-4/stories.json \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-2/components.json \
  --require-deps \
  --require-order
```

**Trivial:**

```bash
python .agents/skills/stage-5-plan/verify/tasks_structure.py --trivial \
  .agents/artifacts/stage-5/tasks.json \
  .agents/artifacts/stage-5/plan_story_final.md \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-2/components.json
```

**Pass criteria (Medium / Large):**
- Every story has at least one task that references it
- Every task has `file`, `tests`, and verifiable `definition_of_done`
- Task `links_to` IDs resolve to `goals.json`
- Task `file` paths are consistent with `components.json`
- Dependency graph is acyclic (Large enforces full graph)

**Pass criteria (Trivial):**
- `plan_story_final.md` exists and cites at least one FR/NFR/CON/GOAL ID
- `tasks.json` contains tasks with valid file paths and tests
