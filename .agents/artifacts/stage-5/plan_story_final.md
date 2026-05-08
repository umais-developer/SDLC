# Stage 5: Implementation Plan - Snake Game with Replay

**Status**: ✅ VERIFIED (64 tasks, acyclic dependency graph)

## Plan Summary

Complete decomposition of 27 user stories into 64 concrete implementation tasks organized in 20 execution phases.

### Execution Phases

#### Phase 1: Infrastructure & Types
- **T-1**: Set up project structure and configuration (npm, TypeScript, Vite, vitest)
- **T-2**: Create types definitions (Direction, SerializedState, ReplayData, ReplayMetadata)

#### Phase 2: Core Engine Implementation
- **T-3**: GridState class (snake array, food position, clone)
- **T-5**: SnakeEngine.move() (direction-based movement, food collision)
- **T-7**: CollisionDetector (wall, self, food collision detection)
- **T-9**: FoodSpawner (random empty cell spawning)
- **T-11**: GameState (score, speed FPS, status, generation)
- **T-13**: InputHandler with buffering and direction validation
- **T-15**: StateSerializer (compact JSON serialization)
- **T-21**: CanvasRenderer (grid, snake, food, ghost rendering)

#### Phase 3: Engine Testing
- **T-4**: Unit test GridState
- **T-6**: Unit test SnakeEngine
- **T-8**: Unit test CollisionDetector
- **T-10**: Unit test FoodSpawner
- **T-12**: Unit test GameState
- **T-14**: Unit test InputHandler
- **T-16**: Unit test StateSerializer
- **T-22**: Unit test CanvasRenderer

#### Phase 4: Replay Layer Implementation
- **T-17**: ReplayRecorder (tick recording, game finalization, localStorage)
- **T-19**: ReplayEngine (playback at variable speeds, pause/resume)

#### Phase 5: Replay Testing
- **T-18**: Unit test ReplayRecorder
- **T-20**: Unit test ReplayEngine

#### Phase 6: Game Loop Scheduler
- **T-23**: TickScheduler (RAF loop, start/pause/resume/step, speed control)

#### Phase 7: Scheduler Testing
- **T-24**: Unit test TickScheduler

#### Phase 8: UI Controller Wiring
- **T-25**: UIController event wiring (buttons, input, rendering coordination)

#### Phase 9: Replay List UI
- **T-26**: ReplayListUI (display list, score, timestamp, delete buttons)

#### Phase 10: Live + Ghost Integration
- **T-27**: Integrate ReplayEngine with live game (simultaneous rendering)

#### Phase 11: Integration & E2E Tests
- **T-28**: Integration test bit-exact replay verification
- **T-29**: E2E test complete game flow
- **T-30**: E2E test replay playback
- **T-31**: E2E test live + ghost coexistence
- **T-32**: E2E test input buffering and direction prevention

#### Phase 12: Feature Implementations (Story Details)
- **T-33**: Snake growth on food
- **T-34**: Speed increase with snake growth (capped at 15 FPS)
- **T-35**: Game lifecycle state transitions
- **T-36**: Pause and Resume buttons
- **T-37**: Stop button
- **T-38**: Delete replay button
- **T-39**: Storage quota handling
- **T-40**: Replay pause/resume
- **T-41**: Ghost snake distinct rendering (faded)
- **T-42**: Isolate collision logic (ghost doesn't affect live)
- **T-43**: Enhance input buffering for rapid keys
- **T-44**: Prevent direction reversal
- **T-45**: Draw live snake and food
- **T-46**: Draw ghost snake on canvas

#### Phase 13: Story-Specific Tests
- **T-47**: Unit test snake growth on food (S-1.2)
- **T-48**: Unit test speed increases with growth (S-2.2)
- **T-49**: Unit test game lifecycle states (S-2.3)
- **T-50**: Unit test pause and resume buttons (S-3.2)
- **T-51**: Unit test stop button (S-3.3)
- **T-52**: Unit test replay list display (S-3.4)
- **T-53**: Unit test delete replay button (S-3.5)
- **T-54**: Unit test storage quota handling (S-4.3)
- **T-55**: Unit test replay pause and resume (S-5.3)
- **T-56**: Unit test ghost snake renders distinct (S-6.1)
- **T-57**: Integration test live and ghost coexist (S-6.2)
- **T-58**: Unit test draw live snake and food (S-8.2)
- **T-59**: Unit test draw ghost snake (S-8.3)

#### Phase 14: Replay Speed & Accuracy
- **T-60**: Implement replay speed controls UI (S-5.2)
- **T-61**: Ensure bit-exact replay accuracy in ReplayEngine (S-5.4)

#### Phase 15: Presentation Layer
- **T-62**: Create HTML and CSS (entry point, styling)

#### Phase 16: Build Verification
- **T-63**: Build verification (npm run build)

#### Phase 17: Test Suite Verification
- **T-64**: Complete test suite verification (all tests pass)

## Dependency Graph

### Critical Path (Longest Dependency Chain)
1. T-1 (setup)
2. T-2 (types)
3. T-5, T-7, T-9, T-11, T-13, T-15, T-21 (core engines)
4. T-17, T-19 (replay layer)
5. T-23 (scheduler)
6. T-25 (UI controller)
7. T-62 (HTML/CSS)
8. T-63 (build)
9. T-64 (tests)

### Key Dependencies
- Engine components (T-3 through T-16) are prerequisite for scheduler (T-23)
- Scheduler is prerequisite for UI controller (T-25)
- ReplayRecorder and ReplayEngine (T-17, T-19) are prerequisite for ReplayListUI (T-26)
- Live/Ghost integration (T-27) requires ReplayEngine
- All integration/E2E tests (T-28 through T-32) require core implementation complete

## File Structure

```
src/
├── types.ts                      [T-2]
├── index.html                    [T-62]
├── style.css                     [T-62]
├── main.ts                       [T-62]
├── engine/
│   ├── GridState.ts              [T-3]
│   ├── SnakeEngine.ts            [T-5]
│   ├── CollisionDetector.ts      [T-7]
│   ├── FoodSpawner.ts            [T-9]
│   └── GameState.ts              [T-11]
├── input/
│   └── InputHandler.ts           [T-13]
├── replay/
│   ├── StateSerializer.ts        [T-15]
│   ├── ReplayRecorder.ts         [T-17]
│   └── ReplayEngine.ts           [T-19]
├── render/
│   └── CanvasRenderer.ts         [T-21]
└── ui/
    ├── TickScheduler.ts          [T-23]
    ├── UIController.ts           [T-25]
    └── ReplayListUI.ts           [T-26]

tests/
├── engine/
│   ├── GridState.test.ts         [T-4]
│   ├── SnakeEngine.test.ts       [T-6]
│   ├── SnakeEngine.growth.test.ts [T-47]
│   ├── CollisionDetector.test.ts [T-8]
│   ├── FoodSpawner.test.ts       [T-10]
│   ├── GameState.test.ts         [T-12]
│   ├── GameState.speed.test.ts   [T-48]
│   └── GameState.lifecycle.test.ts [T-49]
├── input/
│   └── InputHandler.test.ts      [T-14]
├── replay/
│   ├── StateSerializer.test.ts   [T-16]
│   ├── ReplayRecorder.test.ts    [T-18]
│   ├── ReplayRecorder.quota.test.ts [T-54]
│   ├── ReplayEngine.test.ts      [T-20]
│   ├── ReplayEngine.pause.test.ts [T-55]
│   └── replay_accuracy.test.ts   [T-28]
├── render/
│   ├── CanvasRenderer.test.ts    [T-22]
│   ├── CanvasRenderer.ghost.test.ts [T-56]
│   ├── CanvasRenderer.snake_food.test.ts [T-58]
│   └── CanvasRenderer.ghost_render.test.ts [T-59]
├── ui/
│   ├── TickScheduler.test.ts     [T-24]
│   ├── UIController.pause.test.ts [T-50]
│   ├── UIController.stop.test.ts [T-51]
│   ├── ReplayListUI.list.test.ts [T-52]
│   └── ReplayListUI.delete.test.ts [T-53]
├── integration/
│   ├── live_ghost_coexist.test.ts [T-57]
│   └── (T-28 in replay/ folder)
└── e2e/
    ├── game_flow.test.ts         [T-29]
    ├── replay_playback.test.ts   [T-30]
    ├── ghost_snake.test.ts       [T-31]
    └── input_handling.test.ts    [T-32]
```

## Story Coverage Matrix

| Epic | Stories | Implementation Tasks | Test Tasks |
|------|---------|---------------------|-----------|
| E-1: Core Engine | S-1.1, S-1.2, S-1.3, S-1.4 | T-3, T-5, T-7, T-9 | T-4, T-6, T-8, T-10, T-47 |
| E-2: Game State | S-2.1, S-2.2, S-2.3 | T-11 | T-12, T-48, T-49 |
| E-3: UI Controls | S-3.1, S-3.2, S-3.3, S-3.4, S-3.5 | T-25, T-26 | T-29, T-50, T-51, T-52, T-53 |
| E-4: Recording | S-4.1, S-4.2, S-4.3 | T-15, T-17 | T-16, T-18, T-28, T-54 |
| E-5: Replay | S-5.1, S-5.2, S-5.3, S-5.4 | T-19, T-60, T-61 | T-20, T-30, T-55 |
| E-6: Ghost Snake | S-6.1, S-6.2, S-6.3 | T-21, T-27, T-41, T-46 | T-22, T-31, T-56, T-57, T-59 |
| E-7: Input | S-7.1, S-7.2 | T-13, T-43, T-44 | T-14, T-32 |
| E-8: Rendering | S-8.1, S-8.2, S-8.3 | T-21, T-45, T-46 | T-22, T-58, T-59 |

## Acceptance Checklist

- [ ] All 64 tasks completed
- [ ] Unit tests pass: `npm test`
- [ ] E2E tests pass: `npm run test:e2e`
- [ ] Build succeeds: `npm run build`
- [ ] No TypeScript errors
- [ ] Canvas renders 60 FPS
- [ ] Input buffering prevents reverse direction
- [ ] Replay is bit-exact (correctness bar)
- [ ] Live and ghost coexist without collision

## Next Steps

1. **Proceed to Stage 6: Implementation**
   - Execute tasks in order following execution_order phases
   - Implement all 12 core components
   - Create 3 entry points (HTML, CSS, main.ts)
   - Run builds and tests at each phase gate

2. **Verification**
   - After T-63 (build), verify `npm run build` produces `dist/`
   - After T-64 (tests), verify all tests pass and coverage is complete

3. **Deployment**
   - Stage 7: Deploy to GitHub Pages at `/snake-game-replay/` base path
   - Stage 8: Validate against Expected-Outcomes requirements

---

**Generated**: Stage 5 Planning Phase
**Total Tasks**: 64
**Estimated Sprint Time**: 3-5 days (1-2 weeks if including testing infrastructure)
**Status**: Ready for Stage 6 Implementation
