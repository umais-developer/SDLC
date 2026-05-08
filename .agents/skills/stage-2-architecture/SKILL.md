---
name: stage-2-architecture
description: |
  Design the technology stack and component structure for the project.
  Detects machine capabilities, selects tech stack following opinion documents,
  and designs component interfaces. Outputs tech_stack.json, components.json,
  and architecture_final.md to .agents/artifacts/stage-2/.
  Can be invoked independently after Stage 1 is complete.
---

# Stage 2: Architecture Design

You are a Solutions Architect. Design the technical approach, component structure, and data flow for the project described in the PRD.

## Independent Invocation

To run this stage alone (requires Stage 1 artifacts):
```
Follow instructions in #file:.agents/skills/stage-2-architecture/SKILL.md
```

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |
| `{{machine_capabilities_json}}` | Full contents of `.agents/artifacts/stage-2/capabilities.json` (produced by Step 1 below) |
| `{{codebase_context}}` | List all files under `src/` with their line counts. If `src/` does not exist, use `"No existing codebase"` |
| `{{tech_stack_json}}` | Full contents of `.agents/artifacts/stage-2/tech_stack.json` (available after Step 2) |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

## Tech Stack Opinion Documents

When selecting stacks, reference these files in `.agents/skills/stage-2-architecture/tech-stack-opinions/`:
- `spa-opinion.md` → React, Vue, TypeScript, Vite
- `dotnet-opinion.md` → ASP.NET Core 8.0+
- `python-opinion.md` → FastAPI or Django
- `java-opinion.md` → Spring Boot 3.2+

## Execution Steps

### Step 1 — Detect Machine Capabilities
```bash
python3 .agents/scripts/detect_capabilities.py .agents/artifacts/stage-2/capabilities.json
```
- Creates `.agents/artifacts/stage-2/capabilities.json`
- If this fails, flag as a warning and continue — capabilities will be unknown

### Step 2 — Tech Stack Review
- Load prompt: `.agents/skills/stage-2-architecture/prompts/tech_stack_review.md`
- Substitute: `{{goals_json}}`, `{{machine_capabilities_json}}`, `{{codebase_context}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-2/tech_stack.json`

### Step 3 — Component Design
- Load prompt: `.agents/skills/stage-2-architecture/prompts/component_design.md`
- Substitute: `{{tech_stack_json}}`, `{{goals_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-2/components.json`

### Step 4 — Verify Gate
```bash
python .agents/skills/stage-2-architecture/verify/architecture_completeness.py .agents/artifacts/stage-2/components.json
```
- Exit non-zero → **HALT** — report the specific error, do not proceed
- Exit 0 → continue

### Step 5 — Compile Final Architecture Document
- Combine `tech_stack.json` + `components.json` into `.agents/artifacts/stage-2/architecture_final.md`
- Include: component dependency graph, layer boundaries, SOLID assessment, stack justifications

## Outputs

| Artifact | Path |
|---|---|
| Machine capabilities | `.agents/artifacts/stage-2/capabilities.json` |
| Tech stack decision | `.agents/artifacts/stage-2/tech_stack.json` |
| Component design | `.agents/artifacts/stage-2/components.json` |
| Final architecture doc | `.agents/artifacts/stage-2/architecture_final.md` |

## Gate

```bash
python .agents/skills/stage-2-architecture/verify/architecture_completeness.py .agents/artifacts/stage-2/components.json
```

**Pass criteria:** Valid JSON, all components have file paths under `src/`, no circular dependencies, every component has a public interface and justification.
