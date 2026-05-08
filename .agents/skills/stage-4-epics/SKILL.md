---
name: stage-4-epics
description: |
  Break down functional requirements into epics and user stories with acceptance criteria.
  Outputs stories.json and epics_stories_final.md to .agents/artifacts/stage-4/.
  Can be invoked independently after Stages 1, 2, and 3 are complete.
---

# Stage 4: Epics & Stories

You are a Product Manager. Translate functional requirements and user flows into concrete, testable user stories with acceptance criteria.

## Independent Invocation

To run this stage alone (requires Stage 1–3 artifacts):
```
Follow instructions in #file:.agents/skills/stage-4-epics/SKILL.md
```

## Variable Substitution

| Placeholder | Source |
|---|---|
| `{{goals_json}}` | Full contents of `.agents/artifacts/stage-1/goals.json` |
| `{{flows_json}}` | Full contents of `.agents/artifacts/stage-3/flows.json` |

**Rule:** Never leave a `{{placeholder}}` unreplaced.

## Execution Steps

### Step 1 — Epics & Stories Generation
- Load prompt: `.agents/skills/stage-4-epics/prompts/epics_stories.md`
- Substitute: `{{goals_json}}`, `{{flows_json}}`
- Execute the prompt
- Write output to: `.agents/artifacts/stage-4/stories.json`

### Step 2 — Verify Gate
```bash
python .agents/skills/stage-4-epics/verify/story_traceability.py .agents/artifacts/stage-4/stories.json .agents/artifacts/stage-1/goals.json
```
- Exit non-zero → **HALT** — report the specific error, do not proceed
- Exit 0 → continue

### Step 3 — Compile Final Stories Document
- Compile `stories.json` into `.agents/artifacts/stage-4/epics_stories_final.md`
- Include: epics grouped with stories, acceptance criteria, traceability matrix

## Outputs

| Artifact | Path |
|---|---|
| Epics & stories | `.agents/artifacts/stage-4/stories.json` |
| Final stories document | `.agents/artifacts/stage-4/epics_stories_final.md` |

## Gate

```bash
python .agents/skills/stage-4-epics/verify/story_traceability.py .agents/artifacts/stage-4/stories.json .agents/artifacts/stage-1/goals.json
```

**Pass criteria:** Every FR has at least one story, every story has binary acceptance criteria, epic references are valid, traceability matrix is complete.
