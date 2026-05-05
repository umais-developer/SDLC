# B3: Tic-Tac-Toe with Unbeatable AI — Expected Outcomes

---

## What the Completed Application Delivers

A user can play all three modes. In Player vs. Player mode, two players alternate turns on a shared device. In Easy AI mode, the AI plays a random legal move and can be beaten. In Impossible AI mode, the AI cannot be beaten — the best outcome a human player can achieve is a draw.

When playing against the Impossible AI, every open cell displays its minimax score before the AI takes its turn. The user can see the score assigned to each possible move and observe that the AI plays the move with the highest score.

---

## Correctness Bar

The Impossible AI must never lose — exhaustive play across all possible games confirms no path to a human win exists.

The minimax scores displayed must be correct: a cell scored +1 must lead to a forced AI win from that position; a cell scored 0 must lead to a draw with optimal play from both sides; a cell scored -1 must lead to a forced human win and must never be the AI's chosen move.

Win, draw, and ongoing states are detected correctly and the game does not continue after a terminal state is reached.
