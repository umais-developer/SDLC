---
name: stage-7-review
description: |
  Audit the implementation against architecture contracts and requirements.
  Finds real problems — every finding references a specific file and location.
  Outputs review.json and CODE_REVIEW.md to .agents/artifacts/stage-7/.
  Can be invoked independently after Stage 6 is complete.
---

# Stage 7: Code Review

You are a Senior Engineer and Code Reviewer. Audit the generated implementation against the architecture and requirements. Find real problems — every finding must reference a specific file and the exact issue.

Stage 7 is read-only. Do not modify any files outside `.agents/artifacts/stage-7/`.

## Independent Invocation

Requires Stage 1–6 artifacts and `src/`. Pick the form that matches your environment:

- **Claude Code:** `/stage-7`
- **GitHub Copilot:** `Follow instructions in #file:.agents/skills/stage-7-review/SKILL.md`
- **Other agents:** Read this file and follow it.

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{source_files_list}}` | List all files under `src/` with relative paths and line counts |
| `{{components_json}}` | Full contents of `.agents/artifacts/stage-2/components.json` |
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` |
| `{{stories_json}}` | Full contents of `.agents/artifacts/stage-4/stories.json` |
| `{{tasks_json}}` | Full contents of `.agents/artifacts/stage-5/tasks.json` |
| `{{progress_json}}` | Full contents of `.agents/artifacts/stage-6/progress.json` |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

---

## Request Sizing

**Before executing Step 1**, read the `size` field from `problem.json` (set by Stage 1). If the field is absent, **default to whatever size Stage 1 used**.

| Size | Review depth |
|------|--------------|
| **Trivial** | Deterministic structural checks only; no qualitative review required. |
| **Medium** | Structural checks + targeted review of files in `progress.json.modified_files`. |
| **Large** | Structural checks + full qualitative review of all files in `src/` + architecture conformance. |

---

> Shared conventions (size classification, anti-hallucination rule, traceability chain, pipeline leakage rule): see `.agents/skills/STAGE-CONVENTIONS.md`.

**Stage 7 specialization of the anti-hallucination rule:**
- Do not fabricate findings or fabricate clean reviews.
- Every finding must cite a real file path and line range that exists.
- Every passed check must cite the file and line range that was checked.
- Do not invent file paths, line numbers, or issue categories.

**Pipeline leakage rule:** do not reference Stage 8 (UAT) or Stage 9 (Deploy) work.

## Execution Steps

### Step 1 — Code Audit
- Load prompt: `.agents/skills/stage-7-review/prompts/code_audit.md`
- Substitute: `{{source_files_list}}`, `{{components_json}}`, `{{goals_json}}`, `{{problem_json}}`, `{{stories_json}}`, `{{tasks_json}}`, `{{progress_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-7/review.json`

### Step 2 — Verify Gate
```bash
python .agents/skills/stage-7-review/verify/code_review_verdict.py .agents/artifacts/stage-7/
```
- Exit non-zero → **HALT** — output the `must_fix_before_proceeding` list with file, line range, and suggested fix for each item. Do NOT apply fixes yourself. The developer must fix the code and re-invoke this stage.
- Exit 0 → continue

### Step 3 — Compile Code Review Document
- Compile `review.json` into `.agents/artifacts/stage-7/CODE_REVIEW.md`
- Include: verdict, findings by severity, strengths, must-fix list

## Outputs

| Artifact | Path |
|---|---|
| Review results | `.agents/artifacts/stage-7/review.json` |
| Code review document | `.agents/artifacts/stage-7/CODE_REVIEW.md` |

## Gate

```bash
python .agents/skills/stage-7-review/verify/code_review_verdict.py .agents/artifacts/stage-7/
```

**Pass criteria:** Verdict is `APPROVE`, no Critical or High findings, every finding has a `suggested_fix` and file.

Deterministic checks run by the verifier (non-model):
- Every component in `components.json` with a file/path entry exists in `src/`
- Every story ID in `stories.json` appears in at least one test file
- Every file in `progress.json.modified_files` is referenced by a task in `tasks.json`
- Every test file listed in `tasks.json` exists
- Every finding/check cites a real file path and line range

## Verdict Rules

| Condition | Verdict |
|---|---|
| Any Critical or High | `CHANGES_REQUIRED` → **HALT**, fix and re-invoke |
| Only Medium/Low | `APPROVE` (documented in `can_fix_in_followup`) |
| 0 Critical, 0 High, 0 Medium, 0 Low | `APPROVE` |

## Severity Definitions

- **Critical:** Blocks deployment or core flow; security vulnerability; data loss; build/test failure.
- **High:** Must fix before merge; violates an FR acceptance criterion or a CON-* constraint; regression risk in pre-existing behavior.
- **Medium:** Should fix; violates a non-P0 NFR; test coverage gap for a non-critical path; maintainability risk.
- **Low:** Nice-to-fix; naming, minor clarity, style issues.

Tie severity to upstream IDs when possible: violations of FR/CON are at least High; violations of P0 NFR are at least Medium.

## Review Schema Notes

- `must_fix_before_proceeding` entries must include: `id`, `severity`, `file`, `line_range`, `links_to`, `suggested_fix`.
- `links_to` is a list of `FR-*`, `NFR-*`, `CON-*`, or `GOAL-*` IDs from `goals.json` that the finding violates or relates to. May be empty for issues unrelated to a specific requirement.
- `suggested_fix` is guidance, not a required implementation approach.
- For **Trivial**, `review.json` must include `verdict`, `checks_performed`, and empty arrays for `findings`, `strengths`, and `must_fix_before_proceeding`.

## Stage 7 → Stage 6 Loop

When `CHANGES_REQUIRED`, write amendment task definitions to `.agents/artifacts/stage-7/amendment_tasks.json`. The operator (or orchestrator) is responsible for merging these into `tasks.json` before re-running Stage 6. Stage 7 does not modify `tasks.json` directly.

Review cycle cap: maximum 3 iterations. On the third failure, halt and escalate.

Escalation artifact:
- Write `.agents/artifacts/stage-7/escalation_report.json` with remaining must-fix items and a summary of repeated failures.

## CODE_REVIEW.md Formats

- **Trivial:** verdict + deterministic checks passed/failed.
- **Medium:** verdict + findings grouped by severity + must-fix list.
- **Large:** verdict + findings grouped by severity + strengths (cited) + must-fix list + architecture conformance summary.

## Strengths (Optional)

- Strengths must cite specific files and line ranges; no generic praise.
