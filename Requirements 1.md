# B2: Snake with Replay System — Requirements

**Difficulty:** Beginner
**Primary challenge areas:** State (high), Algorithm (medium), UI (medium)

---

## Challenge

Implement the classic Snake game with arrow key controls, increasing speed as the snake grows, and score tracking. Record all game states throughout a session and allow users to replay any completed game at variable speeds (0.5×, 1×, 2×, 4×). Include a ghost snake that shows the replay of a prior game on the same grid while the user is actively playing a new game simultaneously.

---

## Key Technical Requirements

- Input handling that prevents the snake from reversing direction in a single move and correctly handles rapid key presses
- Collision detection for walls and the snake's own body
- State serialization that records every game state in a format that can be replayed accurately and efficiently
- Ghost snake rendered on the same grid as the live game without either interfering with the other's outcome

---

## Optional Stretch Goals

- AI autopilot using A* or BFS pathfinding to navigate toward food while avoiding the snake's body
- Time rewind allowing the player to undo the last N moves during a live game
- Leaderboard with shareable replay links encoded in URL parameters
- Obstacles and power-ups (speed boost, temporary wall pass-through)
