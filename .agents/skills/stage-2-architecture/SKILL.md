---
name: stage-2-architecture
description: |
  Design the technology stack and component structure for the project.
  Size-aware: Trivial changes produce a one-paragraph impact note; Medium changes
  produce components.json + brief rationale; Large/greenfield changes run the full
  tech-stack review, component graph, and design-principles assessment.
  Outputs tech_stack.json, components.json, and architecture_final.md to
  .agents/artifacts/stage-2/. Can be invoked independently after Stage 1 is complete.
---

# Stage 2: Architecture Design

You are a Solutions Architect. Design the technical approach, component structure, and data flow for the project described in the PRD.

## Independent Invocation

Requires Stage 1 artifacts. Pick the form that matches your environment:

- **Claude Code:** `/stage-2`
- **GitHub Copilot:** `Follow instructions in #file:.agents/skills/stage-2-architecture/SKILL.md`
- **Other agents:** Read this file and follow it.

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` |
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |
| `{{codebase_context}}` | List all files under `src/` with their line counts. If `src/` does not exist, use `"No existing codebase"` |
| `{{machine_capabilities_json}}` | Full contents of `.agents/artifacts/stage-2/capabilities.json` (produced by Step 1, only when needed) |
| `{{tech_stack_json}}` | Full contents of `.agents/artifacts/stage-2/tech_stack.json` (available after Step 2) |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

---

## Request Sizing

**Before executing Step 1**, read the `size` field from `problem.json` (set by Stage 1). If the field is absent, **default to whatever size Stage 1 used** — use the same classification rather than re-deriving it from architectural criteria the PRD does not directly answer.

| Size | Architecture work required |
|------|---------------------------|
| **Trivial** | One-paragraph impact note only. No components.json, no tech_stack.json. Skip to Step 5 (compile) then Step 4 (Trivial gate). |
| **Medium** | Codebase inspection (Step 2a), components.json (Step 3). Skip full tech-stack selection unless codebase is greenfield. |
| **Large / Greenfield** | Full execution: capability detection (Step 1), tech-stack selection (Step 2b), components.json (Step 3). |

**Execution order note:** Trivial runs Step 5 (compile) before Step 4 (gate). Medium/Large runs Step 4 (gate) before Step 5 (compile).

When in doubt, default to **Medium**.

---

> Shared conventions (size classification, anti-hallucination rule, traceability chain, pipeline leakage rule): see `.agents/skills/STAGE-CONVENTIONS.md`.

**Stage 2 specialization of the anti-hallucination rule:** every justification in `tech_stack.json` and `components.json` must cite a specific `FR-X`, `NFR-Y`, or `CON-Z` ID from `goals.json`. Generic technology virtues are prohibited.
- **Do not write:** "Vanilla JS chosen for simplicity" / "TypeScript for type safety" / "React for its component model."
- **Do write:** "Vanilla JS with no build step selected because CON-1 forbids a server-side runtime and the PRD requires static deployment" / "Web Workers selected because NFR-1 requires the UI thread to remain unblocked during large-list filtering."
- If the justification reads the same regardless of what the project does, delete it.

---

## Tech Stack Opinion Documents

The following opinion documents are **advisory inputs, not the universe of valid choices**. Referencing one is appropriate only when the project genuinely uses that stack. "None of these — pick something else with justification" is always valid.

| If the project is... | Use |
|---|---|
| A browser SPA with a build step (React, Vue, Svelte, TypeScript + Vite) | `spa-opinion.md` |
| An ASP.NET Core web API or server-rendered app | `dotnet-opinion.md` |
| A Python web service (FastAPI, Django, Flask) | `python-opinion.md` |
| A Java/Kotlin backend (Spring Boot) | `java-opinion.md` |
| A static HTML page, a vanilla JS app, a CLI tool, a shell script, a no-build-tool game | **None** — document the minimal stack directly; do not force one of the four profiles |

For the "None" category, justify the stack choice by citing the PRD requirement that makes a build tool or framework unnecessary or counterproductive (e.g., `CON-1: static deployment only`).

Files:
- `.agents/skills/stage-2-architecture/tech-stack-opinions/spa-opinion.md`
- `.agents/skills/stage-2-architecture/tech-stack-opinions/dotnet-opinion.md`
- `.agents/skills/stage-2-architecture/tech-stack-opinions/python-opinion.md`
- `.agents/skills/stage-2-architecture/tech-stack-opinions/java-opinion.md`

---

## Execution Steps

### Step 1 — Capability Detection (Large / Greenfield only)

Skip this step for Trivial and Medium requests unless `{{codebase_context}}` is `"No existing codebase"`.

```bash
python .agents/scripts/detect_capabilities.py .agents/artifacts/stage-2/capabilities.json
```

**What this output is used for** (only these decisions — no others):
- Is the required runtime available locally to run the dev environment? (blocker check)
- Should we recommend a lightweight vs. full toolchain? (e.g., no Docker if Docker is absent and the project doesn't require it)

**Do not use capabilities.json to justify stack choices.** Stack decisions must be driven by PRD requirements, not by what happens to be installed on the developer's machine.

If this step fails, flag as a warning and continue — capabilities will be unknown.

---

### Step 2 — Tech Stack Handling

**Branch on codebase context:**

#### Step 2a — Existing Codebase (Medium or Large with `src/` present)
- Load prompt: `.agents/skills/stage-2-architecture/prompts/tech_stack_review.md`
- **Mode:** `inspection` — read and document the existing stack; do not propose changing it
- Identify the framework, language, build tool, and test runner already in use
- Note any mismatches with opinion documents as **advisory only** — flag but do not override
- Substitute: `{{goals_json}}`, `{{codebase_context}}`
- Write output to: `.agents/artifacts/stage-2/tech_stack.json` — **this file is required for Step 5; if this step is skipped or fails, Step 5 must note that stack information is unavailable**

#### Step 2b — Greenfield (Large with `"No existing codebase"`)
- Load prompt: `.agents/skills/stage-2-architecture/prompts/tech_stack_review.md`
- **Mode:** `selection` — evaluate and choose the appropriate stack
- Substitute: `{{goals_json}}`, `{{machine_capabilities_json}}`, `{{codebase_context}}`
- Write output to: `.agents/artifacts/stage-2/tech_stack.json`

**Trivial requests:** Skip Step 2 entirely.

---

### Step 3 — Component Design (Medium and Large only)

- Load prompt: `.agents/skills/stage-2-architecture/prompts/component_design.md`
- Substitute: `{{tech_stack_json}}`, `{{goals_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-2/components.json`

**Required in every component entry:**
- `fr_links`: list of FR/NFR IDs this component implements (at least one; reference `goals.json`)
- `modified`: `true` if the component already exists and is being changed; omit for new components
- `public_interface`: at minimum one method or property signature
- `justification`: one sentence citing a specific `FR-X`, `NFR-Y`, `CON-Z`, or `GOAL-X`

**Trivial requests:** Skip Step 3 entirely.

---

### Step 4 — Verify Gate

**Medium / Large:** run the gate now (after Step 3).

```bash
python .agents/skills/stage-2-architecture/verify/architecture_completeness.py \
  .agents/artifacts/stage-2/components.json \
  .agents/artifacts/stage-1/goals.json
```

**Trivial:** run the gate **after Step 5** so `architecture_final.md` exists.

```bash
python .agents/skills/stage-2-architecture/verify/architecture_completeness.py \
  --trivial
```

- For **Trivial** requests: pass `--trivial` flag; script checks that `architecture_final.md` exists, is non-empty, names at least one file path, and cites at least one FR/NFR/CON/GOAL ID
- Exit non-zero → **HALT** — report the specific error, do not proceed
- Exit 0 → continue

---

### Step 5 — Compile Final Architecture Document

Combine artifacts into `.agents/artifacts/stage-2/architecture_final.md`.

**Format is size-dependent:**

#### Trivial format

**Source:** Read `goals.json` and `codebase_context` directly — there are no upstream artifacts from Steps 1–3 to compile.

Write one section only:
- **Impact note** — which existing file(s) are touched (cite by path), what is added or changed (one sentence), and a one-line interface sketch for any new function or method introduced. Cite at least one FR/NFR/CON/GOAL ID. No component graph, no stack justification, no design principles.

**For Trivial requests:** run Step 5 **before** Step 4 so the gate can validate the compiled document.

#### Medium format
Sections in order:
1. **Stack** — one-paragraph confirmation of existing stack (from Step 2a inspection)
2. **New / Modified Components** — list with file path, one-sentence responsibility, public interface sketch, and FR/NFR/CON IDs from `goals.json` that it serves
3. **Data Flow** — bullet steps showing how data moves through the new path; omit section if the flow is trivially obvious from the component list
4. **Constraints Violated or At Risk** — list only CON/NFR IDs the design cannot fully satisfy; omit section if all constraints are met (silence implies compliance)
5. **Risks & Open Questions** — only genuine ones; omit section if none

#### Large / Greenfield format
All Medium sections, plus:
- **Tech Stack Decision** — framework, build tool, test runner, with FR/NFR-cited justifications
- **Component Dependency Graph** — table or ASCII diagram
- **Layer Boundaries** — table of layers and what may/may not cross them
- **Design Principles Assessment** — only when the design introduces **4+ modules with non-trivial interactions**; name the principles actually relevant to this design (not always SOLID); skip if the feature is primarily library composition
- **Testing Strategy** — unit, integration, e2e test descriptions per component

**Pipeline leakage rule:** Do not reference Stage 3, Stage 4, or other pipeline stages in the architecture doc. Only reference real product dependencies.

---

## Outputs

| Artifact | Size | Path |
|---|---|---|
| Machine capabilities | Large/Greenfield only | `.agents/artifacts/stage-2/capabilities.json` |
| Tech stack | Medium (inspection) / Large (selection) | `.agents/artifacts/stage-2/tech_stack.json` |
| Component design | Medium + Large | `.agents/artifacts/stage-2/components.json` |
| Final architecture doc | All sizes | `.agents/artifacts/stage-2/architecture_final.md` |

---

## Gate

**Medium / Large:**

```bash
python .agents/skills/stage-2-architecture/verify/architecture_completeness.py \
  .agents/artifacts/stage-2/components.json \
  .agents/artifacts/stage-1/goals.json
```

**Trivial:**

```bash
python .agents/skills/stage-2-architecture/verify/architecture_completeness.py \
  --trivial
```

**Pass criteria (Medium / Large):**
- Valid JSON, all new (non-`modified`) component file paths under `src/`
- Every new component has at least one entry in `public_interface`
- Every component (new or modified) has at least one `fr_links` entry that matches an ID in `goals.json`
- No component `justification` that contains zero FR/NFR/CON/GOAL ID references
- `tech_stack.json` exists (produced by Step 2a or 2b); if absent, **HALT** with message: "Step 2 did not produce tech_stack.json — re-run Step 2 before proceeding"

**Pass criteria (Trivial):**
- `architecture_final.md` exists, is non-empty, names at least one file path, and cites at least one FR/NFR/CON/GOAL ID
