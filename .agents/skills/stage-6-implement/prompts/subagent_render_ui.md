---
name: "Implementation - Rendering & UI (Sub-agent)"
description: "Sub-agent for implementing rendering and UI controller components"
prompt_version: "2026-05-09"
---

# Implementation Task: Rendering & UI Components

**Subagent Role**: Implement Group C components for Snake game
- Group C: CanvasRenderer, TickScheduler, UIController

## Context

- **Tech Stack**: {{tech_stack_json}}
- **Components Contract**: {{components_json}}
- **Tasks to Execute**: T-21, T-23, T-25, T-26 from {{tasks_json}}
- **Architecture Reference**: {{components_json}}
- **Dependencies**: Group A & B must be completed first (engine/input/replay modules)

## Acceptance Criteria

✅ All source files created under `src/`:
- `src/render/CanvasRenderer.ts` - Canvas rendering engine
- `src/ui/TickScheduler.ts` - Game loop scheduler
- `src/ui/UIController.ts` - Central event and game flow orchestration
- `src/ui/ReplayListUI.ts` - Replay selection interface

✅ All code:
- Follows TypeScript strict mode
- Matches component interfaces from `{{components_json}}`
- Imports all engine/input/replay modules correctly
- Includes JSDoc comments on public methods
- Compiles without errors when engine/input/replay modules exist

✅ All unit tests created and passing:
- `tests/render/CanvasRenderer.test.ts` - Canvas drawing tests
- `tests/ui/TickScheduler.test.ts` - Game loop timing tests
- `tests/ui/UIController*.test.ts` - UI event handling tests

✅ Canvas rendering:
- Draws 30×30 grid with 10px cells
- Snake rendered in green (head bright, body darker)
- Food rendered in red
- Ghost snake rendered faded (50% opacity) in blue
- Grid lines visible

## Requirements (from PRD Goals)

**GOAL-1: Game UI Controls (FR-12)**
- New Game button initializes fresh game
- Pause button freezes game state
- Resume button continues from paused state
- Stop button returns to menu
- View Replays button shows replay list

**GOAL-2: Canvas Rendering (FR-8, FR-9)**
- Render live snake on grid
- Render food on grid
- Render ghost snake during replay
- No collision logic between live and ghost
- Live and ghost coexist on same canvas

**GOAL-3: Game Loop (FR-1)**
- RAF-based tick scheduling
- Target 60 FPS render, game ticks at variable speed
- Pause/resume without losing state
- Step one tick at a time when paused

## Implementation Strategy

1. **CanvasRenderer (no dependencies)**
   - Canvas element setup
   - Grid drawing
   - Snake/food/ghost rendering
   - Pixel-to-grid conversion for inputs

2. **TickScheduler (no dependencies)**
   - RAF loop management
   - FPS targeting
   - Pause/resume mechanics

3. **UIController (depends on everything else)**
   - Wire DOM buttons to game logic
   - Coordinate SnakeEngine, InputHandler, Renderer, Scheduler
   - Manage game state transitions
   - Handle keyboard input

4. **ReplayListUI (depends on UIController, ReplayRecorder)**
   - Display saved replays
   - Provide selection and delete UI

## Testing Approach

- Test canvas operations (mock canvas context)
- Test RAF scheduling accuracy
- Test button state transitions
- Test keyboard input routing
- Test game loop execution

## Definition of Done

1. ✅ All 4 component files created
2. ✅ All test files created and passing
3. ✅ No TypeScript compilation errors
4. ✅ Canvas renders correctly (can be tested manually)
5. ✅ UI buttons functional
6. ✅ Ready for entry point (HTML/CSS/main.ts)
