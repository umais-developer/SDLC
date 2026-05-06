# Epics & Stories: B3 Tic-Tac-Toe with Unbeatable AI

**Status:** Final  
**Author:** Product & Engineering Team  
**Date:** 2026-05-06  
**Version:** 1.0  
**Related PRD:** [prd_final.md](prd_final.md)  
**Related Architecture:** [architecture_final.md](architecture_final.md)  
**Related UX:** [ux_final.md](ux_final.md)

---

## Summary

The Tic-Tac-Toe application is organized into seven epics covering core game mechanics, AI implementations, and UI/UX. Each epic maps to a functional area (mode selection, game rules, AI logic, visualization, state management, and responsive design). Stories are organized from foundation (mode selection, basic UI) through core gameplay (PvP, AI modes) to advanced features (minimax visualization). All stories are independently deliverable and testable against acceptance criteria traceable to PRD functional requirements, architecture constraints, and UX flows.

---

## Epic 1: Mode Selection & Game Initialization

**Goal:** Players can select one of three game modes and begin a fresh game with an empty board and clear game state.  
**Priority:** P0  
**Estimated Size:** M

### Stories

#### Story 1.1 — Display Mode Selection Screen
**As a** casual player, **I want** to see three clearly labeled mode options when the app loads **so that** I can choose how to play.

**Acceptance Criteria:**
- [ ] Application displays a main screen on load with no game board initially visible.
- [ ] Three mode buttons are displayed: "Player vs. Player", "Play Easy AI", "Play Impossible AI".
- [ ] Buttons are equally prominent, centered, and clearly labeled with text (no icons alone).
- [ ] Each button is at least 44×44 px and has high contrast (4.5:1 minimum) for accessibility.
- [ ] Keyboard navigation works: Tab key cycles through buttons; Enter key selects the focused button.
- [ ] Focus indicator is visible (at least 2px border/outline) on all buttons.
- [ ] Page title reads "Tic-Tac-Toe with AI" or similar in browser tab.

**Size:** S  
**Notes:** No styling complexity; buttons are functional and accessible. This story establishes the UI entry point.

---

#### Story 1.2 — Initialize Game Board and Game State
**As a** player, **I want** the board to initialize to an empty state after I select a mode **so that** I can start playing immediately.

**Acceptance Criteria:**
- [ ] After clicking a mode button, the mode selector screen disappears.
- [ ] A 3×3 empty game board is displayed (9 cells arranged in 3 rows × 3 columns).
- [ ] Each cell is labeled or indexed (e.g., positions 0–8 or row/column labels) for reference.
- [ ] Game state is initialized: board is empty, current player is set (human for AI modes; Player 1 for PvP).
- [ ] No mode button is clickable while a game is active (mode selector is hidden).
- [ ] A turn indicator displays whose turn it is (e.g., "Your turn", "Player 1's turn").
- [ ] Rematch button is hidden initially (only shown after game ends).

**Size:** S  
**Notes:** Covers state initialization for all three modes; mode-specific logic (PvP vs. AI) is deferred to later stories.

---

## Epic 2: Player vs. Player Mode

**Goal:** Two human players can alternate turns on a shared device and play a complete game of Tic-Tac-Toe.  
**Priority:** P0  
**Estimated Size:** M

### Stories

#### Story 2.1 — Enable Cell Clicks and Mark Placement (Human Move)
**As a** player, **I want** to click an empty cell to place my mark **so that** I can make a move.

**Acceptance Criteria:**
- [ ] Each empty cell is clickable (hover state shows affordance, e.g., cursor: pointer).
- [ ] Clicking an empty cell places the current player's mark (X for Player 1, O for Player 2 in PvP).
- [ ] Visual feedback is provided on click (cell highlights or briefly inverts color).
- [ ] Clicking an already-filled cell has no effect (click is ignored).
- [ ] After a valid move, the turn indicator updates to the other player's name (e.g., "Player 1's turn" → "Player 2's turn").
- [ ] Board state in memory is updated correctly to reflect the move.
- [ ] Keyboard accessibility: All cells are reachable via Tab key; Enter or Space key places the mark on a focused cell.

**Size:** M  
**Notes:** Foundation for all gameplay modes. Handles mark placement logic independent of mode-specific AI logic.

---

#### Story 2.2 — Track Turn Alternation in PvP Mode
**As a** player in a Player vs. Player game, **I want** the game to alternate turns correctly between players **so that** each player takes exactly one turn per cycle.

**Acceptance Criteria:**
- [ ] After Player 1 makes a move, Player 2 is the current player (turn indicator updates).
- [ ] After Player 2 makes a move, Player 1 becomes the current player.
- [ ] Turn indicator is always visible and correct.
- [ ] After 9 moves (or game ends), turn tracking stops (no further moves allowed).
- [ ] On rematch, turn resets to Player 1.

**Size:** S  
**Notes:** Straightforward turn logic; no AI complexity. Testable in pure PvP flow.

---

## Epic 3: Easy AI Mode

**Goal:** The AI plays random legal moves, allowing the human player to win some games.  
**Priority:** P0  
**Estimated Size:** M

### Stories

#### Story 3.1 — Implement Random Legal Move Selection
**As a** casual player, **I want** to play against an AI that makes random moves **so that** I can sometimes win and have fun.

**Acceptance Criteria:**
- [ ] When it is the AI's turn, the AI selects from all empty cells uniformly at random.
- [ ] The AI move is applied to the board within 500ms–1s (perceived as a thinking delay, not instant).
- [ ] Each cell has an equal probability of being selected (random uniform distribution).
- [ ] The AI never selects an already-filled cell.
- [ ] After the AI move, the turn indicator updates to "Your turn".
- [ ] Board state is updated correctly after AI move.
- [ ] Unit tests confirm random selection across 1000+ moves produces expected distribution (each cell selected ~111 times).

**Size:** M  
**Notes:** Straightforward random selection. Detached from minimax logic (deferred to Epic 4).

---

#### Story 3.2 — Trigger AI Move After Human Move in Easy Mode
**As a** player in Easy AI mode, **I want** the AI to automatically move after I move **so that** gameplay feels natural.

**Acceptance Criteria:**
- [ ] After a human move is validated (and not terminal), the game state switches to AI turn.
- [ ] Board is disabled (no cells clickable) during AI thinking phase.
- [ ] "AI thinking..." message or overlay is displayed.
- [ ] AI move is executed after thinking delay (500ms–1s).
- [ ] After AI move, board is re-enabled and turn returns to human player.
- [ ] If AI move results in win/draw, game terminal flow is triggered (see Epic 6).

**Size:** S  
**Notes:** Handles AI turn orchestration; deferred to other stories to define what the AI move itself is (random vs. minimax).

---

## Epic 4: Impossible AI Mode & Minimax Algorithm

**Goal:** The AI uses minimax with alpha-beta pruning to play optimally and never lose.  
**Priority:** P0  
**Estimated Size:** L

### Stories

#### Story 4.1 — Implement Minimax Algorithm
**As a** algorithm enthusiast, **I want** the AI to use the minimax algorithm **so that** it plays optimally and never loses.

**Acceptance Criteria:**
- [ ] Minimax function is implemented with the signature: `minimax(board, depth, isMaximizing, alpha, beta) → { score, move }`.
- [ ] Terminal state detection correctly identifies: AI win (+1), human win (−1), draw (0), ongoing (null).
- [ ] Base case: terminal states return immediate score without further recursion.
- [ ] Recursive case: For each legal move, the function applies the move, recurses, and undoes the move.
- [ ] Maximizing player (AI) selects the move with the highest score.
- [ ] Minimizing player (human) selects the move with the lowest score (via recursion, not direct call).
- [ ] Alpha-beta pruning is implemented: if `beta <= alpha`, the branch is pruned.
- [ ] Scores returned are always correct for known end-game positions (e.g., immediate three-in-a-row → +1).
- [ ] Unit tests validate minimax scores for a suite of board states (at least 50 test cases covering win/draw/ongoing scenarios).
- [ ] Minimax move completes within 2 seconds for any 3×3 board state (performance target met).

**Size:** L  
**Notes:** Core algorithm. Complexity is algorithmic, not UI. Requires comprehensive unit tests. Alpha-beta pruning is essential for performance.

---

#### Story 4.2 — Select and Execute Impossible AI Move
**As a** competitive player, **I want** the Impossible AI to choose the move that minimax evaluates as best **so that** it never loses.

**Acceptance Criteria:**
- [ ] When it is the Impossible AI's turn, minimax is called on the current board state.
- [ ] The move with the highest minimax score is selected.
- [ ] If multiple moves have the same highest score, one is selected (deterministically, e.g., smallest cell index or random among ties).
- [ ] The selected move is applied to the board.
- [ ] The move is applied within 2 seconds of the human's prior move.
- [ ] Over exhaustive play testing (all possible games), the AI wins or draws in 100% of games (never loses).
- [ ] Integration test: Play 100+ random games against Impossible AI; verify AI never loses (win rate: 50%+, draw rate: 50%−, loss rate: 0%).

**Size:** M  
**Notes:** Depends on Story 4.1 (minimax implementation). Requires integration testing and exhaustive game tree validation.

---

## Epic 5: Move Score Visualization

**Goal:** Players can see minimax evaluation scores for each possible move in Impossible AI mode.  
**Priority:** P0  
**Estimated Size:** M

### Stories

#### Story 5.1 — Compute Minimax Scores for All Legal Moves
**As a** AI learner, **I want** the game to compute minimax scores for every possible move **so that** I can see the evaluation.

**Acceptance Criteria:**
- [ ] Before the Impossible AI makes a move, minimax is run on the board to evaluate all legal moves.
- [ ] Minimax returns a score for each empty cell: +1 (AI win), 0 (draw), −1 (human win).
- [ ] Scores are computed without applying the final move yet (display-only computation).
- [ ] Scores are stored in a data structure (e.g., `Map<cellIndex, score>`) for rendering.
- [ ] Score computation completes before UI overlay is displayed (within 2 seconds).
- [ ] Filled cells are not included in score computation (only empty cells have scores).
- [ ] Unit tests verify scores match expected minimax values for known board states (e.g., one move away from win = +1).

**Size:** M  
**Notes:** Builds on Story 4.1; focuses on data collection, not rendering.

---

#### Story 5.2 — Display Scores on Board with Color & Symbol
**As a** AI learner, **I want** to see the score for each move visually on the board **so that** I can understand the AI's reasoning.

**Acceptance Criteria:**
- [ ] Before the AI moves, the board displays a score overlay on each empty cell.
- [ ] Scores are shown as symbols + colors:
  - **+1 = Green + "+" symbol** (AI wins from this move)
  - **0 = Yellow + "0" symbol** (Draw with optimal play)
  - **−1 = Red + "−" symbol** (Human wins from this move; AI avoids)
- [ ] Color choices are accessible to color-blind users (deuteranopia/protanopia safe; tested with simulator).
- [ ] Scores are overlaid on cells but do not obscure cell positions or make UI unreadable.
- [ ] Filled cells (X or O) do not display scores (scores only on empty cells).
- [ ] Score display remains for 2 seconds with label "AI is thinking..." above the board.
- [ ] After 2 seconds, score overlay clears and best move is highlighted (briefly) before AI places mark.
- [ ] CSS is responsive: scores display correctly on desktop, tablet, and mobile screens (minimum 44×44 px cells).

**Size:** M  
**Notes:** Rendering and UX logic; requires color contrast validation and responsive testing.

---

#### Story 5.3 — Clear Score Display After AI Move
**As a** player, **I want** the score display to disappear after the AI moves **so that** the board is clean for my next turn.

**Acceptance Criteria:**
- [ ] After the 2-second score display window closes, the score overlay is removed.
- [ ] The board shows only X's and O's (no scores, no labels).
- [ ] Turn indicator updates to "Your turn".
- [ ] Board is re-enabled for clicks.
- [ ] No score remnants or artifacts remain on the board.

**Size:** S  
**Notes:** Simple state transition; depends on Stories 5.1 and 5.2.

---

## Epic 6: Game State & Terminal Detection

**Goal:** The game correctly detects win, draw, and ongoing states; prevents moves after terminal states.  
**Priority:** P0  
**Estimated Size:** L

### Stories

#### Story 6.1 — Detect Win State (Three-in-a-Row)
**As a** player, **I want** the game to recognize when three marks are in a row **so that** the game ends and the winner is announced.

**Acceptance Criteria:**
- [ ] The game checks for three-in-a-row after every move (human or AI).
- [ ] Win is detected in all directions: horizontal (rows 0, 1, 2), vertical (columns 0, 1, 2), diagonal (main: 0,4,8; anti: 2,4,6).
- [ ] If three X's are in a row, human wins.
- [ ] If three O's are in a row, AI wins.
- [ ] Win is detected as soon as the winning move is placed (same turn, not delayed).
- [ ] Unit tests cover all 8 winning lines + all winning move positions (at least 72 test cases).
- [ ] Game state is updated to "terminal" (e.g., `gameStatus = 'human_win'` or `gameStatus = 'ai_win'`).

**Size:** M  
**Notes:** Core logic; deterministic. Exhaustive unit test coverage required.

---

#### Story 6.2 — Detect Draw State (Board Full)
**As a** player, **I want** the game to recognize when the board is full with no winner **so that** the game ends in a draw.

**Acceptance Criteria:**
- [ ] The game checks for a draw after every move.
- [ ] A draw is detected when: all 9 cells are filled AND no player has three-in-a-row.
- [ ] Draw is detected on the 9th move (when the last empty cell is filled).
- [ ] Game state is updated to "terminal" (e.g., `gameStatus = 'draw'`).
- [ ] Unit tests cover all full-board scenarios: standard draws, near-wins, various move orders (at least 50 test cases).

**Size:** M  
**Notes:** Straightforward logic; depends on Story 6.1 (win detection already implemented).

---

#### Story 6.3 — Prevent Moves After Game Terminal
**As a** player, **I want** the board to be locked after the game ends **so that** I cannot make invalid moves.

**Acceptance Criteria:**
- [ ] Once game state is "terminal" (win or draw), all cells become unclickable.
- [ ] Board is visually disabled (e.g., opacity reduced, cursor: not-allowed, or overlay).
- [ ] Any click on the board after terminal state is ignored (no side effects).
- [ ] Turn indicator displays the outcome (e.g., "You win!", "AI wins!", "Draw!").
- [ ] Rematch button is enabled and visible.
- [ ] Manual test: Click cells after win/draw → no effect.

**Size:** S  
**Notes:** Prevents user error; UI + state logic combined.

---

#### Story 6.4 — Display Game Outcome Message
**As a** player, **I want** to see a clear message about the game outcome **so that** I know who won or if it was a draw.

**Acceptance Criteria:**
- [ ] Upon terminal state, a message is displayed:
  - Win: "You win! 🎉" (human) or "AI wins! Well played." (AI)
  - Draw: "Draw! Perfect play."
- [ ] Message is large, centered, high-contrast (4.5:1 minimum) and positioned prominently on the screen.
- [ ] Message appears within 500ms of the terminal move.
- [ ] Emoji (optional) is included for celebratory tone but does not replace text (accessibility).
- [ ] Message remains on screen until rematch or page navigation.
- [ ] Screen reader users hear the message via ARIA live region (`aria-live="polite"`).

**Size:** S  
**Notes:** UX messaging; depends on terminal state detection (Stories 6.1 & 6.2).

---

## Epic 7: Rematch & Session Reset

**Goal:** Players can quickly start a new game after one ends, returning to mode selection or the same mode.  
**Priority:** P1  
**Estimated Size:** S

### Stories

#### Story 7.1 — Display Rematch Button After Game Ends
**As a** player, **I want** to see a "Play Again" button after the game ends **so that** I can start a new game quickly.

**Acceptance Criteria:**
- [ ] When the game reaches a terminal state (win or draw), a "Play Again" button is displayed.
- [ ] Button is prominently positioned below the board or in the message area.
- [ ] Button is at least 44×44 px and has high contrast (4.5:1 minimum).
- [ ] Button is accessible via Tab key and activated with Enter or Space.
- [ ] Button text is clear: "Play Again" or "New Game".
- [ ] Button is disabled until game is terminal (not shown during active gameplay).

**Size:** S  
**Notes:** UI element; depends on terminal state detection (Epic 6).

---

#### Story 7.2 — Reset Board and Return to Mode Selection on Rematch
**As a** player, **I want** clicking "Play Again" to reset the board and show the mode selector **so that** I can choose a mode again.

**Acceptance Criteria:**
- [ ] Clicking the rematch button clears the game board (all cells empty).
- [ ] Game state is reset (all flags cleared, counters reset).
- [ ] Mode selector screen is displayed again (three mode buttons visible).
- [ ] Outcome message disappears.
- [ ] Turn indicator and rematch button disappear.
- [ ] User can select a new mode (same or different from the previous game).
- [ ] Click on rematch button does not trigger multiple resets (debounced or one-time).

**Size:** M  
**Notes:** State reset logic; orchestrates transition between game-over state and mode selection.

---

## Epic 8: UI/UX & Responsive Design

**Goal:** The game renders correctly on desktop, tablet, and mobile; provides clear visual feedback and meets accessibility standards.  
**Priority:** P1  
**Estimated Size:** M

### Stories

#### Story 8.1 — Implement Responsive Board Layout
**As a** player on mobile or tablet, **I want** the board to scale and remain playable on my screen **so that** I can play on any device.

**Acceptance Criteria:**
- [ ] Board adapts to screen sizes: desktop (1920×1080), tablet (768×1024), mobile (375×667, 480×800).
- [ ] Each cell remains at least 44×44 px (touch target minimum).
- [ ] Board is centered on the screen.
- [ ] Mode selector buttons also scale: readable on all screen sizes, minimum 44×44 px per button.
- [ ] Text (turn indicator, outcome message) remains readable at all sizes (no overflow, responsive font sizes).
- [ ] Media queries are used: CSS breakpoints at 480px, 768px, 1024px.
- [ ] Manual test on device: iOS Safari, Android Chrome, desktop Chrome/Firefox/Safari.

**Size:** M  
**Notes:** CSS and layout work. Requires cross-device testing.

---

#### Story 8.2 — Provide Visual Feedback on Cell Interaction
**As a** player, **I want** to see visual feedback when hovering or clicking a cell **so that** I feel responsive UI.

**Acceptance Criteria:**
- [ ] Desktop: Hovering over an empty cell shows visual affordance (e.g., background color change, subtle shadow, cursor: pointer).
- [ ] Mobile/Touch: Clicking a cell triggers a brief highlight (100–200ms) before mark is placed.
- [ ] Hover state is removed when mouse leaves the cell.
- [ ] Filled cells do not show hover effects (appear static).
- [ ] After a move, the cell briefly highlights (color invert or pulse) as feedback.
- [ ] Color contrast is maintained in all states (hover, active, filled).

**Size:** S  
**Notes:** CSS animations and state changes; enhances UX responsiveness.

---

#### Story 8.3 — Implement Accessible Keyboard Navigation
**As a** keyboard-only user, **I want** to navigate and play the game using only the keyboard **so that** I can use the app independently.

**Acceptance Criteria:**
- [ ] Tab key cycles through all interactive elements: mode buttons, board cells, rematch button.
- [ ] Shift+Tab cycles backwards.
- [ ] Focus indicator is visible on all focusable elements (at least 2px border, high contrast).
- [ ] Enter and Space keys activate focused buttons and cells.
- [ ] Arrow keys can optionally be used to navigate cells (up/down/left/right from current cell).
- [ ] Focus management: after a move, focus remains accessible (does not jump unexpectedly).
- [ ] Manual test: Play full game using keyboard only (no mouse).

**Size:** M  
**Notes:** Accessibility-critical. Requires keyboard testing with actual screen reader if possible.

---

#### Story 8.4 — Apply High-Contrast Color Scheme
**As a** user with low vision, **I want** the colors to have sufficient contrast **so that** I can read text and distinguish game elements.

**Acceptance Criteria:**
- [ ] All text has a contrast ratio of at least 4.5:1 (normal text) or 3:1 (large text, 18pt+).
- [ ] Color palettes used: backgrounds, text, buttons, score indicators (green/yellow/red).
- [ ] Score colors are distinguishable by non-color-blind users and color-blind users (tested with deuteranopia/protanopia simulators).
- [ ] No information is conveyed by color alone (e.g., scores use symbols + color).
- [ ] Board cells (X, O, empty) are visually distinct (shape or high contrast).
- [ ] WCAG color contrast checker confirms compliance (WebAIM tool or similar).

**Size:** M  
**Notes:** Color & contrast validation; requires testing with accessibility tools and simulators.

---

#### Story 8.5 — Optimize Performance for Smooth Gameplay
**As a** player, **I want** the game to respond instantly to my clicks **so that** gameplay feels fluid.

**Acceptance Criteria:**
- [ ] Cell click-to-visual-feedback latency is ≤ 100ms (measured via browser DevTools).
- [ ] AI move completes within 2 seconds (performance target from NFR-01).
- [ ] No lag or stuttering during board rendering or state updates.
- [ ] No console errors or memory leaks over 10+ consecutive games (Chrome DevTools Memory profiler).
- [ ] Minimax recursion does not block the UI (optional: use Web Workers if needed, deferred if not necessary).

**Size:** S  
**Notes:** Performance validation; use browser DevTools and profiling.

---

## Technical Tasks

| ID | Task | Related Epic | Notes |
|----|------|-------------|-------|
| T-01 | Set up project structure: index.html, styles.css, main.js | All | Foundation for all stories; single-page app. |
| T-02 | Create unit test suite for minimax algorithm (50+ test cases) | Epic 4 | Comprehensive coverage of win/draw/ongoing scenarios. |
| T-03 | Create unit test suite for game state detection (win/draw/terminal) | Epic 6 | Cover all 8 winning lines, full-board draws, edge cases. |
| T-04 | Create integration test: play 100+ random games against Impossible AI | Epic 4 | Validate that AI never loses. |
| T-05 | Accessibility audit: WCAG 2.1 AA compliance check | Epic 8 | Use automated tools (axe, Lighthouse) + manual testing. |
| T-06 | Cross-browser testing: Chrome, Firefox, Safari, Edge on desktop + mobile | Epic 8 | Ensure consistent behavior and rendering. |
| T-07 | Performance profiling: measure move latency and memory usage | Epic 8 | Validate responsiveness and no memory leaks. |

---

## Traceability Matrix

| Story ID | PRD Source | Architecture Source | UX Source |
|----------|------------|---------------------|-----------|
| 1.1 | FR-01 (mode selection screen) | Component: UI Renderer, Event Handler | Flow 1 (mode selection) |
| 1.2 | FR-01, FR-02, FR-03, FR-04 (game initialization) | Data Flow: Game Initialization | Flow 1 (board display) |
| 2.1 | FR-02 (PvP mode, mark placement) | Component: Move Executor, Event Handler | Flow 2 (human move) |
| 2.2 | FR-02 (turn alternation) | Component: Game State Manager | Flow 2 (turn tracking) |
| 3.1 | FR-03 (Easy AI random moves) | Component: Easy AI, Minimax Engine | Flow 2 / 3 (AI move) |
| 3.2 | FR-03 (Easy AI flow) | Data Flow: AI Move Flow | Flow 3 (AI turn orchestration) |
| 4.1 | FR-04 (minimax algorithm) | Component: Minimax Engine, Data Model: MinimaxResult | Architecture section 5 (minimax detail) |
| 4.2 | FR-04, NFR-01 (AI plays best move, performance) | Component: Move Executor | Flow 3 (AI move execution) |
| 5.1 | FR-05 (score visualization) | Component: Score Visualizer, Data Flow: AI Move Flow | Flow 3 (score computation) |
| 5.2 | FR-05 (display scores, UI) | Component: Score Visualizer, UI Renderer | Flow 3 (score overlay display) |
| 5.3 | FR-05 (clear scores) | Component: Score Visualizer | Flow 3 (score cleanup) |
| 6.1 | FR-06 (win detection) | Component: Game State Manager | UX section 6 (win state) |
| 6.2 | FR-07 (draw detection) | Component: Game State Manager | UX section 6 (draw state) |
| 6.3 | FR-08 (prevent moves after terminal) | Component: Move Executor, Event Handler | Flow 4 (board disabled) |
| 6.4 | FR-06, FR-07 (outcome message) | Component: UI Renderer | Flow 4 (outcome message) |
| 7.1 | FR-09 (rematch button) | Component: UI Renderer | Flow 4 (rematch button) |
| 7.2 | FR-09 (rematch flow) | Component: Game State Manager, UI Renderer | Flow 4 (reset and mode selection) |
| 8.1 | FR-11 (responsive design) | Infrastructure: static deployment | UX section 6 (responsive states) |
| 8.2 | — (UX enhancement, not explicitly PRD req) | Component: UI Renderer | UX section 5 (interaction patterns) |
| 8.3 | NFR-04 (keyboard + mouse input) | Component: Event Handler | UX section 7 (keyboard navigation) |
| 8.4 | NFR-05 (high-contrast colors) | Component: UI Renderer | UX section 7 (color contrast, accessibility) |
| 8.5 | NFR-01, NFR-02, NFR-03 (performance, no leaks) | Component: Minimax Engine, Data Flow | UX section 9 (performance targets) |

---

## Open Questions & Assumptions

- **Assumption:** Users are familiar with Tic-Tac-Toe rules; no in-game tutorial is required for MVP.
- **Assumption:** Alpha-beta pruning is implemented in Story 4.1 for performance; minimax without pruning would be acceptable but slower.
- **Assumption:** Single-player games only; no multiplayer or network play in MVP.
- **Assumption:** All scores displayed as +1, 0, −1; more granular scores (e.g., −2, +2) are not needed for 3×3.
- **Open question:** Should the AI move be slightly delayed (500ms–1s) to feel like a thinking opponent, or move instantly? _(Recommend: 500ms delay for Easy AI; 1–2s for Impossible AI to display scores.)_
- **Open question:** If multiple AI moves have the same highest minimax score, should the AI pick the first, a random one, or a specific strategy? _(Recommend: Deterministic—smallest cell index—for repeatability.)_
- **Open question:** Should game history or statistics (win/loss counts) be persisted in localStorage? _(Out of scope for MVP; defer to v2.)_

---

## Out of Scope

- **Ultimate Tic-Tac-Toe:** 9×9 variant with nested boards.
- **4×4 or 5×5 grid variants:** Larger boards with 4-in-a-row or 5-in-a-row win conditions.
- **Teaching mode:** Show optimal response to suboptimal moves.
- **Difficulty knobs:** Deliberate suboptimal moves at lower levels.
- **Game history or replay:** Persistent storage or replay functionality.
- **Multiplayer online:** Network play or real-time multiplayer.
- **Native mobile app:** iOS/Android apps; web-only for MVP.
- **Backend server:** All logic is client-side; no API endpoints or database.
