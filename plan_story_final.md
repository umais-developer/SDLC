# Implementation Plan: Initialize Game Grid & Spawn Snake

**Status:** Draft  
**Author:** SDLC Pipeline  
**Date:** May 6, 2026  
**Story:** Story 1.1  
**Related Epic:** Epic 1 — Core Snake Gameplay  
**Estimate:** M (Medium)

---

## Acceptance Criteria
- [ ] Game grid displays as a 20×20 cell grid on page load
- [ ] Snake appears at center position (approximately 10, 10)
- [ ] Snake initial length is 3 segments (head + 2 body segments)
- [ ] First food item is randomly placed on an empty cell (not on snake body)
- [ ] Game loop begins automatically; no user action required to start
- [ ] Grid background is clearly visible; snake and food are visually distinct

---

## Implementation Tasks

### Frontend

| ID | Task | Definition of Done | Depends On |
|----|------|--------------------|------------|
| FE-01 | Create HTML scaffold with Canvas element | `<canvas id="gameCanvas" width="400" height="400"></canvas>` in index.html; canvas element is accessible to JS | None |
| FE-02 | Initialize Canvas 2D context and set rendering mode | `gameCanvas = document.getElementById('gameCanvas')`, `ctx = gameCanvas.getContext('2d')` in main.js; verify ctx is not null | FE-01 |
| FE-03 | Create Renderer class with grid drawing method | `Renderer` class has `drawGrid(ctx, width, height)` method that draws 20×20 grid lines; grid lines are visible and evenly spaced | None |
| FE-04 | Create Renderer method to draw snake | `Renderer.drawSnake(ctx, snakeBody)` method; draws head and body segments with distinct colors; head is opaque, body is slightly different shade; all segments visible and distinct | FE-03 |
| FE-05 | Create Renderer method to draw food | `Renderer.drawFood(ctx, foodPos)` method; draws food as a colored square at given x,y cell position; color contrasts with grid and snake | FE-03 |
| FE-06 | Create GameController initialization | `GameController` class instantiates on page load; sets up canvas, renderer, and game state; no render yet (see FE-10) | FE-02, FE-03 |
| FE-07 | Create initial app render frame | `Renderer.drawFrame(ctx, gameState)` method; renders grid, snake, and food in one call; frame is clean and readable on canvas | FE-04, FE-05 |

### Backend / Game Logic

| ID | Task | Definition of Done | Depends On |
|----|------|--------------------|------------|
| GL-01 | Create GameEngine class | `GameEngine` class with `initialize(gridWidth, gridHeight)` method; sets initial grid size to 20×20 | None |
| GL-02 | Initialize snake at center position | `GameEngine.initialize()` creates snake with 3 segments at center: head=(10,10), body=(9,10), tail=(8,10) (or similar center position); all segments stored as array of `{x, y}` objects | GL-01 |
| GL-03 | Implement random food spawn | `GameEngine.spawnFood()` method; selects random empty cell (not occupied by snake); places food at that cell; returns `{x, y}` position | GL-02 |
| GL-04 | Create StateManager class | `StateManager` class stores current `gameState` object: `{snakeBody, foodPos, score, speed, direction, gameOver, frameCount, gridWidth, gridHeight}` | None |
| GL-05 | Populate initial game state | `StateManager.getState()` returns initial state after `GameEngine.initialize()` and `spawnFood()` are called; state includes 3-segment snake at center and food at valid position | GL-02, GL-03, GL-04 |

### Testing

| ID | Task | Type | Definition of Done |
|----|------|------|-------------------|
| TEST-01 | Unit test: GameEngine initialization | Unit | Test: `GameEngine.initialize(20, 20)` creates snake with 3 segments at center; verify snake array length is 3; verify head position is approximately (10,10); verify no segments overlap |
| TEST-02 | Unit test: Food spawn uniqueness | Unit | Test: `GameEngine.spawnFood()` is called 100 times; verify food never spawns on snake body in any call; verify food position is within grid bounds (0–19, 0–19) |
| TEST-03 | Unit test: StateManager state structure | Unit | Test: `StateManager.getState()` returns object with all required keys: snakeBody, foodPos, score, speed, direction, gameOver, frameCount, gridWidth, gridHeight; verify types (array, object, number, boolean) |
| TEST-04 | Integration test: Renderer grid drawing | Integration | Test: `Renderer.drawGrid()` on canvas context; verify grid lines are drawn on canvas; measure line count (should be 21 horizontal + 21 vertical for 20×20 grid); verify no exceptions thrown |
| TEST-05 | Integration test: Full frame render | Integration | Test: `Renderer.drawFrame(ctx, initialGameState)` renders grid, snake, and food without exceptions; verify canvas has pixel data (non-blank); verify visual elements are distinguishable (different colors or patterns) |
| TEST-06 | Integration test: Page load initialization | Integration | Test: Load index.html in browser; verify canvas is visible; verify grid, snake, and food are drawn on initial page load; verify no console errors |
| TEST-07 | Manual test: Visual inspection | Manual | Load app in browser (Chrome, Firefox, Safari); verify 20×20 grid is visible; snake is 3 segments at approximate center; food is visible and distinct from snake; grid background is clear |

---

## Task Dependency Order

### Phase 1: Setup & Structure (Day 1)
1. **FE-01:** Create HTML scaffold with Canvas element
2. **GL-01:** Create GameEngine class
3. **GL-04:** Create StateManager class

### Phase 2: Initialization Logic (Day 2)
4. **GL-02:** Initialize snake at center position
5. **GL-03:** Implement random food spawn
6. **FE-02:** Initialize Canvas 2D context
7. **GL-05:** Populate initial game state

### Phase 3: Rendering Infrastructure (Day 2–3)
8. **FE-03:** Create Renderer class with grid drawing method
9. **FE-04:** Create Renderer method to draw snake
10. **FE-05:** Create Renderer method to draw food
11. **FE-06:** Create GameController initialization
12. **FE-07:** Create initial app render frame

### Phase 4: Testing & Verification (Day 3–4)
13. **TEST-01:** Unit test GameEngine initialization
14. **TEST-02:** Unit test food spawn uniqueness
15. **TEST-03:** Unit test StateManager state structure
16. **TEST-04:** Integration test Renderer grid drawing
17. **TEST-05:** Integration test full frame render
18. **TEST-06:** Integration test page load initialization
19. **TEST-07:** Manual test visual inspection

---

## Risks & Unknowns

| Item | Type | Impact | Mitigation / Next Step |
|------|------|--------|------------------------|
| **Canvas rendering performance** | Unknown | If rendering is slow on initial frame, may indicate future performance issues | Profile with DevTools; benchmark canvas draw time; target < 5ms per frame |
| **Random food spawn collisions** | Risk | If food spawn algorithm is inefficient, could have edge cases on very full grids | Implement retry limit (e.g., 10 retries) before failing; document assumption that grid is never fully packed in MVP |
| **Cross-browser Canvas API compatibility** | Risk | Canvas 2D API may have minor differences across browsers (Chrome, Firefox, Safari, Edge) | Test on all four target browsers during TEST-06 and TEST-07; document any workarounds |
| **Floating-point vs. integer grid positioning** | Risk | If grid coordinates use floats, visual alignment may be inconsistent (cells misaligned) | Use integers for grid positions; ensure canvas cell dimensions are calculated as integers (e.g., cellWidth = canvasWidth / gridWidth, rounded) |
| **Screen reader accessibility of canvas** | Risk | Canvas is not inherently accessible to screen readers; need ARIA labels | Out of scope for this story; defer to accessible rendering story. Document that canvas needs role="img" and aria-label |

---

## Out of Scope / Follow-up Items

- **Game loop tick timing:** This story does not include the game loop execution. Story 1.2 (Move Snake) will add the game loop.
- **Input handling:** This story does not capture keyboard input. Story 2.1–2.3 will add input handling.
- **Score display:** This story initializes score = 0 but does not render it on canvas. Story 1.7 will add score rendering.
- **Animation / smooth rendering:** Initial frame is static (no animation). Future stories will add game loop and animation.
- **Pause / resume state:** This story does not handle pause. Later stories will add pause logic.
- **Mobile responsiveness:** This story uses fixed canvas dimensions (400×400). Responsive scaling is a follow-up item.
- **Accessibility beyond canvas label:** Screen reader testing, keyboard-only navigation, and color contrast are follow-up accessibility items.

---

## Open Questions

- **Canvas size:** Should canvas be a fixed 400×400px, or should it scale to viewport? (Answer for MVP: Fixed 400×400px; responsive scaling is a follow-up)
- **Grid cell size:** Should each grid cell be 20×20 pixels (resulting in 400×400 total for 20×20 grid), or variable? (Answer: Fixed 20px per cell; document in code)
- **Snake initial direction:** What direction is the snake "facing" at start? (Answer: No direction initially; direction is set on first key press. See Story 1.2)
- **Food position randomness:** Should food spawn use `Math.random()` directly, or a seeded random for replay determinism? (Answer for MVP: Direct `Math.random()` for live games. Seeded random is applied during replay playback. See Epic 3 & 4)
- **Color scheme:** What colors for grid, snake, food? (Answer: To be determined during implementation; recommend: grid=light gray, snake=green, food=red)

---

## Implementation Notes

### File Structure
```
/
  index.html
  styles.css
  js/
    main.js              (app entry point, initialization)
    game-engine.js       (GameEngine class)
    state-manager.js     (StateManager class)
    renderer.js          (Renderer class)
    game-controller.js   (GameController class)
  tests/
    game-engine.test.js
    renderer.test.js
    state-manager.test.js
```

### Key Implementation Details

1. **Canvas Initialization (FE-02):**
   ```javascript
   const canvas = document.getElementById('gameCanvas');
   const ctx = canvas.getContext('2d');
   const cellWidth = canvas.width / 20;  // 400 / 20 = 20px per cell
   const cellHeight = canvas.height / 20;
   ```

2. **Snake Data Structure (GL-02):**
   ```javascript
   const snakeBody = [
     {x: 10, y: 10},  // head
     {x: 9, y: 10},   // body segment 1
     {x: 8, y: 10}    // tail
   ];
   ```

3. **Food Spawn Algorithm (GL-03):**
   ```javascript
   spawnFood() {
     let foodPos;
     let retries = 0;
     do {
       foodPos = {
         x: Math.floor(Math.random() * 20),
         y: Math.floor(Math.random() * 20)
       };
       retries++;
     } while (this.isOccupiedBySnake(foodPos) && retries < 10);
     return foodPos;
   }
   ```

4. **Grid Rendering (FE-03):**
   ```javascript
   drawGrid(ctx, gridWidth, gridHeight) {
     const cellWidth = ctx.canvas.width / gridWidth;
     const cellHeight = ctx.canvas.height / gridHeight;
     ctx.strokeStyle = '#ccc';
     for (let i = 0; i <= gridWidth; i++) {
       ctx.beginPath();
       ctx.moveTo(i * cellWidth, 0);
       ctx.lineTo(i * cellWidth, ctx.canvas.height);
       ctx.stroke();
     }
     for (let j = 0; j <= gridHeight; j++) {
       ctx.beginPath();
       ctx.moveTo(0, j * cellHeight);
       ctx.lineTo(ctx.canvas.width, j * cellHeight);
       ctx.stroke();
     }
   }
   ```

---

## Definition of Done for Story 1.1

**All of the following must be true before this story is considered complete:**

1. ✅ All 7 frontend tasks complete and tested
2. ✅ All 5 game logic tasks complete and tested
3. ✅ All 7 tests pass (TEST-01 through TEST-07)
4. ✅ Manual visual inspection confirms all 6 acceptance criteria are met
5. ✅ Code is committed to a feature branch with clear commit message
6. ✅ Code review is complete with no blocker comments
7. ✅ No console errors in browser DevTools when loading index.html
8. ✅ Grid, snake, and food are visible on page load (no user action required)

---

## Success Metrics for Story 1.1

- Game initializes in < 100ms on modern hardware
- Canvas renders without flicker or visual artifacts
- No memory leaks on repeated page reloads (check DevTools Memory tab)
- All browsers (Chrome, Firefox, Safari, Edge) render identically (pixel-perfect grid alignment not required, but visual harmony required)
