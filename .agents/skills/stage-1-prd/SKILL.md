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

This skill is tool-neutral. Pick the form that matches your environment:

- **Claude Code:** `/stage-1 <your feature or bug description>`
- **GitHub Copilot:** `Follow instructions in #file:.agents/skills/stage-1-prd/SKILL.md with: <your feature or bug description>`
- **Other agents:** Read this file and follow it; pass the request as input.

Optionally attach context files (`@Requirements.md @design-spec.md` in Copilot, or pass them as additional context in other tools).

## Variable Substitution

Replace every `{{placeholder}}` before executing a sub-prompt:

| Placeholder | Source |
|---|---|
| `{{user_request}}` | The plain-text feature/bug description from the invocation arguments |
| `{{requirements_context}}` | Concatenated contents of all `@file` references, separated by `---`. If none attached, use `"No context files provided"` |
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` (available after Step 1) |
| `{{prd_check_report}}` | Full contents of `.agents/artifacts/stage-1/prd_check_report.json` (available after Step 4a fails) |

**Rule:** Never leave a `{{placeholder}}` unreplaced. If a source file does not exist yet, that is a sequencing error — halt and report it.

---

## Audience

This PRD is written for two audiences:

1. **Human reviewer (primary):** A PM or tech lead confirming scope before work begins. They need clarity and honesty about assumptions — surface those first, bury traceability last.
2. **Downstream LLM stages (secondary):** Stage 2 (Architecture) and Stage 4 (Epics) consume this document as structured input. Crisp, unambiguous fields matter more than prose ceremony.

Write for the human first. If a section would confuse a human reviewer, it is wrong.

---

## Request Sizing

**Before executing Step 1**, classify the request size. This governs the PRD format used in Step 4.

| Size | When to use | Step 4 PRD format |
|------|-------------|-------------------|
| **Trivial** | Single UI tweak, copy change, isolated bug touching ≤2 files | Short-form: Problem statement + Assumptions + Scope + Acceptance criteria only. No Goals section, no Traceability Matrix, no NFRs unless directly affected. |
| **Medium** | Self-contained feature touching 1–3 components, new standalone page, small enhancement | Standard form: all sections; story points optional; omit Traceability Matrix if GOAL count ≤ 2. |
| **Large** | Cross-cutting feature, new subsystem, multiple interdependent components, architectural change | Full form: all sections required including Traceability Matrix, NFRs, and story points. |

When in doubt, default to **Medium**.

---

## Anti-Hallucination Rule

**Never invent a number, benchmark, or justification.**

If a value is not stated in the user request and is not a universally-known industry default (e.g., HTTP status code 404, WCAG AA contrast ratio 4.5:1):

- Mark it with an explicit assumption label: `[assumed: 150 ms — matches classic Nokia pacing]` — **not** `"derived from playability testing norms"` or `"based on industry benchmarks"`
- Add it to `ambiguities[]` in problem.json and to the Assumptions section of the PRD
- **Never** cite studies, user research, or testing data that you cannot verify from the provided context

Examples of invented precision to avoid:
- "≥80% high-score save rate" (where did 80% come from?)
- "2019 mid-range Android device" (invented specificity)
- "derived from playability testing norms" (no such test was run)

If you genuinely cannot determine a reasonable default, use `null` in JSON and write `[TBD — stakeholder input needed]` in the PRD.

---

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
- Apply the PRD format for the request size determined before Step 1 (Trivial / Medium / Large)
- If recompiling after a failed Step 4a, load `.agents/artifacts/stage-1/prd_check_report.json` and fix every item in `failure_summary` before writing

**Section order** (omit sections not required for the request size):

1. Executive Summary — one paragraph: what it is, who it is for, why it matters
2. **Assumptions & Open Questions** — list every default applied and every `ambiguities[]` entry from problem.json. This section comes second so reviewers see it immediately. Prefix each invented value with `[assumed]`.
3. Problem Statement — primary goal, user pain point, scope in/out
4. Goals (Medium/Large only)
5. Functional Requirements
6. Non-Functional Requirements (Large, or Medium when NFRs are directly affected)
7. Constraints
8. Traceability Matrix (Large, or Medium when GOAL count > 2)
9. Testing Strategy
10. Acceptance Summary

**Pipeline leakage rule:** Do **not** include a "Dependencies" section that lists downstream pipeline stages (Stage 2, Stage 3, etc.). The PRD describes the product, not the pipeline. Only list real pre-existing product dependencies (an API, a third-party service, an existing feature this change requires). If there are none, omit the section entirely.

### Step 4a — PRD Confidence Check (loop, max 3 attempts)
```bash
python .agents/skills/stage-1-prd/verify/prd_final_check.py \
  .agents/artifacts/stage-1/prd_final.md \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-1/problem.json
```
- Exit 0 (score ≥ 85%) → continue to done
- Exit non-zero (score < 85%) → read `prd_check_report.json`, address every item in `failure_summary`, recompile `prd_final.md` (Step 4), re-run this check
- If score < 85% after **3 attempts** → **HALT** — report the failure report contents in chat, do not proceed

## Outputs

| Artifact | Path |
|---|---|
| Problem statement | `.agents/artifacts/stage-1/problem.json` |
| Goals & requirements | `.agents/artifacts/stage-1/goals.json` |
| Final PRD document | `.agents/artifacts/stage-1/prd_final.md` |
| PRD confidence report | `.agents/artifacts/stage-1/prd_check_report.json` |

## Gate

> Shared conventions (size classification, anti-hallucination rule, traceability chain, pipeline leakage rule): see `.agents/skills/STAGE-CONVENTIONS.md`.

**Step 3 — JSON structure:**
```bash
python .agents/skills/stage-1-prd/verify/prd_structure.py .agents/artifacts/stage-1/goals.json
```
**Pass criteria:** `problem.json` and `goals.json` valid against schemas; at least one GOAL with success criteria; at least one P0 FR with acceptance criteria; no vague language; ambiguities documented.

**Step 4a — PRD confidence:**
```bash
python .agents/skills/stage-1-prd/verify/prd_final_check.py \
  .agents/artifacts/stage-1/prd_final.md \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-1/problem.json
```
**Pass criteria:** Confidence score ≥ 85% across all required sections present, all IDs traceable, no placeholders, traceability matrix links every GOAL to at least one FR.
