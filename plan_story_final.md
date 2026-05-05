# Implementation Plan: Tic-Tac-Toe with Unbeatable AI — Full Application

**Status:** Draft
**Author:** [TBD]
**Date:** May 5, 2026
**Story:** Deliver a complete, playable Tic-Tac-Toe application with PvP, Easy AI, and Impossible AI modes, minimax score overlay, win/draw detection, and a new-game flow — all running client-side in a single HTML page.
**Related Epics:** Epic 1 (Core Board & Rules), Epic 2 (AI Opponents), Epic 3 (Score Overlay), Epic 4 (Game Flow & Mode Selection)
**Estimate:** M

---

## Acceptance Criteria

Consolidated from all stories in `epics_stories_final.md`:

**Board & Rules (Epic 1)**
- [ ] A 3×3 grid of nine cells is visible on page load; all cells start empty.
- [ ] Grid is responsive and usable at 375 px width.
- [ ] Clicking an empty cell places X (first) then O alternately; turn indicator updates.
- [ ] Clicking a filled cell has no effect.
- [ ] Cells are reachable by Tab (reading order); Enter/Space activates a focused cell.
- [ ] All 8 win lines (3 rows, 3 columns, 2 diagonals) detected correctly and immediately.
- [ ] On win: "[X/O] wins!" banner shown, winning line highlighted (not colour-only), all cells inert.
- [ ] On draw: "It's a draw!" banner shown, all cells inert.

**Easy AI (Epic 2 — Story 2.1)**
- [ ] Easy AI selects a random legal (empty) move on its turn.
- [ ] Board is non-interactive during AI turn.
- [ ] Win/draw detection works in Easy AI mode.

**Impossible AI (Epic 2 — Story 2.2)**
- [ ] Impossible AI uses minimax with alpha-beta pruning.
- [ ] AI never loses; worst case for the human is a draw.
- [ ] AI computation completes in < 50 ms on a mid-range device.
- [ ] Unit tests cover all terminal state evaluations (win = +1/−1, draw = 0).

**Score Overlay (Epic 3 — Story 3.1)**
- [ ] During Impossible AI's turn, minimax score (−1, 0, or +1) appears on every empty cell.
- [ ] Scores computed with plain minimax (no alpha-beta) for display accuracy.
- [ ] Overlay visible for ≥ 150 ms before AI commits move.
- [ ] Overlay clears after AI places its move.
- [ ] Filled cells show no overlay.
- [ ] Each score cell has `aria-label="Minimax score: [value]"`.
- [ ] Overlay shown only in Impossible AI mode.

**Mode Selection & New Game (Epic 4)**
- [ ] Mode selection screen shown on page load with three labelled buttons.
- [ ] Mode buttons are keyboard focusable and activatable.
- [ ] Selecting a mode starts a new game and shows the board.
- [ ] "New Game" button appears only after terminal state; clicking it resets board and returns to mode selection with last-used mode pre-selected.

---

## Implementation Tasks

### Frontend

| ID | Task | Definition of Done | Depends On |
|----|------|--------------------|------------|
| FE-01 | Create `index.html` with semantic structure: mode-selection screen, game board (9 cells), turn indicator, score overlay container, result banner, New Game button | HTML renders correctly in browser; all elements present in DOM | — |
| FE-02 | Style the 3×3 grid: responsive CSS Grid layout, 44×44 px minimum cell size, visible cell borders, pointer/default cursor states | Grid usable at 375 px and 1280 px; cells visually distinct | FE-01 |
| FE-03 | Style mode selection screen: three buttons, focus ring, hover state | Buttons accessible and visually clear | FE-01 |
| FE-04 | Style score overlay: small muted numeric text centred in cell, does not obscure symbol, meets 4.5:1 contrast | Overlay legible; does not shift layout | FE-02 |
| FE-05 | Style winning-line highlight: visual treatment on three winning cells that is not colour-only (e.g., bold border or underline) | Winning cells visually distinct without relying on colour alone | FE-02 |
| FE-06 | Implement `BoardRenderer`: `render(state)` writes X/O symbols as `textContent` into cells; updates turn indicator; shows/hides result banner; shows/hides New Game button | All board states (ongoing, win, draw) render correctly; no `innerHTML` with variable content | FE-01 |
| FE-07 | Implement `BoardRenderer.renderScoreOverlay(scores)` and `clearScoreOverlay()`: writes minimax scores to open cells with `aria-label`; clears on call | Scores appear on correct cells; aria-label set; clears cleanly | FE-06 |
| FE-08 | Implement `UIController`: wire cell click/keyboard events → `GameState.applyMove`; wire mode buttons → game start; wire New Game button → mode selection reset; orchestrate AI turns and score overlay timing | All user interactions produce correct state transitions; board non-interactive during AI turn | FE-06, Logic layer |

### Logic

| ID | Task | Definition of Done | Depends On |
|----|------|--------------------|------------|
| L-01 | Implement `GameState` module: `cells[9]`, `currentPlayer`, `mode`, `status`; pure functions `applyMove(cellIndex)`, `checkWinner()`, `isDraw()`, `getLegalMoves()` | All functions return correct results for all board states; immutable — each call returns a new state object | — |
| L-02 | Implement `EasyAI.bestMove(state)`: returns a random index from `getLegalMoves()` | Always returns a legal move; never returns an occupied index | L-01 |
| L-03 | Implement `MinimaxEngine.minimax(state, isMaximising)`: recursive minimax returning score; base cases: win (+1/−1), draw (0) | Correct scores for all terminal and near-terminal states; confirmed by unit tests | L-01 |
| L-04 | Add alpha-beta pruning to `minimax` as `minimaxAB(state, depth, alpha, beta, isMaximising)` | Same scores as plain minimax; executes in < 50 ms from empty board | L-03 |
| L-05 | Implement `MinimaxEngine.bestMove(state)`: calls `minimaxAB` for each legal move, returns index with highest score | Always returns a legal move that matches known optimal play | L-04 |
| L-06 | Implement `MinimaxEngine.scoreAllMoves(state)`: calls plain `minimax` (no alpha-beta) for each legal move; returns `{ cellIndex: score }` map | Scores match true minimax values; plain minimax used (not alpha-beta) | L-03 |

### Testing

| ID | Task | Type | Definition of Done |
|----|------|------|--------------------|
| TEST-01 | Unit test `GameState.checkWinner`: all 8 win lines for X and O, draw (full board no winner), ongoing (partial board) | Unit | All cases pass; zero false positives/negatives |
| TEST-02 | Unit test `GameState.applyMove`: valid move, occupied cell (should throw/no-op), out-of-range index, move after terminal state | Unit | Edge cases handled; state is immutable |
| TEST-03 | Unit test `GameState.getLegalMoves`: empty board (9 moves), full board (0 moves), mid-game board | Unit | Correct indices returned |
| TEST-04 | Unit test `MinimaxEngine.minimax` terminal states: board with X winning = −1 (from O's perspective), board with O winning = +1, draw = 0 | Unit | Base cases return correct scores |
| TEST-05 | Unit test `MinimaxEngine.bestMove` from empty board: verify score is 0 (optimal play always draws) | Unit | Returns 0-score move; any centre/corner is valid |
| TEST-06 | Unit test `MinimaxEngine.scoreAllMoves`: compare scores on a known mid-game position against a reference lookup | Unit | All cell scores match expected values |
| TEST-07 | Unit test `EasyAI.bestMove`: called 100 times on a mid-game board; all returned indices are legal | Unit | No illegal moves returned in 100 trials |
| TEST-08 | Manual / E2E test: play full games in all three modes; verify win, draw, and new-game flows | E2E | All acceptance criteria pass manually in Chrome, Firefox, Safari |
| TEST-09 | Keyboard accessibility test: complete a full game using only keyboard | E2E | All cells reachable and activatable; focus indicators visible throughout |

---

## Task Dependency Order

1. **L-01** — `GameState` (foundation for everything)
2. **L-02** — `EasyAI` (depends only on `GameState`)
3. **L-03** — `minimax` plain (foundation for AI and overlay)
4. **L-04** — `minimaxAB` with alpha-beta (depends on L-03)
5. **L-05** — `MinimaxEngine.bestMove` (depends on L-04)
6. **L-06** — `MinimaxEngine.scoreAllMoves` (depends on L-03)
7. **TEST-01 → TEST-07** — all logic unit tests (run in parallel after logic layer complete)
8. **FE-01** — HTML structure
9. **FE-02, FE-03** — CSS (can run in parallel with logic layer)
10. **FE-06** — `BoardRenderer` (depends on FE-01)
11. **FE-07** — Score overlay rendering (depends on FE-06, L-06)
12. **FE-04, FE-05** — Overlay and win-line styles (can run in parallel with FE-06)
13. **FE-08** — `UIController` wiring (depends on all FE and logic tasks)
14. **TEST-08, TEST-09** — E2E / accessibility tests (after FE-08)

---

## Risks & Unknowns

| Item | Type | Impact | Mitigation / Next Step |
|------|------|--------|------------------------|
| Alpha-beta pruning altering displayed scores | Risk | High — overlay shows wrong scores, undermining the educational value | `scoreAllMoves` must use plain minimax; `bestMove` uses alpha-beta separately. Covered by TEST-06. |
| Score overlay 150 ms pause UX | Unknown | Low — pause may feel slow or too fast depending on device | Implement as a named constant (`OVERLAY_DISPLAY_MS = 150`); easy to tune |
| Player-side selection (human = X or O) | Unknown | Medium — PRD marks this TBD | Implement human = X, AI = O for now; expose a variable in `UIController` for easy swap later |
| Mobile tap target size | Risk | Medium — cells may be too small on small phones | Enforce `min-width: 44px; min-height: 44px` in CSS; verify at 375 px viewport |

---

## Out of Scope / Follow-up Items

- Ultimate Tic-Tac-Toe variant
- 4×4 / 5×5 grid variants
- Teaching mode with post-move explanations
- Adjustable difficulty
- Transposition table / memoization (performance optimization — not needed given tree size)
- Player-side selection (human as X or O) — deferred pending PRD clarification
- Artificial move delay for Easy AI — not currently specified

---

## Open Questions

- Should the mode selection screen persist the last-used mode across page reloads (localStorage), or only within the session? Plan assumes session-only.
- Should the score overlay remain visible after the AI moves (for reflection) or clear immediately? Plan assumes clear immediately after AI move, per UX guidance.
