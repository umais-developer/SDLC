# B3: Tic-Tac-Toe with Unbeatable AI — Requirements

**Difficulty:** Beginner
**Primary challenge areas:** Algorithm (high), State (medium), UI (medium), Visualization (medium)

---

## Challenge

Create a Tic-Tac-Toe game with three play modes: Player vs. Player, Easy AI (random legal move selection), and Impossible AI (minimax algorithm — must never lose). When playing against the Impossible AI, visualize its evaluation of each possible move by displaying the minimax score for each open cell so the player can see why the AI made its choice.

---

## Key Technical Requirements

- Minimax algorithm with correct terminal state detection (win, loss, draw)
- Alpha-beta pruning for efficiency
- Move evaluation display showing minimax scores on open cells without cluttering the UI
- Correct win, draw, and ongoing game state detection — the game must not continue after a terminal state

---

## Optional Stretch Goals

- Extension to Ultimate Tic-Tac-Toe (nine 3×3 boards forming a meta-game, where each move constrains which board the opponent must play in next)
- 4×4 or 5×5 grid variants requiring 4-in-a-row to win
- Teaching mode showing the optimal response after any suboptimal move with explanation
- Adjustable difficulty with deliberate suboptimal move selection at lower levels
