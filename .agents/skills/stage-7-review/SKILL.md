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

## Independent Invocation

To run this stage alone (requires Stage 1–6 artifacts and `src/`):
```
Follow instructions in #file:.agents/skills/stage-7-review/SKILL.md
```

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{source_files_list}}` | List all files under `src/` with relative paths and line counts |
| `{{components_json}}` | Full contents of `.agents/artifacts/stage-2/components.json` |
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

## Execution Steps

### Step 1 — Code Audit
- Load prompt: `.agents/skills/stage-7-review/prompts/code_audit.md`
- Substitute: `{{source_files_list}}`, `{{components_json}}`, `{{goals_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-7/review.json`

### Step 2 — Verify Gate
```bash
python .agents/skills/stage-7-review/verify/code_review_verdict.py .agents/artifacts/stage-7/review.json
```
- Exit non-zero → **HALT** — output the `must_fix_before_proceeding` list with file, location, and fix for each item. Do NOT apply fixes yourself. The developer must fix the code and re-invoke this stage.
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
python .agents/skills/stage-7-review/verify/code_review_verdict.py .agents/artifacts/stage-7/review.json
```

**Pass criteria:** Verdict is `APPROVE`, no Critical or High findings, every finding has a specified fix and file.

## Verdict Rules

| Condition | Verdict |
|---|---|
| 0 Critical, 0 High | `APPROVE` → proceed to Stage 7 UAT |
| Any Critical or High | `CHANGES_REQUIRED` → **HALT**, fix and re-invoke |
| Only Medium/Low | `APPROVE` (documented in `can_fix_in_followup`) |
