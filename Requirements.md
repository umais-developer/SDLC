# B1: Conway's Game of Life Sandbox — Requirements

**Difficulty:** Beginner
**Primary challenge areas:** State (high), Algorithm (medium), Visualization (medium), UI (medium)

---

## Challenge

Implement Conway's Game of Life with a resizable grid, play/pause/step controls, and adjustable simulation speed. Include a pattern library containing at least the following patterns: glider, blinker, pulsar, and glider gun. Display a generation counter and live cell count. Allow users to draw cells by clicking or dragging on the grid, and support save and load of patterns.

---

## Key Technical Requirements

- Efficient neighbor counting at scale (a 100×100 grid with 10,000 cells updated every frame)
- Boundary condition handling — grid wraps or cells die at the edge; must be explicitly defined and consistent
- Pattern storage in a format that supports reliable save and load
- Performant rendering — only changed cells re-render on each tick, not the full grid

---

## Optional Stretch Goals

- Alternative rulesets (HighLife, Day and Night, Seeds) with a visual rule editor
- Pattern detection for stable states or cycles, with a notification when the grid stabilizes
- Trail mode showing cell age with a color gradient (younger cells brighter, older cells fading)
- RLE pattern import/export for compatibility with external pattern libraries
