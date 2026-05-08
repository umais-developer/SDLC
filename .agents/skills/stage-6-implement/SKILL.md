---
name: stage-6-implement
description: |
  Generate production-quality source code and tests from the implementation plan.
  Uses parallel sub-agents for large components. Build and tests must pass before completion.
  Outputs source code to src/ and build artifacts to dist/.
  Can be invoked independently after Stages 1–5 are complete.
---

# Stage 6: Implementation

You are a Senior Developer. Generate source code for each task in the implementation plan using the technology stack defined in Stage 2. Write complete files — no placeholders, no partial implementations.

## Independent Invocation

To run this stage alone (requires Stage 1–5 artifacts):
```
Follow instructions in #file:.agents/skills/stage-6-implement/SKILL.md
```

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{tasks_json}}` | Full contents of `.agents/artifacts/stage-5/tasks.json` |
| `{{components_json}}` | Full contents of `.agents/artifacts/stage-2/components.json` |
| `{{tech_stack_json}}` | Full contents of `.agents/artifacts/stage-2/tech_stack.json` |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

## Execution Steps

### Step 1 — Parse Execution Order
- Read `execution_order` from `tasks.json`
- Partition tasks into groups for parallel sub-agent execution where no cross-group dependencies exist

### Step 2 — Code Generation
- Load prompt: `.agents/skills/stage-6-implement/prompts/code_generation.md`
- Substitute: `{{tasks_json}}`, `{{components_json}}`, `{{tech_stack_json}}`

**For projects with parallelizable components**, use sub-agent prompts:
- `.agents/skills/stage-6-implement/prompts/subagent_engine_replay.md` — core engine + replay
- `.agents/skills/stage-6-implement/prompts/subagent_render_ui.md` — rendering + UI
- `.agents/skills/stage-6-implement/prompts/subagent_entry_build.md` — entry points + build

For each task: write the complete file to the path specified in the task. Confirm: `"Written: <path> (N lines)"`

### Step 3 — Build Verification
Run `build_command` from `tech_stack.json`:
- Exit non-zero → **HALT** — identify the specific failing file, fix it, re-run
- Do not proceed to Step 4 until build succeeds

### Step 4 — Test Verification
Run `test_command` from `tech_stack.json`:
- Exit non-zero → **HALT** — fix the failing test or implementation, re-run
- Do not proceed to Stage 7 until all tests pass

### Step 5 — Verify Gate
```bash
python .agents/skills/stage-6-implement/verify/implementation_completeness.py src/ .agents/artifacts/stage-4/stories.json
```
- Exit non-zero → **HALT** — report missing coverage, do not proceed
- Exit 0 → Stage 6 complete

## Outputs

| Artifact | Path |
|---|---|
| Source code | `src/` |
| Build output | `dist/` |

## Gate

```bash
<build_command> && <test_command>
python .agents/skills/stage-6-implement/verify/implementation_completeness.py src/ .agents/artifacts/stage-4/stories.json
```

**Pass criteria:** Build exits 0, all tests pass, `src/` is non-empty, no empty files, every story ID referenced in at least one test file.
