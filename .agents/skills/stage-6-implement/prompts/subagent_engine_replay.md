---
name: "Implementation - Engine & Replay (Sub-agent)"
description: "Sub-agent for implementing core game engine and replay system components"
prompt_version: "2026-05-09"
---

# Implementation Task: Core Engine & Replay Components

**Subagent Role**: Implement Group A + B components for Snake game
- Group A: GridState, SnakeEngine, CollisionDetector, FoodSpawner, GameState
- Group B: InputHandler, StateSerializer, ReplayRecorder, ReplayEngine

## Context

- **Tech Stack**: {{tech_stack_json}}
- **Components Contract**: {{components_json}}
- **Tasks to Execute**: All T-3 through T-23 from {{tasks_json}}
- **Architecture Reference**: {{components_json}}

## Acceptance Criteria

✅ All source files created under `src/`:
- `src/engine/GridState.ts` - Snake and food state management
- `src/engine/SnakeEngine.ts` - Movement logic
- `src/engine/CollisionDetector.ts` - Collision detection
- `src/engine/FoodSpawner.ts` - Random food placement
- `src/engine/GameState.ts` - Score, speed, status tracking
- `src/input/InputHandler.ts` - Keyboard buffering
- `src/replay/StateSerializer.ts` - JSON serialization
- `src/replay/ReplayRecorder.ts` - State recording & persistence
- `src/replay/ReplayEngine.ts` - Replay playback

✅ All code:
- Follows TypeScript strict mode
- Matches component interfaces from `{{components_json}}`
- Includes JSDoc comments on public methods
- Compiles without errors: `tsc -b`

✅ All unit tests created and passing:
- `tests/engine/*.test.ts` - Engine component tests
- `tests/input/*.test.ts` - Input handler tests
- `tests/replay/*.test.ts` - Replay system tests
- Command: `npm test` exits 0

## Requirements (from PRD Goals)

**GOAL-1: Core Game Engine**
- Snake moves in response to arrow keys (FR-1)
- Snake grows when eating food (FR-3)
- Food spawns at random empty cells (FR-3)
- Collision detection for walls and self-body (FR-2)
- Score increments per food (FR-4)
- Speed increases with growth (FR-5)

**GOAL-2: Replay System**
- State serialization capturing all game states (FR-6)
- Replay playback at variable speeds 0.5×/1×/2×/4× (FR-7)
- Ghost snake rendering (FR-8)
- Bit-exact replay verification (FR-10)

**GOAL-3: Input Handling**
- Direction buffering for rapid key presses (FR-1)
- Prevent reverse direction in single move (FR-11)

## Implementation Strategy

1. **Start with types** (`src/types.ts` - already done)
2. **Implement engines in order of dependency**:
   - GridState (no dependencies)
   - SnakeEngine (depends on GridState, types)
   - CollisionDetector (depends on GridState, types)
   - FoodSpawner (depends on GridState, types)
   - GameState (depends on types)
3. **Implement input layer**:
   - InputHandler (depends on SnakeEngine, types)
4. **Implement replay layer**:
   - StateSerializer (depends on GridState, GameState, types)
   - ReplayRecorder (depends on StateSerializer, types)
   - ReplayEngine (depends on types)

## Testing Approach

After implementing each component, create corresponding test file:
- Test state creation and modification
- Test move logic and direction changes
- Test collision detection (walls, self, food)
- Test food spawning distribution
- Test input buffering and direction validation
- Test serialization round-trips
- Test replay accuracy

## Definition of Done

1. ✅ All 9 component files created
2. ✅ All 9 test files created and passing
3. ✅ No TypeScript compilation errors
4. ✅ Code matches architecture interfaces
5. ✅ All comments/documentation complete
6. ✅ Ready for sub-agent 2 (rendering/UI) to depend on these exports
