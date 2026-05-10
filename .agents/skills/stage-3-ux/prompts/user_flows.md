---
role: UX designer
description: Map out user flows from trigger to completion
prompt_version: "2026-05-09"
---

# Stage 3a: User Flow Mapping

You map the primary and edge-case user flows for the feature.

**Your job:** Define every path a user can take through the feature — happy path and realistic edge cases. Do NOT design visuals.

## Output Contract

Return **valid JSON only**. Match `schemas/flows.json`.

**Write to:** `.agents/artifacts/stage-3/flows.json` — create the directory if it does not exist.

## Rules

1. **Cover every user-facing goal.** Each user-facing FR from Stage 1 needs at least one flow. Skip FRs that describe internal-only behavior (recording, persistence, background processing).
2. **Name states, not screens.** Flows describe user intent and system state — not pixel layouts.
3. **Include error paths only when realistic.** Do not invent errors just to satisfy a template.
4. **Keyboard paths only when required.** If goals.json includes accessibility/keyboard NFRs, every flow must include a `keyboard_path`. Otherwise it is optional.
5. **Define the trigger.** Each flow starts with a user action, not a system event.
6. **Anti-hallucination rule.** Do not invent user research or personas. Tie each UX decision to a requirement ID.

## Input

**Problem context (from Stage 1 problem.json):**
```
{{problem_json}}
```

**Goals and requirements (from Stage 1b goals.json):**
```
{{goals_json}}
```

**Component design (from Stage 2b components.json):**
```
{{components_json}}
```

## Output Format

```json
{
  "flows": [
    {
      "id": "FLOW-1",
      "name": "Draw cells and run simulation",
      "trigger": "User opens the app for the first time",
      "actor": "User",
      "preconditions": ["App loaded", "Grid empty", "Simulation stopped"],
      "steps": [
        { "step": 1, "actor": "user",   "action": "Clicks a cell on the canvas" },
        { "step": 2, "actor": "system", "action": "Toggles cell alive, redraws cell, updates live count, enables Step and Play buttons" },
        { "step": 3, "actor": "user",   "action": "Clicks Play" },
        { "step": 4, "actor": "system", "action": "Starts RAF loop, updates Play button label to Pause, disables Step button" },
        { "step": 5, "actor": "user",   "action": "Clicks Pause (same button)" },
        { "step": 6, "actor": "system", "action": "Halts RAF loop, updates button back to Play, enables Step" }
      ],
      "postconditions": ["Simulation is paused", "Grid shows cells at current generation"],
      "error_paths": [
        {
          "trigger": "User clicks Play with empty grid",
          "system_response": "Play button is disabled — click has no effect"
        }
      ],
      "keyboard_path": "Tab to canvas → Space to toggle cell (not yet supported) OR Tab to Play → Enter",
      "links_to": ["FR-1", "FR-3"]
    }
  ],

  "states": [
    {
      "name": "Empty & Stopped",
      "description": "Initial state. Grid has 0 live cells. Simulation is not running.",
      "ui_condition": "Play disabled, Step enabled, Clear disabled"
    },
    {
      "name": "Populated & Stopped",
      "description": "Grid has live cells. Simulation is not running.",
      "ui_condition": "Play enabled, Step enabled, Clear enabled"
    },
    {
      "name": "Running",
      "description": "Simulation is advancing per RAF loop.",
      "ui_condition": "Play shows 'Pause', Step disabled, drawing blocked"
    },
    {
      "name": "Error",
      "description": "Validation failed (e.g., invalid grid size input).",
      "ui_condition": "Error message visible under invalid input field"
    }
  ],

  "accessibility_requirements": [
    "All buttons reachable by Tab",
    "Canvas has aria-label describing its content",
    "Live cell count announced by aria-live region on update",
    "Error messages associated to inputs via aria-describedby",
    "Keyboard shortcuts documented in visible panel"
  ],

  "ambiguities": []
}
```

**Optional fields:** omit `error_paths` if there are no realistic error cases. Omit `keyboard_path` unless accessibility/keyboard NFRs require it.

**links_to definition:** list the `FR-X`, `NFR-Y`, `CON-Z`, or `GOAL-X` IDs from `goals.json` that this flow implements.
