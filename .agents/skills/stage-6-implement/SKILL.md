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

Stage 6 outputs cover: code changes limited to the task list, build/test evidence logs, and a resumable progress record. Out of scope: modifying files not listed in tasks.json or claiming success without command output.

## Independent Invocation

To run this stage alone (requires Stage 1–5 artifacts):
```
Follow instructions in #file:.agents/skills/stage-6-implement/SKILL.md
```

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` |
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |
| `{{tasks_json}}` | Full contents of `.agents/artifacts/stage-5/tasks.json` |
| `{{stories_json}}` | Full contents of `.agents/artifacts/stage-4/stories.json` |
| `{{components_json}}` | Full contents of `.agents/artifacts/stage-2/components.json` |
| `{{tech_stack_json}}` | Full contents of `.agents/artifacts/stage-2/tech_stack.json` |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

---

## Request Sizing

**Before executing Step 1**, read the `size` field from `problem.json` (set by Stage 1). If the field is absent, **default to whatever size Stage 1 used**.

| Size | Execution approach |
|------|--------------------|
| **Trivial** | Single agent, implement all tasks in one pass; run build+tests once at the end. |
| **Medium** | Implement story-by-story; run build+tests after each story batch. |
| **Large** | Implement vertical slice by vertical slice; run build+tests at slice boundaries. Parallelize only when file ownership does not overlap. Use slice metadata from `tasks.json` if present; otherwise treat each story as a slice. |

---

> Shared conventions (size classification, anti-hallucination rule, traceability chain, pipeline leakage rule): see `.agents/skills/STAGE-CONVENTIONS.md`.

**Stage 6 specialization of the anti-hallucination rule:**
- Modify only files listed in `tasks.json`. If a task requires a new file not listed, **HALT** and report a missing task.
- Do not refactor or reformat unrelated files.
- Do not claim build/test success without captured logs.
- Do reference upstream IDs (FR-*, S-*, T-*) in progress logs to preserve traceability.

**Pipeline leakage rule:** do not reference Stage 7 (Review), Stage 8 (UAT), or Stage 9 (Deploy) in code or logs.

## Execution Steps

### Step 0 — Snapshot Pre-existing Tests
- Before writing any files, record the current test file list to `.agents/artifacts/stage-6/test_snapshot.json`.
- Include all files under `src/` and `tests/` that match typical test patterns (e.g., `*.test.*`, `*.spec.*`).

Command:
```bash
python .agents/skills/stage-6-implement/verify/capture_test_snapshot.py .agents/artifacts/stage-6/test_snapshot.json src tests
```

`test_snapshot.json` format:
```json
{
  "test_files": ["tests/unit/example.test.ts", "src/foo/bar.spec.ts"]
}
```

### Step 1 — Parse Execution Order
- Read `execution_order` from `tasks.json`
- Partition tasks into groups for parallel sub-agent execution where no cross-group dependencies exist
- Partition by **file ownership**: no two groups may modify the same file path
- Partition by **dependency**: tasks with dependency edges cannot be parallelized
- Partition by **import relationship**: if a task imports from another task's outputs, they are sequential
- If `execution_order` is absent, order tasks by dependencies and story grouping

### Step 2 — Code Generation
- Load prompt: `.agents/skills/stage-6-implement/prompts/code_generation.md`
- Substitute: `{{problem_json}}`, `{{goals_json}}`, `{{tasks_json}}`, `{{stories_json}}`, `{{components_json}}`, `{{tech_stack_json}}`

**Parallelism (Large only):** use sub-agents only when file ownership does not overlap. Each sub-agent owns a disjoint set of file paths.

For each task:
- Write the complete file to the path specified in the task
- Confirm: "Written: <path> (N lines)"
- Update `.agents/artifacts/stage-6/progress.json` after each file write (atomic: file write succeeds, then progress.json update)
- Track task verification separately once the task's tests pass

`progress.json` format:
```json
{
  "completed_tasks": ["T-1", "T-2"],
  "tasks_verified": ["T-1"],
  "failed_tasks": [
    {
      "id": "T-2",
      "command": "test",
      "log_excerpt": "AssertionError: expected ..."
    }
  ],
  "test_mode": "split",
  "modified_files": ["src/path/File.ts", "tests/path/File.test.ts"]
}
```

`test_mode` values: `split` | `full-suite`.

Resume semantics:
- Skip tasks that are in both `completed_tasks` and `tasks_verified`
- If a task is in `completed_tasks` but not `tasks_verified`, re-run that task's tests (do not re-write files)

Failure tracking:
- When retry limits are exhausted, add the task to `failed_tasks` with the command that failed and the log excerpt.
- Failed tasks must be manually inspected and either re-attempted or removed before Stage 6 can resume.

### Step 3 — Build Verification
Run `build_command` from `tech_stack.json`:
- Capture stdout/stderr to `.agents/artifacts/stage-6/build.log` and exit code to `.agents/artifacts/stage-6/build.exit`
- Exit non-zero → **HALT** — identify the specific failing file, fix it (within task scope), re-run
- Do not proceed to Step 4 until build succeeds

**Retry limit:** maximum 3 fix attempts per failing command. On the final failure, write `progress.json` and HALT.

**Retry scope:** maximum 3 attempts per command per task (build has its own 3, tests have their own 3).

### Step 4 — Test Verification
Run `test_command` from `tech_stack.json`:
- Capture stdout/stderr to `.agents/artifacts/stage-6/test.log` and exit code to `.agents/artifacts/stage-6/test.exit`
- Regression check: run pre-existing tests (from `test_snapshot.json`) and write `.agents/artifacts/stage-6/test_pre.log` + `.agents/artifacts/stage-6/test_pre.exit`
- New coverage check: run tests listed in `tasks.json` and write `.agents/artifacts/stage-6/test_new.log` + `.agents/artifacts/stage-6/test_new.exit`
- If the test runner cannot target specific files, run the full suite once, set `test_mode` to `full-suite`, and record only `test.log`/`test.exit`
- Otherwise set `test_mode` to `split`
- Exit non-zero → **HALT** — fix the failing test or implementation (within task scope), re-run
- Do not proceed to Stage 7 until all tests pass

**Retry limit:** maximum 3 fix attempts per failing command. On the final failure, write `progress.json` and HALT.

**Retry scope:** maximum 3 attempts per command per task (build has its own 3, tests have their own 3).

**Scope for fixes:** only modify files owned by the current task. If a fix requires modifying another task's file, HALT and report a cross-task dependency defect.

When cross-task dependency defects are detected, write `.agents/artifacts/stage-6/cross_task_defects.json` with the failing task, the task whose file needs modification, and the failing test/log excerpt. Then HALT.

### Step 5 — Verify Gate
```bash
python .agents/skills/stage-6-implement/verify/implementation_completeness.py \
  .agents/artifacts/stage-6/
```
- Exit non-zero → **HALT** — report missing coverage, do not proceed
- Exit 0 → Stage 6 complete

## Outputs

| Artifact | Path |
|---|---|
| Source code | `src/` |
| Build output | `dist/` |
| Build log | `.agents/artifacts/stage-6/build.log` |
| Build exit code | `.agents/artifacts/stage-6/build.exit` |
| Test log | `.agents/artifacts/stage-6/test.log` |
| Test exit code | `.agents/artifacts/stage-6/test.exit` |
| Pre-test log | `.agents/artifacts/stage-6/test_pre.log` |
| Pre-test exit code | `.agents/artifacts/stage-6/test_pre.exit` |
| New-test log | `.agents/artifacts/stage-6/test_new.log` |
| New-test exit code | `.agents/artifacts/stage-6/test_new.exit` |
| Progress record | `.agents/artifacts/stage-6/progress.json` |
| Test snapshot | `.agents/artifacts/stage-6/test_snapshot.json` |
| Cross-task defect report | `.agents/artifacts/stage-6/cross_task_defects.json` |

## Gate

```bash
<build_command> && <test_command>
python .agents/skills/stage-6-implement/verify/implementation_completeness.py \
  .agents/artifacts/stage-6/
```

**Pass criteria:** Build/test exit codes are 0 (per log files), `src/` is non-empty, no empty or placeholder files, every story ID referenced in at least one substantive test file, and progress.json only lists files present in tasks.json.

**Placeholder definition:** any of the following fails the gate — TODO/FIXME/TBD, "not implemented" or thrown not-implemented errors, lorem ipsum, or fewer than 5 non-comment/non-import lines (3 for tests).

**Substantive test definition:** test file includes at least one assertion and (for non-e2e) imports a symbol from a story-owned implementation file.

**Trivial tradeoff:** Trivial runs build/tests once at the end; failures are reported at the batch level rather than per task.

## Completion Report

When reporting Stage 6 completion, cite evidence from the artifact files:
- Build: exit code and log file path
- Tests: exit codes and log file paths (pre/new or full-suite)
- Tasks completed: from `progress.json`
- Files modified: from `progress.json`

Template:
```
Stage 6 Status: COMPLETE | PARTIAL | FAILED
Tasks completed: <N>/<total> (progress.json)
Tasks verified: <N>/<total> (progress.json)
Build: exit <code> (build.log)
Tests (pre-existing): exit <code> (test_pre.log) — <N> passed
Tests (new): exit <code> (test_new.log) — <N> passed
Files modified: <count> (progress.json)
```
