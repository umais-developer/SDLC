# Epics & Stories: Tic-Tac-Toe with Unbeatable AI

**Status:** Draft
**Author:** [TBD]
**Date:** May 5, 2026
**Version:** 1.0
**Related PRD:** `prd_final.md`

---

## Summary

The feature breaks into four epics: the core game board and rules engine, the AI implementations (Easy and Impossible), the minimax score overlay, and the game-over and new-game flow. Each epic can be delivered and tested independently. The architecture separates `GameState`, `MinimaxEngine`, `EasyAI`, `UIController`, and `BoardRenderer`, so stories align to those boundaries.

---

## Epic 1: Core Game Board & Rules Engine

**Goal:** Deliver a playable 3×3 Tic-Tac-Toe board for two human players with correct win/draw detection and turn management.
**Priority:** P0
**Estimated Size:** M

### Stories

#### Story 1.1 — Render the 3×3 Game Board
**As a** player, **I want** to see a 3×3 Tic-Tac-Toe grid when I open the page **so that** I can begin placing moves.

**Acceptance Criteria:**
- [ ] A 3×3 grid of nine equal cells is visible on page load.
- [ ] Each cell is empty (no X or O) at the start of the game.
- [ ] The grid is responsive and usable on viewports as narrow as 375 px.
- [ ] All nine cells are reachable by keyboard Tab navigation in reading order (left-to-right, top-to-bottom).
- [ ] Each cell has a visible focus indicator when focused by keyboard.

**Size:** S
**Notes:** The game mode selection (Epic 4) is a separate story. This story delivers the board in a default single-player-can-click state; mode wiring is added in later stories.

---

#### Story 1.2 — Place X and O Alternately (Player vs Player)
**As a** player, **I want** to click an empty cell to place my symbol (X or O) and have the turn automatically switch to the other player **so that** two people can play a complete game of Tic-Tac-Toe.

**Acceptance Criteria:**
- [ ] Clicking an empty cell places X on the first turn, O on the second, and continues alternating.
- [ ] A turn indicator above or below the board shows "X's turn" or "O's turn" and updates after each move.
- [ ] Clicking an already-filled cell has no effect (symbol does not change, turn does not advance).
- [ ] The cell cursor is `pointer` on hover for empty cells and `default` for filled cells.
- [ ] Move can also be placed by pressing Enter or Space when a cell is focused.

**Size:** S
**Notes:** Assumes the board from Story 1.1 is rendered. Win/draw detection is delivered in Story 1.3.

---

#### Story 1.3 — Detect Win, Draw, and Ongoing Game State
**As a** player, **I want** the game to detect when someone has won or the board is full **so that** the game ends correctly and no further moves are accepted.

**Acceptance Criteria:**
- [ ] The game correctly detects all 8 win lines (3 rows, 3 columns, 2 diagonals).
- [ ] When a win is detected, a banner displays "[X/O] wins!" and all cells become inert (no further moves accepted).
- [ ] The three winning cells are visually distinguished from the other cells (e.g., highlighted).
- [ ] When all 9 cells are filled with no winner, a banner displays "It's a draw!" and all cells become inert.
- [ ] Win/draw detection fires immediately after the move that causes it — no extra click required.
- [ ] The turn indicator is replaced by or updated to the result text on game over.
- [ ] The winning highlight does not rely solely on colour (WCAG requirement — e.g., includes a border or underline).

**Size:** M
**Notes:** Terminal state halting input is a P0 requirement from the PRD.

---

## Epic 2: AI Opponents

**Goal:** Deliver two AI play modes — Easy (random) and Impossible (minimax + alpha-beta) — that plug into the existing board.
**Priority:** P0
**Estimated Size:** M

### Stories

#### Story 2.1 — Easy AI: Random Legal Move
**As a** player, **I want** to play against an Easy AI that selects a random legal move each turn **so that** I have a beatable computer opponent to practice against.

**Acceptance Criteria:**
- [ ] When "Easy AI" mode is selected, the player places X and the AI places O.
- [ ] The AI always plays into an empty cell; it never places on an occupied cell.
- [ ] The AI's move appears immediately after the human's move (no artificial delay required).
- [ ] Win/draw detection works identically to PvP — the game ends correctly regardless of who causes the terminal state.
- [ ] The board is non-interactive during the AI's turn (prevents double moves).

**Size:** S
**Notes:** Mode selection UI is delivered in Story 4.1. This story can be tested by hard-coding "Easy AI" mode temporarily.

---

#### Story 2.2 — Impossible AI: Minimax with Alpha-Beta Pruning
**As a** player, **I want** to play against an Impossible AI that uses minimax with alpha-beta pruning **so that** I cannot beat it — the best I can do is draw.

**Acceptance Criteria:**
- [ ] The AI uses the minimax algorithm with alpha-beta pruning for move selection.
- [ ] The AI never loses: across all reachable game states, the result is always a win for O or a draw.
- [ ] The AI always plays into an empty cell.
- [ ] Win/draw detection works identically to other modes.
- [ ] The board is non-interactive while the AI computes its move.
- [ ] AI move computation completes in under 50 ms on a mid-range device.
- [ ] Unit tests cover all terminal state evaluations: win returns +1 (or −1 for opponent), draw returns 0.

**Size:** M
**Notes:** Alpha-beta pruning is required for correctness of the score overlay (see Story 3.1) — the engine must support a "no pruning" mode for `scoreAllMoves`. Score overlay is a separate story.

---

## Epic 3: Minimax Score Overlay

**Goal:** Show the minimax evaluation score for each open cell during the Impossible AI's turn so the player can understand the AI's decision.
**Priority:** P0
**Estimated Size:** S

### Stories

#### Story 3.1 — Display Minimax Scores on Open Cells Before AI Moves
**As a** learner, **I want** to see the minimax score for each open cell while the Impossible AI is deciding **so that** I can understand why it chose the move it did.

**Acceptance Criteria:**
- [ ] When it is the Impossible AI's turn, the minimax score (−1, 0, or +1) is displayed on every empty cell before the AI commits its move.
- [ ] Scores are computed using plain minimax (no alpha-beta) to guarantee each cell's displayed score is the true minimax value.
- [ ] Cells already containing X or O show no score overlay.
- [ ] The score overlay is visually distinct but does not obscure the X/O symbols or grid lines.
- [ ] The overlay is visible for at least 150 ms before the AI places its move (gives the user time to read it).
- [ ] The overlay clears immediately after the AI places its move.
- [ ] Each score cell has `aria-label="Minimax score: [value]"` for screen reader accessibility.
- [ ] The overlay is only shown in Impossible AI mode — PvP and Easy AI modes show no overlay.

**Size:** S
**Notes:** Depends on the Impossible AI engine from Story 2.2. The `scoreAllMoves` function is separate from `bestMove` to avoid alpha-beta interference with score accuracy.

---

## Epic 4: Game Flow & Mode Selection

**Goal:** Let the player choose a game mode before starting, and restart without a page refresh.
**Priority:** P1
**Estimated Size:** S

### Stories

#### Story 4.1 — Mode Selection Screen
**As a** player, **I want** to choose between Player vs Player, Easy AI, and Impossible AI before the game starts **so that** I can play the experience I want.

**Acceptance Criteria:**
- [ ] On page load, a mode selection screen is shown with three clearly labelled options: "Player vs Player", "Easy AI", "Impossible AI".
- [ ] Clicking a mode button starts a new game in that mode and shows the game board.
- [ ] The mode selection screen is not shown during an active game.
- [ ] All three buttons are keyboard focusable and activatable with Enter or Space.
- [ ] Each button has a visible focus indicator.

**Size:** S
**Notes:** Mode selection precedes board render. The board stories (Epic 1, 2, 3) can be developed against a hard-coded mode and wired to this story when available.

---

#### Story 4.2 — New Game Button and Mode Reset
**As a** player, **I want** to click a "New Game" button after a game ends and return to the mode selection screen **so that** I can start fresh without refreshing the page.

**Acceptance Criteria:**
- [ ] A "New Game" button is displayed after a win or draw is detected.
- [ ] "New Game" button is not visible during an active game.
- [ ] Clicking "New Game" clears the board, resets all game state, and shows the mode selection screen.
- [ ] The previously used mode is shown as the default selected option on the mode selection screen after clicking "New Game".
- [ ] The "New Game" button is keyboard focusable and activatable with Enter or Space.

**Size:** XS
**Notes:** Connects to terminal state from Story 1.3 and mode selection from Story 4.1.

---

## Technical Tasks

| ID | Task | Related Story | Notes |
|----|------|---------------|-------|
| T-01 | Set up project file structure: `index.html`, `game.js`, `minimax.js`, `ui.js` | All | No build toolchain required; vanilla JS |
| T-02 | Write unit tests for `GameState`: `applyMove`, `checkWinner`, `isDraw`, `getLegalMoves` | Story 1.3 | Test all 8 win lines, draw, and ongoing states |
| T-03 | Write unit tests for `MinimaxEngine`: validate AI never loses across sampled game trees | Story 2.2 | At minimum, test first-move scores and all depth-1 terminal states |
| T-04 | Write unit tests for `scoreAllMoves`: confirm scores match known minimax values | Story 3.1 | Compare against a reference lookup table for common positions |

---

## Open Questions & Assumptions

- **Assumption:** Human always plays X; AI always plays O. PRD marks player side selection as TBD.
- **Assumption:** No persistent score tracking between sessions is required (PRD: out of scope).
- **Open question:** Should the mode selection persist the last-used mode as default on "New Game"? Story 4.2 assumes yes — update if the product decision changes.
- **Open question:** Should a visual or audio cue accompany the AI's move placement? Not currently specified.

---

## Out of Scope

- Ultimate Tic-Tac-Toe (9-board meta-game)
- 4×4 / 5×5 grid variants
- Teaching mode with post-move explanations
- Adjustable difficulty sub-levels
- Multiplayer over a network
- Persistent score tracking
