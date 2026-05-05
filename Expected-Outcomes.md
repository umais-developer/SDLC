# B1: Conway's Game of Life Sandbox — Expected Outcomes

---

## What the Completed Application Delivers

A user can open the application and immediately interact with a live simulation. Clicking or dragging on the grid toggles cells on and off. Pressing Play starts the simulation; the grid updates at the configured speed. Pressing Pause freezes it at the current generation. Pressing Step advances exactly one generation. The generation counter and live cell count update in real time.

The pattern library contains at least a glider, blinker, pulsar, and glider gun. Selecting a pattern stamps it onto the grid at a chosen position. A user can save the current grid state and reload it later, with the saved pattern appearing exactly as it was saved.

---

## Correctness Bar

The simulation follows Conway's rules exactly: a live cell with 2 or 3 neighbors survives; a dead cell with exactly 3 neighbors becomes live; all others die or stay dead. This is verifiable by loading a known pattern (glider) and confirming it moves in the expected direction over the expected number of generations.

The grid boundary behavior is consistent (either wrapping or dying at edges) and does not change during a session.

Performance remains acceptable at a 100×100 grid — the simulation does not visibly stutter or lag at normal speeds.
