# PRD: B3 Tic-Tac-Toe with Unbeatable AI

**Status:** Final  
**Author:** Product Team  
**Date:** 2026-05-06  
**Version:** 1.0  

---

## 1. Overview
A full-featured Tic-Tac-Toe game with three play modes: Player vs. Player, Easy AI (random move selection), and Impossible AI (minimax algorithm that never loses). The Impossible AI mode will display minimax evaluation scores on each open cell so players can observe the algorithm's decision-making process in real time.

---

## 2. Problem Statement
Players want to:
- **Play casually** against another human on a shared device.
- **Practice and learn** by playing against an AI that makes increasingly challenging moves.
- **Understand AI decision-making** by seeing how the minimax algorithm evaluates each possible move and selects the optimal one.

Today, existing Tic-Tac-Toe implementations either lack difficulty progression (always trivial to beat) or provide no transparency into AI reasoning. This PRD addresses both by offering three modes with clear decision visualization.

---

## 3. Goals & Success Metrics

| Goal | Metric | Target | Timeframe |
|------|--------|--------|-----------|
| Support all three play modes | All three modes (PvP, Easy AI, Impossible AI) are fully functional and selectable | 100% functional | Sprint 1 |
| Impossible AI never loses | Exhaustive play testing confirms AI never loses—best human outcome is draw | 0 losses in test suite | Sprint 1 |
| Visualize minimax decisions | Score displayed on each open cell before AI move; scores match algorithm output | 100% score accuracy | Sprint 1 |
| Correct game state detection | Win, draw, and ongoing states detected correctly; no moves allowed after terminal state | All tests pass | Sprint 1 |
| Player clarity and trust | User can see why AI made each move; display does not clutter UI | Qualitative feedback positive | Sprint 1 |

---

## 4. User Personas & Stakeholders

- **Primary users:**
  - **Casual players:** Want a simple, fun 3×3 Tic-Tac-Toe experience; can toggle between PvP and Easy AI.
  - **AI learners:** Want to study the minimax algorithm and see how it evaluates board states; interested in Impossible AI.
  - **Algorithm enthusiasts:** Want to verify the minimax implementation is correct and explore game theory.

- **Secondary users / stakeholders:**
  - **Game developers:** Reference implementation demonstrating minimax and alpha-beta pruning best practices.
  - **Educators:** Use as a teaching tool for game theory and recursive algorithms.

---

## 5. User Stories

- As a **casual player**, I want to play Tic-Tac-Toe against a human opponent on a shared device so I can enjoy a quick game.
- As a **casual player**, I want to play Tic-Tac-Toe against an easy AI opponent so I can sometimes win and have fun.
- As a **competitive player**, I want to play against an unbeatable AI opponent so I can test my strategy and aim for draws.
- As an **AI learner**, I want to see the minimax score for each possible move before the AI plays so I understand the algorithm's reasoning.
- As an **algorithm enthusiast**, I want to verify that the AI never makes a losing move so I can trust the implementation.

---

## 6. Functional Requirements

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-01 | Display mode selection screen at game start (Player vs. Player, Easy AI, Impossible AI) | P0 | User must be able to choose play mode. |
| FR-02 | Implement Player vs. Player mode with alternating human turns | P0 | Two players alternate on shared device; turns tracked clearly. |
| FR-03 | Implement Easy AI mode with random legal move selection | P0 | AI selects from legal moves uniformly at random. |
| FR-04 | Implement Impossible AI mode using minimax algorithm | P0 | AI uses minimax to never lose; alpha-beta pruning optional but recommended. |
| FR-05 | Display minimax score for each open cell in Impossible AI mode | P0 | Scores (+1, 0, -1) shown before AI takes turn; display is uncluttered. |
| FR-06 | Detect win state and end game correctly | P0 | Game recognizes three-in-a-row (horizontal, vertical, diagonal) and announces winner. |
| FR-07 | Detect draw state and end game correctly | P0 | Game recognizes board full with no winner and announces draw. |
| FR-08 | Prevent moves after game ends | P0 | No further moves allowed once win or draw is declared. |
| FR-09 | Provide reset/rematch button after game ends | P1 | User can start a new game without page reload. |
| FR-10 | Display current game state clearly (whose turn, winner, draw) | P1 | UI clearly shows whose turn it is or if game has ended. |
| FR-11 | Responsive design works on desktop and tablet | P1 | Game plays smoothly at various screen sizes. |

---

## 7. Non-Functional Requirements

| ID | Requirement | Category |
|----|-------------|----------|
| NFR-01 | AI move is played within 2 seconds | Performance |
| NFR-02 | Minimax algorithm with alpha-beta pruning for efficiency | Performance |
| NFR-03 | No console errors or memory leaks during play | Stability |
| NFR-04 | Keyboard and mouse/touch input supported | Accessibility |
| NFR-05 | UI uses high-contrast colors for readability | Accessibility |
| NFR-06 | Static deployable (no backend required) | Scalability |

---

## 8. Scope

### In Scope
- **3×3 Tic-Tac-Toe board** with standard rules (three-in-a-row wins).
- **Three play modes:** Player vs. Player, Easy AI, Impossible AI.
- **Minimax algorithm** for Impossible AI.
- **Move score visualization** showing +1 (AI win), 0 (draw), -1 (human win) for each open cell.
- **Correct terminal state detection** (win, loss, draw).
- **Single-page static web application** deployable to GitHub Pages.
- **HTML, CSS, JavaScript** implementation (or equivalent modern web stack).

### Out of Scope
- **Ultimate Tic-Tac-Toe** (9×9 variant with nested boards) — saved for stretch goal.
- **4×4 or 5×5 grid variants** — saved for stretch goal.
- **Teaching mode** with explanations of optimal play — saved for stretch goal.
- **Difficulty knobs** (e.g., Impossible AI deliberately plays suboptimally at lower levels) — saved for stretch goal.
- **Multiplayer over network** — beyond scope of single-device game.
- **Backend/database** — not required for MVP.
- **Mobile app** (native iOS/Android) — web-only for MVP.

---

## 9. Dependencies & Risks

| Item | Type | Owner | Mitigation |
|------|------|-------|------------|
| Minimax algorithm correctness | Dependency | Engineering | Implement comprehensive test suite validating all board states; exhaustive coverage of end-to-end play. |
| Alpha-beta pruning performance | Risk | Engineering | If pruning not performant, can defer to post-MVP; minimax without pruning acceptable for 3×3. |
| UI clutter with score display | Risk | Design / Engineering | Iterative UI testing; scores overlaid subtly or in dedicated UI region. |
| Cross-browser compatibility | Risk | Engineering | Test on Chrome, Firefox, Safari, Edge during QA phase. |

---

## 10. Open Questions & Assumptions

- **Assumption:** Tic-Tac-Toe is a finite, deterministic, zero-sum game; minimax is the canonical approach.
- **Assumption:** Alpha-beta pruning is optional; game performance is acceptable with standard minimax on 3×3 boards.
- **Assumption:** Static HTML/CSS/JS is sufficient; no server-side logic required.
- **Open question:** Should score display remain visible during human's turn, or only before AI move? _(Recommend: only before AI move to reduce visual noise.)_
- **Open question:** Should Impossible AI have a slight delay before moving to avoid feeling instantaneous? _(Recommend: 1–2 second delay for UX clarity.)_

---

## 11. Release Criteria

- ✅ All P0 functional requirements met and tested.
- ✅ Minimax algorithm proven correct through exhaustive test suite.
- ✅ AI never loses in any tested game sequence.
- ✅ Scores displayed are accurate and do not clutter UI.
- ✅ Win, draw, and ongoing states detected correctly.
- ✅ No console errors or memory leaks.
- ✅ QA sign-off on manual play testing.
- ✅ Deployed to GitHub Pages and live URL verified.

---

## 12. Appendix

**Related Documents:**
- [Expected-Outcomes 2.md](Expected-Outcomes%202.md) — Definition of "done" with correctness bar and expected game behavior.
- [Requirements 2.md](Requirements%202.md) — Technical challenge areas and optional stretch goals.

**Minimax Algorithm Reference:**
- Minimax is a recursive algorithm used in zero-sum games to determine the optimal move.
- For Tic-Tac-Toe: Maximizer (AI) seeks highest score; Minimizer (human) seeks lowest score.
- Terminal states: +1 (AI win), -1 (human win), 0 (draw).

**Stretch Goals (out of scope for MVP):**
- Ultimate Tic-Tac-Toe variant.
- 4×4 or 5×5 grid variants (4-in-a-row to win).
- Teaching mode showing optimal response to any suboptimal move.
- Adjustable difficulty with deliberate suboptimal moves at lower levels.
