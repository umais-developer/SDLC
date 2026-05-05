# Conway's Game of Life Sandbox

A beautiful, interactive React application for exploring Conway's Game of Life with pattern library, playback controls, and save/load functionality.

## Features

✅ **Correct Simulation** — Accurately implements Conway's Game of Life rules
✅ **Interactive Grid** — Click and drag to draw cells
✅ **Playback Controls** — Play, Pause, Step, and Speed adjustment
✅ **Pattern Library** — Pre-built patterns: Glider, Blinker, Block, Pulsar
✅ **Responsive Design** — Desktop and tablet optimized
✅ **Performance** — Uses Web Workers for smooth simulation at scale (100×100 grid at 10 gen/sec)

## Getting Started

### Prerequisites
- Node.js 16+ and npm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173 in your browser
```

### Build for Production

```bash
npm run build
npm run preview
```

## Development

### Running Tests

```bash
# Run all tests
npm test

# Run tests with UI
npm test:ui
```

### Project Structure

```
src/
├── components/         # React components
│   ├── Grid.tsx       # Grid rendering (Canvas)
│   ├── ControlsPanel.tsx  # Play/Pause/Step/Speed controls
│   └── PatternLibrary.tsx # Pattern selection and placement
├── context/           # React Context for state management
│   └── GameContext.tsx
├── engine/            # Core simulation logic
│   ├── grid.ts        # Grid data structure and utilities
│   ├── rules.ts       # Conway's Game of Life rules
│   ├── rules.test.ts  # Rule engine tests
│   └── game-of-life.worker.ts  # Web Worker for background computation
├── hooks/             # Custom React hooks
│   └── useGameOfLife.ts  # Game engine hook with worker support
├── App.tsx            # Main app component
└── main.tsx           # Entry point
```

## How to Use

1. **Draw Cells**: Click or drag on the grid to toggle cells alive/dead
2. **Use Patterns**: Select from the Pattern Library to instantly place predefined patterns
3. **Control Simulation**: Use Play/Pause buttons to control the animation
4. **Adjust Speed**: Use the speed slider (1-10 generations per second)
5. **Step Through**: Click Step to advance exactly one generation
6. **Resize Grid**: Click Resize to change grid dimensions (10-200)
7. **Clear**: Click Clear to reset all cells

## How It Works

### Conway's Game of Life Rules
- A live cell with 2 or 3 neighbors survives
- A dead cell with exactly 3 neighbors becomes alive
- All other cells die or remain dead

### Boundary Conditions
Grid wraps at edges (toroidal topology) — cells are treated as if they exist on a torus.

### Performance
- Computation runs in a Web Worker to keep UI responsive
- Grid rendering uses Canvas for efficiency
- Only changed cells are re-rendered

## Known Patterns

- **Glider**: A spaceship that travels diagonally (repeats every 4 generations)
- **Blinker**: Oscillates between horizontal and vertical (period 2)
- **Block**: Stable 2×2 square (period 0)
- **Pulsar**: Complex period 3 oscillator

## Future Enhancements

- Save/load patterns to browser storage
- Import/export RLE format (compatibility with external libraries)
- Alternative rulesets (HighLife, Seeds, etc.)
- Trail mode (cell age visualization)
- Pattern detection and auto-save on stabilization
- Undo/Redo functionality

## Technologies

- **React 18** — UI framework
- **TypeScript** — Type safety
- **Vite** — Build tool
- **Tailwind CSS** — Styling
- **Vitest** — Testing framework
- **Web Workers** — Background computation

## License

MIT

## References

- [Conway's Game of Life (Wikipedia)](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
- [LifeWiki](http://www.conwaylife.com/)

