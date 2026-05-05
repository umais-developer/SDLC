# Epics & Stories: Conway's Game of Life Sandbox

**Status:** Complete  
**Author:** Product & Engineering Team  
**Date:** May 5, 2026  
**Version:** 1.0  
**Related PRD:** prd_final.md

---

## Summary

Conway's Game of Life Sandbox is a React application that enables users to simulate cellular automata interactively. The feature is organized into six epics: (1) **Core Simulation Engine** delivers accurate rule execution and efficient neighbor counting, (2) **Interactive Grid UI** provides visual grid display and cell drawing, (3) **Playback Controls** enable simulation start/stop/step and speed adjustment, (4) **Pattern Library** provides pre-built patterns for rapid exploration, (5) **Save & Load** enables pattern persistence and retrieval, and (6) **Polish & Accessibility** ensures responsive design, keyboard navigation, and performance optimization. Stories are prioritized P0 (must-have for MVP) or P1 (nice-to-have, post-MVP). All stories are independently deliverable and testable.

---

## Epic 1: Core Simulation Engine

**Goal:** Implement a correct, performant neighbor counting and rule application engine that accurately simulates Conway's Game of Life.

**Priority:** P0 (blocking all other work)

**Estimated Size:** L

### Stories

#### Story 1.1 — Implement Neighbor Counting Algorithm
**As a** developer, **I want** to count the alive neighbors for any cell on an infinite or wrapped grid **so that** I can apply Conway's rules correctly.

**Acceptance Criteria:**
- [ ] Function `countNeighbors(grid, x, y)` correctly counts alive cells in the 8 surrounding cells
- [ ] Boundary conditions handled: edge cells correctly report wrapped neighbors (toroidal topology)
- [ ] Function returns integer 0–8
- [ ] Performance: counts neighbors for all cells in a 100×100 grid in <50 ms
- [ ] Unit tests written: test edge cells, center cells, corners, and boundary wrap behavior

**Size:** M

**Notes:** This is foundational; all rule logic depends on it. Toroidal wrapping (grid wraps at edges) is the assumed boundary mode.

---

#### Story 1.2 — Implement Conway's Game of Life Rules
**As a** developer, **I want** to apply Conway's rules to compute the next generation **so that** users see correct emergent behavior.

**Acceptance Criteria:**
- [ ] Function `computeNextGeneration(grid)` applies rules to all cells:
  - A live cell with 2 or 3 neighbors survives
  - A dead cell with exactly 3 neighbors becomes alive
  - All other cells die or remain dead
- [ ] Returns a new Grid object with the next generation state
- [ ] Generation counter increments by 1 after each call
- [ ] Live cell count correctly reflects alive cells in new generation
- [ ] Unit tests written: test blinker (period 2), static blocks, known oscillators

**Size:** M

**Notes:** Correctness is critical. Unit tests must validate against at least 3 known patterns (blinker, block, beehive).

---

#### Story 1.3 — Implement Web Worker for Background Computation
**As a** a developer, **I want** to offload neighbor counting and rule application to a Web Worker **so that** the UI remains responsive during heavy simulation.

**Acceptance Criteria:**
- [ ] Web Worker process spawned on app startup
- [ ] `computeNextGeneration()` call posts message to worker with current grid
- [ ] Worker performs computation and posts result back
- [ ] UI updates from result; no blocking of render thread
- [ ] Performance on 100×100 grid at 10 gen/sec: main thread remains responsive (smooth animations, buttons responsive)
- [ ] Graceful fallback: if Web Worker unavailable, computation runs on main thread with warning logged
- [ ] Unit tests: verify worker communication works; verify fallback behavior

**Size:** L

**Notes:** Critical for performance at scale. Fallback must be tested in older browsers.

---

#### Story 1.4 — Optimize Neighbor Counting for Large Grids
**As a** a developer, **I want** to optimize neighbor counting **so that** large grids (100×100+) simulate smoothly.

**Acceptance Criteria:**
- [ ] Implement efficient algorithm (e.g., sparse grid or optimized loop) that avoids unnecessary computation
- [ ] Benchmark: 100×100 grid updates in <100 ms at normal speed
- [ ] 200×200 grid updates in <300 ms at normal speed
- [ ] Profile and identify hotspots; document optimization strategy
- [ ] No functional regressions; all existing tests still pass

**Size:** M

**Notes:** Only required if performance profiling reveals bottleneck. Otherwise, can be deferred to post-MVP.

---

## Epic 2: Interactive Grid UI

**Goal:** Provide an intuitive visual grid where users can click and drag to toggle cells.

**Priority:** P0

**Estimated Size:** L

### Stories

#### Story 2.1 — Render 2D Grid Display
**As a** user, **I want** to see a 2D grid on screen **so that** I can visualize the cellular automaton state.

**Acceptance Criteria:**
- [ ] Grid displays with default 50×50 cells
- [ ] Alive cells are visually distinct from dead cells (e.g., colored vs. empty)
- [ ] Grid fits within viewport without horizontal scrollbar (responsive)
- [ ] Each cell is at least 15×15 pixels for visibility
- [ ] Grid layout respects screen size (desktop: full grid visible; tablet: grid scales)
- [ ] No flicker or performance degradation on re-render

**Size:** M

**Notes:** Use Canvas or DOM-based grid; Canvas preferred for performance at scale.

---

#### Story 2.2 — Implement Single Cell Click Toggle
**As a** user, **I want** to click on a cell to toggle it alive or dead **so that** I can manually create patterns.

**Acceptance Criteria:**
- [ ] Clicking an alive cell toggles it dead; dead cell toggles alive
- [ ] Visual feedback (highlight or outline) appears on hover
- [ ] Click is immediate; no lag
- [ ] Live cell count updates after each toggle
- [ ] Only cells within grid bounds respond to clicks
- [ ] Touch events also work (if supported)

**Size:** S

**Notes:** Implement event listener on grid; calculate cell coordinates from mouse position.

---

#### Story 2.3 — Implement Drag-to-Toggle Cells
**As a** user, **I want** to drag my mouse across cells to toggle multiple cells at once **so that** I can draw patterns quickly.

**Acceptance Criteria:**
- [ ] Holding mouse button and dragging across cells toggles each cell under cursor
- [ ] Toggled cells are visually highlighted as dragging occurs
- [ ] Release mouse button stops toggling
- [ ] Performance: dragging across 100+ cells is smooth (no visible lag)
- [ ] Dragging outside grid bounds has no effect
- [ ] Works with both up-to-down and down-to-up drag directions

**Size:** M

**Notes:** Track `mousedown`, `mousemove`, and `mouseup` events; maintain state of toggled cells during drag.

---

#### Story 2.4 — Update Grid When Simulation Advances
**As a** user, **I want** to see the grid update each time a generation advances **so that** I can observe the simulation in real time.

**Acceptance Criteria:**
- [ ] Grid updates visually every time `computeNextGeneration()` is called
- [ ] Only changed cells are re-rendered (performance optimization)
- [ ] Update latency: <16 ms for 100×100 grid (60 FPS target)
- [ ] Generation counter and live cell count update in sync with grid
- [ ] No tearing or flicker during update

**Size:** M

**Notes:** Use React state or similar to trigger re-render. Optimize with `useMemo` or similar to only re-render changed cells.

---

#### Story 2.5 — Display Empty State Message
**As a** user, **I want** to see a helpful message when the grid is empty **so that** I know what to do next.

**Acceptance Criteria:**
- [ ] When grid has zero live cells and generation = 0, show overlay message: "Click to draw cells or select a pattern from the library"
- [ ] Message is semi-transparent, doesn't block grid interaction
- [ ] Message disappears when first cell is drawn
- [ ] Font size at least 16 pt for readability
- [ ] Accessible to screen readers (ARIA label)

**Size:** XS

**Notes:** Optional; can be shown in sidebar or as tooltip instead.

---

## Epic 3: Playback Controls

**Goal:** Enable users to start, pause, step through, and adjust simulation speed.

**Priority:** P0

**Estimated Size:** L

### Stories

#### Story 3.1 — Implement Play Button (Start Simulation)
**As a** user, **I want** to click Play to start the simulation **so that** I can see the grid evolve.

**Acceptance Criteria:**
- [ ] Play button visible in controls panel
- [ ] Clicking Play starts the simulation; grid updates each tick
- [ ] Tick rate follows current speed setting (default 10 gen/sec)
- [ ] Play button changes to Pause button while simulation running
- [ ] Generation counter increments each tick
- [ ] Live cell count updates each tick
- [ ] Play is disabled if grid has zero live cells

**Size:** M

**Notes:** Use `requestAnimationFrame()` or `setInterval()` for animation loop. Ensure Web Worker is used for computation (see Epic 1).

---

#### Story 3.2 — Implement Pause Button (Pause Simulation)
**As a** user, **I want** to click Pause to freeze the simulation **so that** I can observe a specific generation.

**Acceptance Criteria:**
- [ ] Pause button visible only while simulation is running
- [ ] Clicking Pause stops the animation loop; grid freezes
- [ ] Pause button changes to Play button
- [ ] Generation and live cell counters remain visible and frozen
- [ ] User can toggle back to Play without losing state

**Size:** S

**Notes:** Straightforward; cancel animation loop timer.

---

#### Story 3.3 — Implement Step Button (Single Generation Advance)
**As a** user, **I want** to click Step to advance exactly one generation **so that** I can carefully observe each transition.

**Acceptance Criteria:**
- [ ] Step button visible and enabled when simulation is paused or idle
- [ ] Clicking Step computes next generation and displays it
- [ ] Generation counter increments by 1
- [ ] Live cell count updates
- [ ] User can click Step multiple times in succession
- [ ] Step button is disabled while simulation is running (playing)

**Size:** S

**Notes:** Call `computeNextGeneration()` once; update UI.

---

#### Story 3.4 — Implement Speed Slider (Adjust Generation Rate)
**As a** user, **I want** to adjust a slider to control how fast the simulation ticks **so that** I can speed up or slow down observations.

**Acceptance Criteria:**
- [ ] Slider labeled "Speed" or "Generations per second"
- [ ] Slider range: 1–10 generations per second
- [ ] Default value: 10 gen/sec
- [ ] Slider updates display value in real time
- [ ] If simulation running: speed change takes effect immediately (no stutter)
- [ ] If simulation paused: new speed applies when Play is clicked next
- [ ] Keyboard accessible (slider can be adjusted via arrow keys)

**Size:** M

**Notes:** HTML5 `<input type="range">` element or custom slider component. Use event listener for smooth updates.

---

#### Story 3.5 — Implement Clear Grid Button
**As a** user, **I want** to click Clear to reset the grid to all dead cells **so that** I can start fresh without refreshing the page.

**Acceptance Criteria:**
- [ ] Clear Grid button visible in controls panel
- [ ] Clicking Clear sets all cells to dead (alive = false)
- [ ] Generation counter resets to 0
- [ ] Live cell count resets to 0
- [ ] Grid visually clears immediately
- [ ] Optional: show confirmation dialog "Resizing will clear the current pattern. Continue?"

**Size:** S

**Notes:** Optional confirmation can be added if user feedback requests it.

---

## Epic 4: Pattern Library

**Goal:** Provide users with pre-built patterns (glider, blinker, pulsar, glider gun) they can instantly place on the grid.

**Priority:** P0

**Estimated Size:** M

### Stories

#### Story 4.1 — Create Static Pattern Library Data
**As a** developer, **I want** to define the four core patterns (glider, blinker, pulsar, glider gun) as data structures **so that** they can be displayed and used.

**Acceptance Criteria:**
- [ ] Pattern data structure defined: `{ name, description, grid, width, height, tags }`
- [ ] Glider pattern defined and verified against LifeWiki
- [ ] Blinker pattern defined and verified
- [ ] Pulsar pattern defined and verified
- [ ] Glider gun pattern defined and verified
- [ ] All patterns stored in a JSON file or TypeScript constant
- [ ] Unit test: verify each pattern has correct cell count and format

**Size:** S

**Notes:** Patterns should be minimally bounding (smallest rectangle containing all alive cells). Reference: LifeWiki.

---

#### Story 4.2 — Display Pattern Library UI
**As a** user, **I want** to see a list of available patterns **so that** I can choose one to place on the grid.

**Acceptance Criteria:**
- [ ] Pattern library panel visible on screen (sidebar or modal)
- [ ] Each pattern shown with name and brief description
- [ ] Optional: thumbnail/preview of pattern
- [ ] User can click a pattern to select it
- [ ] Selected pattern is visually highlighted
- [ ] List is scrollable if patterns exceed viewport
- [ ] Keyboard navigation supported (arrow keys, Enter to select)

**Size:** M

**Notes:** UI component: list or grid of pattern cards. Keep it simple for MVP.

---

#### Story 4.3 — Implement Pattern Placement on Grid
**As a** user, **I want** to click on the grid to place a selected pattern **so that** I can position it where I want.

**Acceptance Criteria:**
- [ ] After selecting a pattern, cursor changes to crosshair or highlight
- [ ] Placement preview shown: semi-transparent overlay of pattern on grid at mouse position
- [ ] Clicking places the pattern at that grid location
- [ ] Pattern is placed at clicked cell as its top-left corner (or center; document choice)
- [ ] If pattern would extend outside grid, adjust placement or reject with error message
- [ ] Live cell count updates after placement
- [ ] Grid is editable after placement; user can draw more cells or select another pattern

**Size:** M

**Notes:** Coordinate transformation required; ensure pattern placement respects grid bounds. Empty state: show "Select a pattern first" if user tries to click without selecting.

---

#### Story 4.4 — Display Pattern Descriptions
**As a** educator, **I want** to see descriptions and metadata for each pattern **so that** I understand what I'm exploring.

**Acceptance Criteria:**
- [ ] Each pattern has a description (1–2 sentences)
- [ ] Description visible in pattern library UI or tooltip
- [ ] Metadata displayed: pattern size (e.g., "3×3"), initial cell count, period (if oscillator)
- [ ] Example descriptions:
  - Glider: "A spaceship that travels diagonally. Repeats every 4 generations."
  - Blinker: "Period 2 oscillator. Alternates between horizontal and vertical."
- [ ] Accessible: descriptions available to screen readers

**Size:** S

**Notes:** User-facing copy should be non-technical but accurate.

---

## Epic 5: Save & Load

**Goal:** Enable users to persist patterns to browser storage and reload them later.

**Priority:** P1 (nice-to-have, can defer to Sprint 2)

**Estimated Size:** M

### Stories

#### Story 5.1 — Implement Save Pattern to LocalStorage
**As a** user, **I want** to save the current grid pattern with a custom name **so that** I can reload it later without redrawing.

**Acceptance Criteria:**
- [ ] Save Pattern button visible in controls
- [ ] Clicking opens a modal with text input for pattern name
- [ ] User enters name and clicks Save
- [ ] Pattern is serialized to JSON and stored in browser LocalStorage
- [ ] Success message shown: "Pattern saved!"
- [ ] Modal closes after save
- [ ] Saved pattern persists across browser sessions (until localStorage cleared)
- [ ] Error handling:
  - Empty name: show error "Pattern name cannot be empty"
  - Duplicate name: show error "Pattern already exists"
  - Storage quota exceeded: show error "Storage full. Delete old patterns."

**Size:** M

**Notes:** Grid state serialized as 2D array of booleans. Use `JSON.stringify()` and LocalStorage API. Implement validation before save.

---

#### Story 5.2 — Implement Load Pattern from LocalStorage
**As a** user, **I want** to load a previously saved pattern **so that** I can re-explore or share it.

**Acceptance Criteria:**
- [ ] Load Pattern button visible in controls
- [ ] Clicking opens a modal showing list of all saved patterns
- [ ] If no patterns saved: empty state message "No saved patterns yet"
- [ ] User selects a pattern from the list
- [ ] Pattern preview shown: pattern name, size, cell count
- [ ] User clicks Load
- [ ] Current grid cleared and replaced with loaded pattern
- [ ] Live cell count updates
- [ ] Generation counter resets to 0
- [ ] Modal closes; grid ready to simulate
- [ ] Error handling: if pattern corrupted, show error "Pattern data corrupted"

**Size:** M

**Notes:** Deserialize JSON and restore grid state. Ensure loaded pattern fits within current grid; offer resize suggestion if needed.

---

#### Story 5.3 — Implement Delete Saved Pattern
**As a** user, **I want** to delete old saved patterns **so that** I can manage storage and keep the list clean.

**Acceptance Criteria:**
- [ ] In Load modal, each pattern has a Delete button or right-click menu option
- [ ] Clicking Delete shows confirmation: "Delete this pattern?"
- [ ] Confirming removes pattern from LocalStorage
- [ ] Pattern no longer appears in Load list
- [ ] Confirmation message shown: "Pattern deleted"
- [ ] Delete is disabled for built-in patterns (if applicable)

**Size:** S

**Notes:** Simple deletion from LocalStorage. Confirmation prevents accidental loss.

---

#### Story 5.4 — Implement Export Pattern as JSON (Optional)
**As a** user, **I want** to export a saved pattern as a JSON file **so that** I can share it or back it up.

**Acceptance Criteria:**
- [ ] Export button available in Load modal or right-click context menu
- [ ] Clicking Export downloads a JSON file named `pattern-{name}.json`
- [ ] JSON structure: `{ name, grid, width, height, cellCount }`
- [ ] File can be re-imported via Import button (see next story)
- [ ] File size reasonable (<1 MB for typical pattern)

**Size:** M

**Notes:** Optional feature; can defer to post-MVP. Use Blob and `URL.createObjectURL()` for download.

---

#### Story 5.5 — Implement Import Pattern from File (Optional)
**As a** user, **I want** to import a pattern from a JSON file **so that** I can load externally-created or shared patterns.

**Acceptance Criteria:**
- [ ] Import button visible in Load modal
- [ ] Clicking opens file chooser; user selects `.json` file
- [ ] File parsed; if valid, pattern is loaded and displayed on grid
- [ ] If invalid JSON: error "Invalid pattern file"
- [ ] If structure missing required fields: error "Pattern file corrupted"
- [ ] Imported pattern can be saved to LocalStorage as a new saved pattern

**Size:** M

**Notes:** Optional feature; can defer to post-MVP. Use `<input type="file">` and FileReader API.

---

## Epic 6: Polish & Accessibility

**Goal:** Ensure responsive design, keyboard navigation, accessibility, and performance optimization.

**Priority:** P1 (should be completed before launch)

**Estimated Size:** M

### Stories

#### Story 6.1 — Implement Keyboard Navigation
**As a** user, **I want** to navigate and control the app using keyboard only **so that** I can use it without a mouse.

**Acceptance Criteria:**
- [ ] All buttons keyboard-accessible via Tab key
- [ ] Tab order is logical (left-to-right, top-to-bottom)
- [ ] Enter or Space activates buttons
- [ ] Arrow keys adjust sliders (Speed slider)
- [ ] Grid cells focusable with Tab; spacebar toggles focused cell
- [ ] Modal dialogs: Tab cycles through inputs/buttons; Escape closes modal
- [ ] Focus indicators visible (3+ px, high contrast)

**Size:** M

**Notes:** WCAG 2.1 AA requirement. Implement via semantic HTML and ARIA attributes.

---

#### Story 6.2 — Implement Screen Reader Support
**As a** user with a screen reader, **I want** to hear meaningful labels and updates **so that** I can understand and use the app.

**Acceptance Criteria:**
- [ ] All interactive elements have `aria-label` or `<label>` associations
- [ ] Buttons announced with their purpose (e.g., "Play button" not just "button")
- [ ] Grid updates announced: "Generation 5, 24 live cells" (live region)
- [ ] Form inputs labeled: "Pattern name input"
- [ ] Error messages announced immediately
- [ ] Modal dialogs announced as modal (role="dialog", aria-modal="true")
- [ ] Test with NVDA or JAWS screen reader

**Size:** M

**Notes:** Implement `aria-live="polite"` for dynamic updates. Test with actual screen reader if possible.

---

#### Story 6.3 — Implement Responsive Layout (Desktop & Tablet)
**As a** user on a tablet, **I want** the app to adapt to smaller screens **so that** I can use it comfortably.

**Acceptance Criteria:**
- [ ] Grid and controls adapt to viewport size
- [ ] Desktop (1024px+): Grid on left, controls panel on right (or full layout)
- [ ] Tablet (768px–1023px): Grid full-width or stacked; controls below
- [ ] Mobile (< 768px): Optional; at minimum, app is usable without horizontal scroll
- [ ] Touch targets at least 44×44 px
- [ ] No horizontal overflow on any viewport size
- [ ] Test on Chrome DevTools emulator for tablet/mobile sizes

**Size:** M

**Notes:** Use CSS media queries or CSS Grid/Flexbox for responsive layout. Mobile is optional for MVP but should be noted.

---

#### Story 6.4 — Ensure Color Contrast & Readability
**As a** user with low vision, **I want** the app to have sufficient color contrast **so that** I can see everything clearly.

**Acceptance Criteria:**
- [ ] Alive cells vs. dead cells: minimum 4.5:1 contrast ratio
- [ ] All text labels: minimum 4.5:1 contrast ratio (or 3:1 for large text ≥18pt)
- [ ] Buttons and controls: sufficient contrast for visibility
- [ ] No information conveyed by color alone (e.g., error state also uses text or icon)
- [ ] Test with WebAIM contrast checker
- [ ] Document color choices in design system or README

**Size:** S

**Notes:** WCAG 2.1 AA requirement. Validate colors early in design; test before launch.

---

#### Story 6.5 — Implement Performance Monitoring & Optimization
**As a** developer, **I want** to monitor and optimize performance **so that** users experience smooth simulation at all scales.

**Acceptance Criteria:**
- [ ] Profile app using Chrome DevTools; identify bottlenecks
- [ ] Measure FPS on 100×100 grid at 10 gen/sec; target ≥30 FPS
- [ ] Measure computation time for `computeNextGeneration()` on 100×100 grid; target <100 ms
- [ ] Measure UI re-render time; target <16 ms per frame
- [ ] Optimize identified bottlenecks (memoization, canvas rendering, worker offload)
- [ ] Document optimizations in code comments
- [ ] Performance benchmarks recorded (baseline for regression testing)

**Size:** L

**Notes:** Requires profiling tools. Can be started after initial implementation; consider a separate "optimization sprint" if needed.

---

#### Story 6.6 — Implement Error Boundaries & User Feedback
**As a** user, **I want** to see clear error messages when something goes wrong **so that** I know how to recover.

**Acceptance Criteria:**
- [ ] Try-catch blocks around critical operations (compute, save, load)
- [ ] Error messages are specific and actionable:
  - ✅ "Storage full. Delete saved patterns to free space."
  - ✅ "Pattern too large for current grid. Resize the grid first."
  - ❌ "Error" (too vague)
- [ ] Errors don't crash the app; user can continue or retry
- [ ] Console warnings/errors logged for debugging (dev only)
- [ ] Test error scenarios: storage quota, invalid file format, etc.

**Size:** M

**Notes:** Implement error UI component; show errors in toast notification or modal dialog.

---

## Technical Tasks

| ID | Task | Related Stories | Notes |
|----|------|-----------------|-------|
| T-01 | Set up React project with Vite | All | Create `vite.config.ts`, ESLint, TypeScript config |
| T-02 | Set up Web Worker bundling in Vite | 1.3, 1.4 | Ensure Web Worker file is properly bundled |
| T-03 | Create unit test suite and runner (Jest/Vitest) | All stories | Test coverage target: 80%+ for critical paths (rules, neighbor counting) |
| T-04 | Set up LocalStorage abstraction layer | 5.1, 5.2, 5.3 | Reusable storage service to avoid duplication |
| T-05 | Create CSS/Tailwind design system | 2.1, 6.1–6.4 | Grid styles, button styles, color palette, spacing |
| T-06 | Set up GitHub Pages deployment workflow | All | GitHub Actions workflow to build and deploy on push |
| T-07 | Create accessibility testing checklist | 6.1, 6.2 | WCAG 2.1 AA checklist; include screen reader and keyboard testing |
| T-08 | Performance profiling setup | 1.4, 6.5 | Chrome DevTools, performance metrics logging |
| T-09 | Documentation: Rules verification & validation | 1.1, 1.2 | Document how to validate rule correctness against known patterns |
| T-10 | Create RLE pattern import utility (optional) | 5.4, 5.5 | Deferred; useful for external pattern library compatibility |

---

## Open Questions & Assumptions

- **Assumption:** All stories assume default grid size is 50×50 and max grid size is 200×200. Grid resizing as a feature is implied but should be a story if not already included.
- **Assumption:** Boundary mode is toroidal (wrapping). If edge-death mode is chosen, Story 1.1 must be adjusted.
- **Assumption:** Web Workers are available; fallback to main thread is acceptable (not critical for MVP).
- **Assumption:** LocalStorage quota is sufficient (~5–10 MB); no need for IndexedDB in MVP.
- **Assumption:** Pattern library in MVP is static (4 patterns); user-contributed patterns deferred to post-MVP.
- **Open question:** Should grid size be adjustable via UI, or fixed at 50×50 for MVP? Recommend: adjustable, so add a story if not covered.
- **Open question:** Should Undo/Redo be supported, or is it out of scope? Recommend: out of scope for MVP; defer to post-MVP.
- **Open question:** Should RLE import/export be in MVP or deferred? Recommend: deferred to post-MVP (stretch goal).

---

## Out of Scope

- **Undo/Redo functionality:** Deferred to post-MVP; requires state history stack.
- **Alternative rulesets (HighLife, Seeds, etc.):** Marked as stretch goal in PRD; deferred to post-MVP.
- **Trail mode (cell age visualization):** Stretch goal; deferred.
- **Pattern detection (auto-stabilization notification):** Stretch goal; deferred.
- **RLE import/export:** Stretch goal; deferred.
- **Multiplayer or real-time collaboration:** Out of scope; not mentioned in PRD.
- **User accounts or cloud sync:** Out of scope; purely client-side app.
- **Mobile touch optimization (beyond responsive layout):** Out of scope for MVP; can be added post-launch if demand exists.
- **Tutorials or guided onboarding:** Out of scope; MVP relies on intuitive UI and empty state messaging.
- **Dark mode / theme customization:** Out of scope for MVP; can be added as UI polish.

---

## Release Planning Notes

**Sprint 1 (MVP - Week 1–2):**
- Epic 1: Core Simulation Engine (Stories 1.1–1.3)
- Epic 2: Interactive Grid UI (Stories 2.1–2.4)
- Epic 3: Playback Controls (Stories 3.1–3.5)
- Epic 4: Pattern Library (Stories 4.1–4.3)
- Technical Tasks: T-01, T-03, T-05, T-06

**Sprint 2 (Feature Complete - Week 3–4):**
- Epic 5: Save & Load (Stories 5.1–5.3)
- Epic 6: Polish & Accessibility (Stories 6.1–6.4)
- Technical Tasks: T-02, T-04, T-07, T-08
- Optional: Story 1.4 (performance optimization) if needed

**Post-MVP (Stretch Goals):**
- Story 5.4–5.5: Import/Export
- Story 1.4: Optimization for very large grids
- Alternative rulesets, trail mode, pattern detection (see PRD stretch goals)

