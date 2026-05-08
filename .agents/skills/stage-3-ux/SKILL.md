---
name: stage-3-ux
description: |
  Map out user flows, UI states, error paths, and accessibility requirements.
  Outputs flows.json and ux_final.md to .agents/artifacts/stage-3/.
  Can be invoked independently after Stages 1 and 2 are complete.
---

# Stage 3: UX Design

You are a UX Designer. Define every path a user can take through the feature — happy path, error path, and edge cases. You design flows and states, not visual layouts.

## Independent Invocation

To run this stage alone (requires Stage 1 and 2 artifacts):
```
Follow instructions in #file:.agents/skills/stage-3-ux/SKILL.md
```

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |
| `{{components_json}}` | Full contents of `.agents/artifacts/stage-2/components.json` |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

## Execution Steps

### Step 1 — User Flow Mapping
- Load prompt: `.agents/skills/stage-3-ux/prompts/user_flows.md`
- Substitute: `{{goals_json}}`, `{{components_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-3/flows.json`

### Step 2 — Verify Gate
```bash
python .agents/skills/stage-3-ux/verify/flows_structure.py .agents/artifacts/stage-3/flows.json .agents/artifacts/stage-1/goals.json
```
- Exit non-zero → **HALT** — report the specific error, do not proceed
- Exit 0 → continue

### Step 3 — Compile Final UX Document
- Compile `flows.json` into `.agents/artifacts/stage-3/ux_final.md`
- Include: state diagram, flow descriptions, accessibility requirements, error paths

## Outputs

| Artifact | Path |
|---|---|
| User flows | `.agents/artifacts/stage-3/flows.json` |
| Final UX document | `.agents/artifacts/stage-3/ux_final.md` |

## Gate

```bash
python .agents/skills/stage-3-ux/verify/flows_structure.py .agents/artifacts/stage-3/flows.json .agents/artifacts/stage-1/goals.json
```

**Pass criteria:** All P0 FRs have at least one flow, every flow has steps, error_paths, keyboard_path, and links_to. At least one UI state defined.
