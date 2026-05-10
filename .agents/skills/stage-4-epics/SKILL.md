---
name: stage-4-epics
description: |
  Break down functional requirements into epics and user stories with acceptance criteria.
  Outputs stories.json and epics_stories_final.md to .agents/artifacts/stage-4/.
  Can be invoked independently after Stages 1, 2, and 3 are complete.
---

# Stage 4: Epics & Stories

You are a Product Manager. Translate functional requirements and user flows into concrete, testable user stories with acceptance criteria.

Stage 4 outputs cover: decomposition of FRs that span multiple flows/components/criteria into implementation-trackable stories, with full traceability to the FRs, flows, and components they implement. Sequencing recommendations where dependencies exist between stories. Out of scope: re-stating FRs that are already story-grain, inventing personas not present in the PRD, or adding estimates without concrete reference points.

## Independent Invocation

Requires Stage 1–3 artifacts. Pick the form that matches your environment:

- **Claude Code:** `/stage-4`
- **GitHub Copilot:** `Follow instructions in #file:.agents/skills/stage-4-epics/SKILL.md`
- **Other agents:** Read this file and follow it.

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` |
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |
| `{{flows_json}}` | Full contents of `.agents/artifacts/stage-3/flows.json` |
| `{{components_json}}` | Full contents of `.agents/artifacts/stage-2/components.json` |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

---

## Request Sizing

**Before executing Step 1**, read the `size` field from `problem.json` (set by Stage 1). If the field is absent, **default to whatever size Stage 1 used** — use the same classification rather than re-deriving it from delivery criteria the PRD does not directly answer.

| Size | Stage 4 work required |
|------|------------------------|
| **Trivial** | One-paragraph story note only. No stories.json. Skip to Step 3 (compile) then Step 2 (Trivial gate). |
| **Medium** | Generate stories only if at least one FR needs decomposition (see trigger below). If none need decomposition, produce the Trivial note. No traceability matrix. |
| **Large** | Full epics + stories + traceability matrix + sequencing/dependencies. |

**Decomposition trigger (mechanical):** An FR needs decomposition if **any** of the following are true:
- It maps to **2+ flows** in `flows.json` (FR is broader than a single user flow)
- It has **4+ acceptance criteria** in `goals.json`
- It spans **2+ components** in `components.json`

**User-facing FRs (for coverage):** An FR is user-facing if Stage 3 produced at least one flow that links to it. FRs not linked by any flow are treated as non-user-facing for Stage 4 coverage.

If **no FR** meets any trigger, produce the Trivial story note: "Stories not generated — all FRs are story-grain. Implementation tracks against FR IDs directly."

**Execution order note:** Trivial runs Step 3 (compile) before Step 2 (gate). Medium/Large runs Step 2 (gate) before Step 3 (compile).

When in doubt, default to **Medium**.

---

> Shared conventions (size classification, anti-hallucination rule, traceability chain, pipeline leakage rule): see `.agents/skills/STAGE-CONVENTIONS.md`.

**Stage 4 specialization of the anti-hallucination rule:** do not invent personas, research, or generic “standard patterns.” Every story must cite real requirement IDs.
- **Do not write:** "As a power user, I want bulk operations" / "Estimated 5 points based on similar work" / "Standard search pattern applies"
- **Do write:** "As a player viewing replay history (per FR-1), I want to filter by score so I can find specific games" / cite `FR-X`, `NFR-Y`, `CON-Z`, or `GOAL-X` in story links.

**Pipeline leakage rule:** do not reference Stage 5 implementation tasks in stories or `epics_stories_final.md`.
- **Do write:** the user-visible value the story delivers, and cite the requirements that define its scope.

## Execution Steps

### Step 1 — Epics & Stories Generation (Medium/Large when decomposition applies)
- Load prompt: `.agents/skills/stage-4-epics/prompts/epics_stories.md`
- Substitute: `{{problem_json}}`, `{{goals_json}}`, `{{flows_json}}`, `{{components_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-4/stories.json`

**Story requirements (Medium/Large):**
- Each story must cite at least one `FR-X`, `NFR-Y`, `CON-Z`, or `GOAL-X` in `links_to`
- If the story implements a user flow, include `links_to.flow` with the `FLOW-X` ID(s)
- Include `components` with the component name(s) from `components.json`
- Acceptance criteria are binary pass/fail, and a refinement/subset of the linked FR acceptance criteria (bullet list format)
- Do **not** include story points unless explicitly requested by the PRD
- **Epics are optional** and only used when there are **4+ related stories**; otherwise list stories without epics

**Large only:** add `depends_on` per story when dependencies exist, and propose a delivery order.

### Step 2 — Verify Gate
**Medium only:**
```bash
python .agents/skills/stage-4-epics/verify/story_traceability.py \
  .agents/artifacts/stage-4/stories.json \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-3/flows.json \
  .agents/artifacts/stage-2/components.json
```

**Large only (enforce dependencies + matrix):**
```bash
python .agents/skills/stage-4-epics/verify/story_traceability.py \
  .agents/artifacts/stage-4/stories.json \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-3/flows.json \
  .agents/artifacts/stage-2/components.json \
  --require-deps \
  --require-matrix
```

**Trivial:**
```bash
python .agents/skills/stage-4-epics/verify/story_traceability.py --trivial .agents/artifacts/stage-4/epics_stories_final.md
```
- Exit non-zero → **HALT** — report the specific error, do not proceed
- Exit 0 → continue

### Step 3 — Compile Final Stories Document
- Compile into `.agents/artifacts/stage-4/epics_stories_final.md`

**Trivial format**
- One paragraph noting stories are not generated, citing the FR/NFR/CON/GOAL IDs that will track the work. Optionally note the smallest meaningful delivery unit.

**Medium format**
- Stories with acceptance criteria (bullet list) and links to FR/NFR/CON/GOAL IDs
- Optional epics only if 4+ related stories
- No traceability matrix

**Large format**
- Epics grouped with stories (epics required when 4+ stories cluster)
- Acceptance criteria and full links to FR/NFR/CON/GOAL, flow IDs, and components
- Traceability matrix
- Recommended delivery order (based on dependencies)

## Outputs

| Artifact | Path |
|---|---|
| Epics & stories (Medium/Large only) | `.agents/artifacts/stage-4/stories.json` |
| Final stories document (all sizes) | `.agents/artifacts/stage-4/epics_stories_final.md` |

## Gate

**Medium only:**

```bash
python .agents/skills/stage-4-epics/verify/story_traceability.py \
  .agents/artifacts/stage-4/stories.json \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-3/flows.json \
  .agents/artifacts/stage-2/components.json
```

**Large only (enforce dependencies + matrix):**

```bash
python .agents/skills/stage-4-epics/verify/story_traceability.py \
  .agents/artifacts/stage-4/stories.json \
  .agents/artifacts/stage-1/goals.json \
  .agents/artifacts/stage-3/flows.json \
  .agents/artifacts/stage-2/components.json \
  --require-deps \
  --require-matrix
```

**Trivial:**

```bash
python .agents/skills/stage-4-epics/verify/story_traceability.py --trivial .agents/artifacts/stage-4/epics_stories_final.md
```

**Pass criteria (Medium / Large):**
- Every P0 user-facing FR has at least one story
- Every story has at least one `links_to` ID that resolves to `goals.json`
- If a story implements a flow, it cites the `FLOW-X` ID
- Each story cites at least one component from `components.json`
- Acceptance criteria are binary and do not exceed the scope of the linked FRs
- Epic references are valid

**Pass criteria (Large):**
- Dependency graph is acyclic
- Traceability matrix present and consistent

**Pass criteria (Trivial):**
- `epics_stories_final.md` exists, is non-empty, and cites at least one FR/NFR/CON/GOAL ID
