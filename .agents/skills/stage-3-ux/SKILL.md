---
name: stage-3-ux
description: |
  Map out user flows, UI states, error paths, and accessibility requirements.
  Outputs flows.json and ux_final.md to .agents/artifacts/stage-3/.
  Can be invoked independently after Stages 1 and 2 are complete.
---

# Stage 3: UX Design

You are a UX Designer. Define every path a user can take through the feature — happy path, error path, and edge cases. You design flows and states, not visual layouts.

Stage 3 outputs cover: user flows, UI states (including empty/loading/error), interaction patterns (keyboard/pointer/touch as relevant), and microcopy for system messages. Visual design — layout, typography, colors — is out of scope.

## Independent Invocation

To run this stage alone (requires Stage 1 and 2 artifacts):
```
Follow instructions in #file:.agents/skills/stage-3-ux/SKILL.md
```

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{problem_json}}` | Full contents of `.agents/artifacts/stage-1/problem.json` |
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |
| `{{components_json}}` | Full contents of `.agents/artifacts/stage-2/components.json` |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

---

## Request Sizing

**Before executing Step 1**, read the `size` field from `problem.json` (set by Stage 1). If the field is absent, **default to whatever size Stage 1 used** — use the same classification rather than re-deriving it from UX criteria the PRD does not directly answer.

| Size | UX work required |
|------|-----------------|
| **Trivial** | Brief flow note only. No flows.json. Skip to Step 3 (compile) then Step 2 (Trivial gate). |
| **Medium** | Standard flows.json with realistic error paths and accessibility where required. Compile ux_final.md (state diagram conditional). |
| **Large** | Full flows.json with comprehensive states, accessibility requirements, and error paths. Compile ux_final.md with state diagram. |

**Execution order note:** Trivial runs Step 3 (compile) before Step 2 (gate). Medium/Large runs Step 2 (gate) before Step 3 (compile).

When in doubt, default to **Medium**.

---

> Shared conventions (size classification, anti-hallucination rule, traceability chain, pipeline leakage rule): see `.agents/skills/STAGE-CONVENTIONS.md`.

**Stage 3 specialization of the anti-hallucination rule:** do not invent user research, personas, or "user expectations." Every UX decision must cite a specific requirement.
- **Do not write:** "Users expect instant feedback" / "Research shows users abandon forms after 3 seconds" / "The standard mental model is..."
- **Do write:** "Real-time filtering on every keystroke per FR-2" / "Empty state per FR-3" / "Keyboard-only operation per NFR-2 (WCAG 2.1 AA)."

**Pipeline leakage rule:** do not reference Stage 4 epics or Stage 5 implementation tasks in `ux_final.md`. Only reference product requirements.
- **Do write:** user-visible behavior and system responses tied to FR/NFR/CON IDs.

## Execution Steps

### Step 1 — User Flow Mapping (Medium and Large only)
- Load prompt: `.agents/skills/stage-3-ux/prompts/user_flows.md`
- Substitute: `{{problem_json}}`, `{{goals_json}}`, `{{components_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-3/flows.json`
- Skip FRs that are not user-facing (if `goals.json` includes `user_facing: false`, or the FR describes internal-only behavior)
- If **all** P0 FRs are non-user-facing, skip flows.json and use Trivial format in Step 3 (note the feature is non-user-facing and cite the FR IDs)

**Required in every flow entry (Medium/Large):**
- `links_to`: list of `FR-X`, `NFR-Y`, `CON-Z`, or `GOAL-X` IDs from `goals.json` that this flow implements
- `error_paths`: include only when realistic; omit if none
- `keyboard_path`: required **only** if `goals.json` contains accessibility/keyboard NFRs; otherwise optional

### Step 2 — Verify Gate
**Medium / Large:**
```bash
python .agents/skills/stage-3-ux/verify/flows_structure.py .agents/artifacts/stage-3/flows.json .agents/artifacts/stage-1/goals.json
```

**Trivial:**
```bash
python .agents/skills/stage-3-ux/verify/flows_structure.py --trivial .agents/artifacts/stage-3/ux_final.md
```
- Exit non-zero → **HALT** — report the specific error, do not proceed
- Exit 0 → continue

### Step 3 — Compile Final UX Document
- Compile into `.agents/artifacts/stage-3/ux_final.md`

**Trivial format**
- One paragraph: brief flow note covering user-visible behavior only, with at least one FR/NFR/CON/GOAL ID cited
- No flows.json, no state diagram

**Medium format**
- Summarize each flow with its linked FR/NFR/CON IDs
- Define UI states including empty/loading/error where applicable
- Include accessibility requirements **only** when required by goals.json
- Include a state diagram **only if** there are more than 3 states

**Large format**
- Full flow descriptions and realistic error paths
- UI states with transitions and conditions
- Accessibility requirements section
- State diagram required

**State diagram format:** any text-renderable format (Mermaid preferred; ASCII acceptable). Do not specify visual styling.

## Outputs

| Artifact | Path |
|---|---|
| User flows (Medium/Large only) | `.agents/artifacts/stage-3/flows.json` |
| Final UX document (all sizes) | `.agents/artifacts/stage-3/ux_final.md` |

## Gate

**Medium / Large:**

```bash
python .agents/skills/stage-3-ux/verify/flows_structure.py .agents/artifacts/stage-3/flows.json .agents/artifacts/stage-1/goals.json
```

**Trivial:**

```bash
python .agents/skills/stage-3-ux/verify/flows_structure.py --trivial .agents/artifacts/stage-3/ux_final.md
```

**Pass criteria (Medium / Large):**
- All P0 user-facing FRs have at least one flow
- Every flow has `steps` and `links_to`, and every `links_to` entry resolves to an ID in `goals.json`
- `error_paths` present only when realistic (may be omitted)
- `keyboard_path` required only when accessibility/keyboard NFRs are present in `goals.json`
- UI states defined (more than one when multiple states exist)

**Pass criteria (Trivial):**
- `ux_final.md` exists, is non-empty, cites at least one FR/NFR/CON/GOAL ID, and describes at least one user action plus system response
