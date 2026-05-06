# B2: Snake with Replay System — Expected Outcomes

---

## What the Completed Application Delivers

A user can play a complete Snake game. The snake moves in the direction of the last arrow key pressed, grows when it eats food, and the game ends on wall or self-collision. Score increases with each food item consumed. Speed increases as the snake grows longer.

After a game ends, the user can select it from a replay list and watch it play back at a chosen speed. The replay is accurate — every move matches what happened in the original game. While a replay is running, the user can start a new live game on the same grid; the ghost snake (the replay) plays alongside the live game, rendered visually distinct, with no effect on the live game's outcome.

---

## Correctness Bar

Pressing two arrow keys in rapid succession cannot reverse the snake's direction in a single move — pressing right then immediately left must not cause the snake to move into itself on the next tick.

The replay is bit-exact: any game can be replayed and produces the same sequence of states as the original. Ghost snake and live snake coexist on the same grid without collision logic between them — the ghost snake is a visual overlay only and cannot end the live game.
