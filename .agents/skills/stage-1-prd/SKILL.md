---
name: stage-1-prd
description: |
  Generate a structured Product Requirements Document (PRD) from a feature request or bug description.
  Outputs problem.json, goals.json, and prd_final.md to .agents/artifacts/stage-1/.
  Can be invoked independently to create or update the PRD for any request.
---

# Stage 1: Product Requirements Document (PRD)

You are a PRD specialist. Expand the user's feature or bug description into a structured, goals-driven PRD.

## Independent Invocation

To run this stage alone:
```
Follow instructions in #file:.agents/skills/stage-1-prd/SKILL.md with: <your feature or bug description>
```
Optionally attach context files: `@Requirements.md @design-spec.md`

## Variable Substitution

Replace every `{{placeholder}}` before executing a sub-prompt:

| Placeholder | Source |
|---|---|
| `{{user_request}}` | The plain-text feature/bug description from the invocation arguments |
| `{{requirements_context}}` | Concatenated contents of all `@file` references, separated by `---`. If none attached, use `"No context files provided"` |
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` (available after Step 1) |

**Rule:** Never leave a `{{placeholder}}` unreplaced. If a source file does not exist yet, that is a sequencing error — halt and report it.

## Execution Steps

### Step 1 — Problem Interpretation
- Load prompt: `.agents/skills/stage-1-prd/prompts/problem_interpretation.md`
- Substitute: `{{user_request}}`, `{{requirements_context}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-1/problem.json`

### Step 2 — Goals & Scope Extraction
- Load prompt: `.agents/skills/stage-1-prd/prompts/goals_extraction.md`
- Substitute: `{{problem_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-1/goals.json`

### Step 3 — Verify Gate
```bash
python .agents/skills/stage-1-prd/verify/prd_structure.py .agents/artifacts/stage-1/goals.json
```
- Exit non-zero → **HALT** — report the specific error in chat, do not proceed
- Exit 0 → continue

### Step 4 — Compile Final PRD
- Combine `problem.json` + `goals.json` into `.agents/artifacts/stage-1/prd_final.md`
- Include: traceability matrix linking goals to requirements, ambiguities array, all defaults applied

## Outputs

| Artifact | Path |
|---|---|
| Problem statement | `.agents/artifacts/stage-1/problem.json` |
| Goals & requirements | `.agents/artifacts/stage-1/goals.json` |
| Final PRD document | `.agents/artifacts/stage-1/prd_final.md` |

## Gate

```bash
python .agents/skills/stage-1-prd/verify/prd_structure.py .agents/artifacts/stage-1/goals.json
```

**Pass criteria:** Valid JSON, at least one GOAL with success criteria, at least one P0 FR with acceptance criteria, no vague language.
