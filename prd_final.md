# PRD: Tic-Tac-Toe with Unbeatable AI

**Status:** Draft
**Author:** [TBD]
**Date:** May 5, 2026
**Version:** 1.0

---

## 1. Overview

A browser-based Tic-Tac-Toe game supporting three play modes: Player vs. Player, Easy AI (random legal move selection), and Impossible AI (minimax with alpha-beta pruning that never loses). When the Impossible AI is active, the evaluation scores for every open cell are overlaid on the board so the player can see the AI's reasoning in real time.

---

## 2. Problem Statement

Classic Tic-Tac-Toe implementations offer no insight into computer decision-making, making them trivial once the novelty wears off. Players who want to learn strategy or understand why the AI made a move have no visibility. The target audience — learners, casual players, and developers studying game AI — needs a version that is both challenging and transparent.

---

## 3. Goals & Success Metrics

| Goal | Metric | Target | Timeframe |
|------|--------|--------|-----------|
| Impossible AI never loses | Win/draw rate for Impossible AI over test suite | 100% draws or AI wins across all 255,168 distinct game sequences | At launch |
| Move evaluation visible | Minimax score shown on every open cell during Impossible AI's turn | Score displayed for all open cells before AI moves | At launch |
| Smooth play experience | Time from last human move to AI move displayed | < 50 ms on a mid-range device | At launch |
| Easy AI is beatable | Easy AI win rate in random playtesting | < 60% AI wins vs. random play | At launch |

---

## 4. User Personas & Stakeholders

- **Primary users:** Casual players wanting a challenging solo game; learners studying minimax / alpha-beta pruning.
- **Secondary users / stakeholders:** Developers using this as a reference implementation; educators demonstrating game AI.

---

## 5. User Stories

- As a player, I want to choose between PvP, Easy AI, and Impossible AI so that I can pick a challenge level.
- As a player, I want to see the minimax score on each open cell when playing against the Impossible AI so that I understand why the AI chose its move.
- As a player, I want the game to detect wins, losses, and draws immediately and stop accepting input so that I know the game is over.
- As a learner, I want the AI to play optimally every time so that I can use it to study perfect Tic-Tac-Toe strategy.
- As a player, I want to start a new game without refreshing the page so that I can play multiple rounds in one session.

---

## 6. Functional Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-01 | The game shall support three modes: Player vs. Player, Easy AI, Impossible AI | P0 | Mode selected before game start |
| FR-02 | The Easy AI shall select a random legal move on its turn | P0 | |
| FR-03 | The Impossible AI shall use the minimax algorithm with alpha-beta pruning | P0 | Must never lose |
| FR-04 | Terminal state detection shall identify win, loss, and draw correctly and immediately halt gameplay | P0 | No moves accepted after terminal state |
| FR-05 | When the Impossible AI is active, the minimax score for each open cell shall be displayed on that cell | P0 | Scores shown before the AI commits its move |
| FR-06 | The board shall be a standard 3×3 grid | P0 | |
| FR-07 | A "New Game" control shall reset the board and allow mode re-selection | P1 | |
| FR-08 | The current player's turn shall be clearly indicated | P1 | |
| FR-09 | The winning line (three in a row) shall be visually highlighted on game end | P1 | |

---

## 7. Non-Functional Requirements

| ID | Requirement | Category |
|----|-------------|----------|
| NFR-01 | AI move computation shall complete in under 50 ms on a mid-range device | Performance |
| NFR-02 | The application shall run entirely in the browser with no server-side dependency | Portability |
| NFR-03 | The UI shall be usable on both desktop and mobile screen sizes | Accessibility |
| NFR-04 | Minimax score overlay must not obscure the X/O symbols or the grid lines | UI/Accessibility |
| NFR-05 | All interactive elements must have sufficient colour contrast (WCAG AA) | Accessibility |

---

## 8. Scope

### In Scope
- 3×3 Tic-Tac-Toe board
- Three game modes: PvP, Easy AI (random), Impossible AI (minimax + alpha-beta)
- Real-time minimax score overlay on open cells during Impossible AI mode
- Win, draw, and ongoing state detection
- Winning line highlight
- New Game / mode reset control
- Fully client-side (HTML/CSS/JS or equivalent single-page implementation)

### Out of Scope
- Ultimate Tic-Tac-Toe (9-board meta-game) — stretch goal, not in v1
- 4×4 or 5×5 grid variants — stretch goal, not in v1
- Teaching mode with post-move explanations — stretch goal, not in v1
- Adjustable difficulty sub-levels within Easy or Impossible — stretch goal, not in v1
- Multiplayer over a network
- Persistent score tracking across sessions
- Server-side logic or backend

---

## 9. Dependencies & Risks

| Item | Type | Owner | Mitigation |
|------|------|-------|------------|
| Minimax correctness | Risk | Engineering | Validate against known perfect-play lookup table; unit test all terminal states |
| Alpha-beta pruning introducing incorrect scores in overlay | Risk | Engineering | Compute overlay scores with unmodified minimax; use alpha-beta only for the AI's move selection |
| Score overlay cluttering the board on mobile | Risk | Design | Use small, muted typography; hide overlay after AI moves |

---

## 10. Open Questions & Assumptions

- **Assumption:** The implementation is a standalone web page (HTML + JS); no framework is mandated.
- **Assumption:** The human player is always X and moves first; the AI is always O. (Mode selection may allow swapping — [TBD — needs input])
- **Open question:** Should the minimax score overlay remain visible after the AI has made its move, or clear immediately?
- **Open question:** Should the Easy AI have any artificial delay to feel more natural, or move instantly?

---

## 11. Release Criteria

- All P0 functional requirements implemented and passing manual test.
- Impossible AI validated against exhaustive game-tree: zero losses across all reachable states.
- Minimax score overlay renders correctly for all open cells without UI regression.
- Game correctly halts on all terminal states (win rows, columns, diagonals, and full board draw).
- Tested on Chrome, Firefox, and Safari (latest stable); tested on a 375 px wide viewport.

---

## 12. Appendix

- Source requirements: `Requirements 2.md`
- Minimax reference: [Wikipedia — Minimax](https://en.wikipedia.org/wiki/Minimax)
- Alpha-beta pruning reference: [Wikipedia — Alpha–beta pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)
