---
name: "UAT Test Execution Plan"
description: "Master test plan partitioning for parallel UAT sub-agents"
prompt_version: "2026-05-09"
---

# Stage 8: UAT Test Execution Strategy

## Overview

The Snake game project uses **4 parallel sub-agents** to execute independent test suites:

1. **Subagent 1 (Game Mechanics)** - Core engine functionality
2. **Subagent 2 (Replay System)** - Recording and playback accuracy
3. **Subagent 3 (UI & Input)** - User controls and buffering
4. **Subagent 4 (Edge Cases)** - Boundaries, limits, performance

Each sub-agent:
- Operates independently (no blocking dependencies)
- Executes assigned test suite (unit + E2E)
- Produces JSON results file
- Reports PASS/FAIL with evidence

## Subagent 1: Game Mechanics Tests

**Responsibility**: Core snake movement, collision, food, scoring

**Tests to Execute**:
```bash
npm test -- tests/engine/
npm run test:e2e -- tests/e2e/mechanics.e2e.ts
```

**Test Coverage**:
- ✅ Snake moves up, down, left, right
- ✅ Snake moves one cell per tick
- ✅ Food spawns in empty cells only
- ✅ Snake grows by 1 when eating food
- ✅ Score increments by 1 per food
- ✅ Wall collision ends game
- ✅ Self-collision ends game
- ✅ Speed increases after each food (up to 15 FPS cap)
- ✅ Multiple food doesn't cause multiple growth
- ✅ Grid wrapping does NOT occur (boundary walls)

**Acceptance Criteria**:
- [ ] All movement direction tests pass
- [ ] All collision tests pass
- [ ] All scoring tests pass
- [ ] All growth tests pass

**Output**: `.agents/artifacts/stage-8/uat_results_mechanics.json`

## Subagent 2: Replay System Tests

**Responsibility**: State serialization, recording, playback, bit-exact accuracy

**Tests to Execute**:
```bash
npm test -- tests/replay/
npm run test:e2e -- tests/e2e/replay.e2e.ts
```

**Test Coverage**:
- ✅ State serialization round-trip (serialize → deserialize matches original)
- ✅ Replay recording captures all ticks
- ✅ Replay playback at 0.5× speed
- ✅ Replay playback at 1× speed
- ✅ Replay playback at 2× speed
- ✅ Replay playback at 4× speed
- ✅ Bit-exact replay verification (recorded state == replayed state)
- ✅ Ghost snake renders during replay
- ✅ localStorage persistence (save/load replay)
- ✅ Multiple replays can coexist in localStorage

**Acceptance Criteria**:
- [ ] Serialization tests all pass
- [ ] Replay playback at all speeds works
- [ ] Bit-exact verification passes (recorded game == replayed game)
- [ ] Ghost snake visible during replay
- [ ] localStorage persistence works

**Output**: `.agents/artifacts/stage-8/uat_results_replay.json`

## Subagent 3: UI & Input Tests

**Responsibility**: Button controls, keyboard buffering, direction validation

**Tests to Execute**:
```bash
npm test -- tests/input/ tests/ui/
npm run test:e2e -- tests/e2e/ui.e2e.ts
```

**Test Coverage**:
- ✅ New Game button creates fresh game
- ✅ Pause button freezes state
- ✅ Resume button continues from pause
- ✅ Stop button returns to menu
- ✅ View Replays button displays list
- ✅ Arrow key input queues direction changes
- ✅ Rapid key presses don't lose input (buffering)
- ✅ Reverse direction prevention: UP + DOWN in rapid succession fails
- ✅ Reverse direction prevention: LEFT + RIGHT in rapid succession fails
- ✅ Score display updates in real-time
- ✅ Speed display updates when food eaten
- ✅ Button states transition correctly (disabled during gameplay, etc.)

**Acceptance Criteria**:
- [ ] All button events trigger correct actions
- [ ] Input buffering prevents key loss
- [ ] Reverse direction validation prevents self-collision
- [ ] Display updates are timely

**Output**: `.agents/artifacts/stage-8/uat_results_ui.json`

## Subagent 4: Edge Cases & Performance

**Responsibility**: Boundary conditions, limits, performance under stress

**Tests to Execute**:
```bash
npm test -- tests/edge-cases/
npm run test:e2e -- tests/e2e/edge-cases.e2e.ts
```

**Test Coverage**:
- ✅ Snake at grid boundaries (no wrapping)
- ✅ Snake fills entire grid (31×31 = 961 cells max length)
- ✅ Speed caps at 15 FPS (not infinite)
- ✅ Canvas renders at 60 FPS (baseline performance check)
- ✅ localStorage quota not exceeded (< 5MB assumed available)
- ✅ 100 ticks without food doesn't crash
- ✅ Direction changes at max speed don't cause desyncs
- ✅ Pause at any game state is recoverable
- ✅ Very rapid pause/resume doesn't cause glitches
- ✅ Replay playback handles 1000+ state ticks

**Acceptance Criteria**:
- [ ] No crashes at boundaries
- [ ] Speed capped correctly
- [ ] Performance acceptable (60 FPS maintains)
- [ ] Storage limits respected

**Output**: `.agents/artifacts/stage-8/uat_results_edge.json`

## Result Aggregation

After all 4 subagents complete:

**Master Results File**: `.agents/artifacts/stage-8/uat_results_master.json`
```json
{
  "timestamp": "2024-01-15T14:30:00Z",
  "total_tests": <sum of all 4 suites>,
  "passed": <count>,
  "failed": <count>,
  "skipped": <count>,
  "suites": {
    "mechanics": { "path": ".../uat_results_mechanics.json", "status": "PASS/FAIL" },
    "replay": { "path": ".../uat_results_replay.json", "status": "PASS/FAIL" },
    "ui": { "path": ".../uat_results_ui.json", "status": "PASS/FAIL" },
    "edge_cases": { "path": ".../uat_results_edge.json", "status": "PASS/FAIL" }
  },
  "verdict": "PASS" | "FAIL",
  "blocking_issues": [/* any failures */]
}
```

**Compiled Report**: `.agents/artifacts/stage-8/uat-results_final.md`
- Human-readable summary
- Test count table
- Per-test results grouped by suite
- Bugs and failures (if any)
- Recommendations

## Gate Logic

**Verification Script**: `python .agents/skills/stage-8-uat/verify/uat_gate.py .agents/artifacts/stage-8/`

Exit codes:
- `0` → ✅ All tests passed, project ready
- Non-zero → ❌ Test failures blocking gate, output specific issues

## Execution Order

1. **Parallel dispatch**: All 4 subagents launched simultaneously
2. **Independence**: Each runs own test commands, no inter-dependencies
3. **Collection**: Master coordinator waits for all 4 to complete
4. **Aggregation**: Results merged into master file
5. **Verification**: Gate script checks master file
6. **Report**: Final markdown compiled

## Test Infrastructure

**Unit Tests**: `npm test`
- Vitest 1.5.x with jsdom
- jsdom environment for DOM/canvas mocking

**E2E Tests**: `npm run test:e2e`
- Playwright 1.44.x
- Headless browser, actual canvas rendering

**Commands**:
```bash
# All tests
npm test && npm run test:e2e

# By suite
npm test -- tests/engine/           # Mechanics unit tests
npm run test:e2e -- tests/e2e/mechanics.e2e.ts

npm test -- tests/replay/           # Replay unit tests
npm run test:e2e -- tests/e2e/replay.e2e.ts

# etc.
```

## Continuation

Once UAT passes:
- ✅ Project is **COMPLETE**
- ✅ All acceptance criteria met
- ✅ Ready for local play
- No deployment needed (removed from SDLC pipeline)
