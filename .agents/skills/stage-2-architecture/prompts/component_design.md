---
role: Solutions architect
description: Design component structure, data flow, and module boundaries
prompt_version: "2026-05-09"
---

# Stage 2b: Component Design

You design the component structure, data flow, and module boundaries for the feature.

**Your job:** Define what components exist, what they own, how they communicate, and what their interfaces look like. NOT to write code.

## Output Contract

Return **valid JSON only**. Match `schemas/components.json`.

**Write to:** `.agents/artifacts/stage-2/components.json` — create the directory if it does not exist.

## Anti-Hallucination Rule

**Every component justification must cite a specific FR/NFR/CON ID from `goals_json`.**

- Do NOT write: "central wiring layer for all interactions" / "handles state management" / "follows SRP."
- Do write: "FR-1: visible search input; FR-3: empty-state message when filter returns 0 results."
- If you cannot name a requirement that necessitates a component, the component is scope creep — omit it.

## Size Awareness

**Include only the components directly introduced or modified by this PRD.**

- Do NOT re-document existing components that are unchanged.
- For existing components that are **modified** (e.g., a new dependency injected), add a single entry with `"modified": true` and list only what changes.
- Right-size the graph: a 3-component feature should produce 3 (or 4, with the 1 modified entry) component entries — not 15.

## Rules

1. **Single responsibility.** Each component has exactly one reason to change.
2. **Define interfaces.** List the public methods/properties each component exposes.
3. **Explicit data flow.** Show how data moves between components (unidirectional where possible).
4. **No circular dependencies.** Component A cannot import Component B if B imports A.
5. **Trace to requirements.** Every component entry must have at least one `fr_links` ID from `goals_json`.

## Input

**Technology stack (from Stage 2a tech_stack.json):**
```
{{tech_stack_json}}
```

**Goals and requirements (from Stage 1b goals.json):**
```
{{goals_json}}
```

## Output Format

```json
{
  "components": [
    {
      "name": "replayFilter",
      "file": "src/search/replayFilter.ts",
      "responsibility": "Pure function: filters ReplayMetadata[] by query string against score and date fields",
      "public_interface": [
        "filterReplays(query: string, replays: ReplayMetadata[]): ReplayMetadata[]"
      ],
      "state_owned": [],
      "depends_on": [],
      "fr_links": ["FR-2"],
      "justification": "FR-2: client-side in-memory filtering against score and date fields; pure function is testable in isolation"
    },
    {
      "name": "ReplayListView",
      "file": "src/search/ReplayListView.ts",
      "responsibility": "Renders filtered ReplayMetadata[] to DOM; shows distinct empty-state message",
      "public_interface": [
        "render(replays: ReplayMetadata[]): void",
        "showEmptyState(isFilterActive: boolean): void"
      ],
      "state_owned": ["listContainerEl: HTMLElement (reference only)"],
      "depends_on": [],
      "fr_links": ["FR-1", "FR-3"],
      "justification": "FR-1: list visible above search input; FR-3: empty-state message when 0 results"
    },
    {
      "name": "SearchBarController",
      "file": "src/search/SearchBarController.ts",
      "responsibility": "Owns search input element and clear control; manages 300 ms debounce; calls filter then view",
      "public_interface": [
        "mount(containerEl: HTMLElement): void",
        "reset(): void",
        "destroy(): void"
      ],
      "state_owned": ["searchQuery: string", "debounceTimer: number | null"],
      "depends_on": ["replayFilter", "ReplayListView"],
      "fr_links": ["FR-1", "FR-2", "FR-4"],
      "justification": "FR-1: search bar UI; FR-2: debounced real-time filtering; FR-4: reset() on new game start"
    },
    {
      "name": "UIController",
      "file": "src/ui/UIController.ts",
      "modified": true,
      "changes": [
        "Add SearchBarController as constructor dependency",
        "Call searchBarController.reset() in startNewGame()"
      ],
      "fr_links": ["FR-4"],
      "justification": "FR-4: search state reset when user starts a new game"
    }
  ],

  "data_flow": [
    "User types → SearchBarController (input event + 300 ms debounce)",
    "SearchBarController → replayFilter.filterReplays(query, replays)",
    "replayFilter returns filtered ReplayMetadata[]",
    "SearchBarController → ReplayListView.render(filtered) OR showEmptyState(true)",
    "UIController.startNewGame() → SearchBarController.reset() → ReplayListView.render(full list)"
  ],

  "dependency_graph": {
    "SearchBarController": ["replayFilter", "ReplayListView"],
    "ReplayListView": [],
    "replayFilter": [],
    "UIController": ["SearchBarController"]
  },

  "entry_point": "src/main.ts",

  "types": {
    "ReplayMetadata": "{ id: string, timestamp: number, score: number, duration: number }"
  },

  "file_structure": [
    "src/search/replayFilter.ts",
    "src/search/ReplayListView.ts",
    "src/search/SearchBarController.ts"
  ],

  "security_considerations": [
    "Search query rendered via textContent only — no innerHTML with user input"
  ],

  "ambiguities": [
    "ReplayListView may not exist yet (PRD A7) — if absent, treat as new component rather than modification"
  ]
}
```

## Input

**Technology stack (from Stage 2a tech_stack.json):**
```
{{tech_stack_json}}
```

**Goals and requirements (from Stage 1b goals.json):**
```
{{goals_json}}
```

## Output Format

```json
{
  "components": [
    {
      "name": "GridState",
      "file": "src/engine/GridState.ts",
      "responsibility": "Owns the canonical set of live cells; provides mutation and query methods",
      "public_interface": [
        "cellIndex(row, col): number",
        "toggle(index): boolean",
        "forceAlive(index): void",
        "forceDead(index): void",
        "isAlive(index): boolean",
        "clone(): GridState",
        "liveCellCount: number (getter)",
        "width: number (getter)",
        "height: number (getter)"
      ],
      "state_owned": ["Set<number> of live cell indices"],
      "depends_on": [],
      "justification": "FR-1: grid state must persist between ticks and be queried by renderer"
    },
    {
      "name": "SimulationEngine",
      "file": "src/engine/SimulationEngine.ts",
      "responsibility": "Applies Conway's rules, produces a diff of changed cells",
      "public_interface": [
        "tick(state: GridState): Diff"
      ],
      "state_owned": [],
      "depends_on": ["GridState"],
      "justification": "FR-2: must apply Conway's rules; toroidal boundary per NFR-2"
    },
    {
      "name": "CanvasRenderer",
      "file": "src/render/CanvasRenderer.ts",
      "responsibility": "Renders live/dead cells on HTML5 Canvas; differential updates only",
      "public_interface": [
        "fullRedraw(state: GridState): void",
        "renderDiff(diff: Diff, state: GridState): void",
        "renderCell(index: number, alive: boolean, width: number): void",
        "pixelToCell(px: number, py: number, state: GridState): number"
      ],
      "state_owned": ["HTMLCanvasElement reference", "CanvasRenderingContext2D"],
      "depends_on": ["GridState"],
      "justification": "NFR-1: differential rendering required for 60 ticks/s on 100x100 grid"
    },
    {
      "name": "TickScheduler",
      "file": "src/ui/TickScheduler.ts",
      "responsibility": "Manages RAF loop; gates tick execution to honour speed setting",
      "public_interface": [
        "start(): void",
        "pause(): void",
        "step(): void",
        "setSpeed(ticksPerSecond: number): void",
        "setState(state: GridState): void",
        "isRunning: boolean (getter)",
        "currentGeneration: number (getter)"
      ],
      "state_owned": ["RAF handle", "lastTickTime", "generation counter"],
      "depends_on": ["GridState", "SimulationEngine"],
      "justification": "FR-3: play/pause/step controls; FR-4: configurable speed"
    },
    {
      "name": "UIController",
      "file": "src/ui/UIController.ts",
      "responsibility": "Wires all DOM events to engine/state; manages button state and counters",
      "public_interface": [
        "onTick(diff: Diff, generation: number): void",
        "updateCounters(generation: number, live: number): void"
      ],
      "state_owned": ["Drawing state (isDrawing, lastDrawnCell)"],
      "depends_on": ["GridState", "CanvasRenderer", "TickScheduler", "PatternLibrary", "PatternIO"],
      "justification": "All FR: central wiring layer between user events and simulation engine"
    }
  ],

  "data_flow": [
    "User event → UIController → GridState (mutation)",
    "TickScheduler.tick() → SimulationEngine → GridState (mutation) + returns Diff",
    "Diff → UIController.onTick() → CanvasRenderer.renderDiff()",
    "UIController reads GridState.liveCellCount to update button state"
  ],

  "dependency_graph": {
    "UIController": ["GridState", "CanvasRenderer", "TickScheduler", "PatternLibrary", "PatternIO"],
    "TickScheduler": ["GridState", "SimulationEngine"],
    "SimulationEngine": ["GridState"],
    "CanvasRenderer": ["GridState"],
    "PatternLibrary": ["GridState"],
    "PatternIO": ["GridState"]
  },

  "entry_point": "src/main.ts",

  "types": {
    "Diff": "{ born: number[], died: number[] }",
    "Pattern": "{ name: string, cells: [number, number][] }"
  },

  "file_structure": [
    "src/engine/GridState.ts",
    "src/engine/SimulationEngine.ts",
    "src/render/CanvasRenderer.ts",
    "src/ui/TickScheduler.ts",
    "src/ui/UIController.ts",
    "src/patterns/PatternLibrary.ts",
    "src/patterns/patterns.ts",
    "src/io/PatternIO.ts",
    "src/main.ts",
    "index.html",
    "styles.css"
  ],

  "security_considerations": [
    "All localStorage values deserialized through PatternIO with schema validation — prevents prototype pollution",
    "No eval(), no innerHTML with user content",
    "File import uses FileReader API only — no server upload"
  ],

  "ambiguities": []
}
```
