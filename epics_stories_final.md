# Epics & Stories: Snake with Replay System

**Status:** Draft  
**Author:** SDLC Pipeline  
**Date:** May 6, 2026  
**Version:** 1.0  
**Related PRD:** [prd_final.md](prd_final.md)  
**Related Architecture:** [architecture_final.md](architecture_final.md)  
**Related UX:** [ux_final.md](ux_final.md)

---

## Summary

The Snake with Replay System is implemented across five major epics that deliver a complete arcade game experience with replay functionality. **Epic 1 (Core Gameplay)** provides the live snake game with all standard mechanics. **Epic 2 (Input & Safety)** ensures responsive, reversal-proof keyboard input. **Epic 3 (State Recording)** captures every frame for deterministic replay. **Epic 4 (Replay Playback)** enables viewing and controlling recorded games at variable speeds. **Epic 5 (Ghost Snake & Simultaneous Play)** allows users to compare live play against prior attempts with visual distinction and collision isolation. All epics are P0 (critical path); all stories are independently testable.

---

## Epic 1: Core Snake Gameplay

**Goal:** Deliver a fully playable Snake game with score tracking, snake growth, speed progression, collision detection, and food mechanics.  
**Priority:** P0  
**Estimated Size:** L

### Stories

#### Story 1.1 — Initialize Game Grid & Spawn Snake

**As a** player, **I want** the game to initialize with a snake at the center of a 20×20 grid **so that** I can immediately start playing when the app loads.

**Acceptance Criteria:**
- [ ] Game grid displays as a 20×20 cell grid on page load
- [ ] Snake appears at center position (approximately 10, 10)
- [ ] Snake initial length is 3 segments (head + 2 body segments)
- [ ] First food item is randomly placed on an empty cell (not on snake body)
- [ ] Game loop begins automatically; no user action required to start
- [ ] Grid background is clearly visible; snake and food are visually distinct

**Size:** S  
**Notes:** This story establishes the baseline rendering and initialization; does not include movement yet (see Story 1.2).

---

#### Story 1.2 — Move Snake in Response to Directional Input

**As a** player, **I want** the snake to move in the direction indicated by my arrow key press **so that** I can navigate and control the game.

**Acceptance Criteria:**
- [ ] Pressing ↑ moves snake up by one cell on the next game tick
- [ ] Pressing ↓ moves snake down by one cell on the next game tick
- [ ] Pressing ← moves snake left by one cell on the next game tick
- [ ] Pressing → moves snake right by one cell on the next game tick
- [ ] Snake head moves; body segments follow (classic Snake behavior)
- [ ] Game loop runs at a consistent tick rate (e.g., 10 ticks per second initially)
- [ ] Movement is smooth and responsive; no lag between input and visible motion

**Size:** S  
**Notes:** See Story 2.1 for directional reversal prevention. This story focuses on basic directional movement.

---

#### Story 1.3 — Detect Wall Collisions & End Game

**As a** player, **I want** the game to end when my snake hits the grid boundary **so that** I understand when I've failed and can start over.

**Acceptance Criteria:**
- [ ] Game detects collision when snake head reaches or exceeds grid boundaries (x < 0, x >= 20, y < 0, y >= 20)
- [ ] Game ends immediately upon wall collision; snake ceases movement
- [ ] Game Over state is displayed to user (e.g., modal, end screen)
- [ ] Final score is shown on end screen
- [ ] User can choose to play again or view replays after game over
- [ ] Collision detection works on all four walls (top, bottom, left, right)

**Size:** S  
**Notes:** Collision logic is isolated per Story 1.4 (self-collision) and Story 1.3 (wall collision). Both must be tested independently.

---

#### Story 1.4 — Detect Self-Collision & End Game

**As a** player, **I want** the game to end when my snake's head touches its own body **so that** I understand when I've failed through poor control.

**Acceptance Criteria:**
- [ ] Game detects collision when snake head position equals any body segment position
- [ ] Collision only triggers after the snake has grown to at least 4 segments (no instant self-collision at start)
- [ ] Game ends immediately upon self-collision
- [ ] Tail is safe to occupy until the snake moves (no collision with tail at its current position immediately after movement)
- [ ] Final score is shown; user can replay or try again

**Size:** S  
**Notes:** Tail safety is critical: the new head position must be checked only against body segments excluding the tail's current frame (before it moves).

---

#### Story 1.5 — Eat Food & Grow Snake

**As a** player, **I want** the snake to grow by one segment when it eats food **so that** I can see my progress and increase my score.

**Acceptance Criteria:**
- [ ] When snake head moves to the same cell as food, food is consumed
- [ ] Snake grows by one segment; new segment is added at the tail end (extends snake body)
- [ ] Score increases by 1 point for each food consumed
- [ ] New food immediately spawns at a random empty cell on the grid
- [ ] Food never spawns on the snake body (live snake only; ghost snakes do not affect food spawn)
- [ ] Visual feedback: food disappears, snake body extends, score updates on screen

**Size:** M  
**Notes:** Food spawn logic must guarantee an empty cell. Consider implementing a retry or cell-finding algorithm.

---

#### Story 1.6 — Increase Speed as Snake Grows

**As a** player, **I want** the snake to move faster as it grows **so that** the game becomes more challenging and engaging.

**Acceptance Criteria:**
- [ ] Each time snake eats food and grows, movement speed increases
- [ ] Speed progression is smooth and measurable (e.g., 10% increase per segment, or fixed tick-rate increase)
- [ ] Speed increase is visible to player: faster movement is perceptible
- [ ] Speed progression has a practical upper limit (e.g., max speed at 20 segments or after 50 food items) to prevent unplayable speeds
- [ ] Speed progression is consistent across all games (same formula applies to all players)

**Size:** M  
**Notes:** Speed progression formula should be deterministic for replay accuracy. Document formula in code comments.

---

#### Story 1.7 — Display Score During Gameplay

**As a** player, **I want** to see my current score displayed at all times during the game **so that** I can track my progress.

**Acceptance Criteria:**
- [ ] Score is visible on screen during gameplay (e.g., top-left corner, HUD)
- [ ] Score updates immediately when food is consumed
- [ ] Score displays as "Score: [number]"
- [ ] Score is large enough to read comfortably
- [ ] Score persists in same location when snake moves around grid

**Size:** XS  
**Notes:** Score is a simple UI element; included with Story 1.5 (Eat Food) but separated here for clarity.

---

#### Story 1.8 — Handle Game Over & Show End Screen

**As a** player, **I want** to see a clear end screen with my final score and options to play again or review replays **so that** I know the game has ended and can decide my next action.

**Acceptance Criteria:**
- [ ] Game Over modal/screen appears when game ends (wall collision or self-collision)
- [ ] Modal displays: "Game Over" heading, "Final Score: [X]" message, buttons for "Play Again" and "View Replays"
- [ ] Modal is non-dismissible (cannot click outside to close); user must choose an action
- [ ] "Play Again" button immediately starts a new game
- [ ] "View Replays" button opens the replay list
- [ ] Modal is centered, readable, and accessible

**Size:** S  
**Notes:** Replay saving happens automatically (see Epic 3); this story focuses on the end-of-game UX flow.

---

## Epic 2: Input Handling & Directional Safety

**Goal:** Ensure responsive keyboard input with directional reversal prevention so rapid key presses cannot cause the snake to collide with itself.  
**Priority:** P0  
**Estimated Size:** M

### Stories

#### Story 2.1 — Buffer Arrow Key Input

**As a** player, **I want** my arrow key presses to be queued so that rapid key presses are not lost **so that** I can control the snake smoothly even when I press keys quickly.

**Acceptance Criteria:**
- [ ] Arrow key presses are captured and queued
- [ ] Queue holds at least 2 directional inputs to prevent loss of input
- [ ] Each game tick, the next queued direction is applied (if available)
- [ ] Older queued directions are discarded after being applied
- [ ] Rapid repeated presses (e.g., mashing the same key) do not overflow the queue; only latest is queued
- [ ] Input buffering works for all four directions equally

**Size:** S  
**Notes:** Buffering prevents input loss during fast gameplay. Reversal prevention logic (Story 2.2) checks the buffered direction before applying.

---

#### Story 2.2 — Prevent Directional Reversal

**As a** player, **I want** the snake to never reverse direction in a single move when I press two opposing keys in rapid succession **so that** I cannot accidentally cause the snake to collide with itself.

**Acceptance Criteria:**
- [ ] If snake is moving RIGHT, pressing LEFT is ignored (not queued)
- [ ] If snake is moving LEFT, pressing RIGHT is ignored
- [ ] If snake is moving UP, pressing DOWN is ignored
- [ ] If snake is moving DOWN, pressing UP is ignored
- [ ] Non-reversing key combinations (e.g., RIGHT then UP) are queued normally
- [ ] Test case: pressing RIGHT then LEFT in rapid succession results in snake moving RIGHT on next tick, then UP on following tick (not LEFT on next tick)
- [ ] Directional reversal prevention applies during live gameplay but NOT during replay (replay is deterministic)

**Size:** M  
**Notes:** Reversal check happens at the InputManager level before direction reaches GameEngine. Must test with sub-millisecond key timing.

---

#### Story 2.3 — Capture & Handle Arrow Key Events

**As a** player, **I want** arrow keys to control my snake and prevent browser default scroll behavior **so that** the game responds to my input and does not interfere with page scrolling.

**Acceptance Criteria:**
- [ ] Pressing arrow keys triggers game movement (does not scroll page)
- [ ] Arrow key events are captured with `keydown` or `keyup` listeners (to be determined during implementation)
- [ ] Browser default scroll behavior is prevented for arrow keys
- [ ] All four arrow keys (↑↓←→) are captured
- [ ] Non-arrow keys do not affect the game (no accidental movement from other keypresses)
- [ ] Input listeners are attached on app load and remain active during game
- [ ] Input listeners are detached (or ignored) when game ends or app unloads

**Size:** S  
**Notes:** Use `event.preventDefault()` to block default scroll behavior. Consider WASD keys as a future stretch goal (not in MVP).

---

## Epic 3: Game State Recording & Serialization

**Goal:** Record every game state frame-by-frame so that replays can be played back with 100% accuracy.  
**Priority:** P0  
**Estimated Size:** M

### Stories

#### Story 3.1 — Record Game State Each Frame

**As a** developer, **I want** every game state to be recorded each tick **so that** I can replay the game deterministically.

**Acceptance Criteria:**
- [ ] Each frame's state (snake position, food position, score, speed, direction) is captured and stored
- [ ] State is captured after collision detection but before rendering
- [ ] Recording begins at game start and continues until game end (no user action required)
- [ ] States are stored in a sequential array or list in memory
- [ ] State snapshots are compact (do not store redundant data)
- [ ] Recording does not significantly impact game performance (recording overhead < 5% frame time)

**Size:** M  
**Notes:** State recording is automatic and transparent to player. Recording is not pauseable (even if pause feature added, state still recorded).

---

#### Story 3.2 — Serialize Recorded Game for Storage

**As a** developer, **I want** completed games to be serializable into a compact format **so that** they can be stored and replayed later.

**Acceptance Criteria:**
- [ ] When game ends, all recorded states are serialized into a ReplayData object
- [ ] ReplayData includes: game ID, timestamp, final score, total frames, grid dimensions, frame history
- [ ] Frame history is a compact array of state snapshots (no redundant nesting)
- [ ] Serialization is synchronous; does not block the UI
- [ ] Serialized data can be deserialized without loss of information
- [ ] Serialization format is JSON-serializable (for future localStorage or server storage)

**Size:** M  
**Notes:** Serialization format should be documented for future compatibility (e.g., version field for format upgrades).

---

#### Story 3.3 — Store Completed Replays in Session Memory

**As a** player, **I want** my completed games to be saved so that I can replay them later in the same session **so that** I can review my performance.

**Acceptance Criteria:**
- [ ] When game ends, the completed replay is automatically added to a replay list (no user confirmation needed)
- [ ] Replay list persists in memory for the duration of the session (or until 50 replays; oldest purged on overflow)
- [ ] Each replay in the list is identifiable by ID, score, and timestamp
- [ ] Replays are stored in order (newest first or oldest first; document choice)
- [ ] Replay list is accessible from the replay list UI (Story 4.1)
- [ ] Replays are cleared when the page is reloaded (in-memory storage; not persistent)

**Size:** S  
**Notes:** No localStorage or backend storage in MVP. In-memory only. Overflow limit (50) prevents memory bloat.

---

## Epic 4: Replay Playback & Speed Control

**Goal:** Enable users to view recorded games at variable speeds with full visual accuracy.  
**Priority:** P0  
**Estimated Size:** L

### Stories

#### Story 4.1 — Display Replay List

**As a** player, **I want** to see a list of my completed games **so that** I can select one to replay.

**Acceptance Criteria:**
- [ ] Replay list screen displays all available replays from the session
- [ ] Each replay shows: score, date/time, and "Play" button
- [ ] List is sorted by most recent first (or oldest first; document choice)
- [ ] If no replays exist, empty state displays: "No Replays Yet. Play a game to create one!"
- [ ] Clicking a replay row or its "Play" button loads the replay and shows playback controls
- [ ] "Back" button returns to home screen
- [ ] Replay list is accessible from home screen and from game over screen

**Size:** M  
**Notes:** Replay list is a read-only view; does not modify replays. Delete functionality not in MVP.

---

#### Story 4.2 — Load Replay & Prepare Playback

**As a** player, **I want** to select a replay and see playback controls **so that** I can start watching it.

**Acceptance Criteria:**
- [ ] Clicking "Play" on a replay list item loads the replay into memory
- [ ] Playback controls appear: Play button, Pause button, Speed selector (0.5×, 1×, 2×, 4×), Back button
- [ ] Speed selector defaults to 1× (normal speed)
- [ ] Grid is visible but replay has not yet started (ghost snake not visible until Play is pressed)
- [ ] All controls are accessible and clickable
- [ ] Loading a replay does not affect the current live game state (if one is in progress)

**Size:** S  
**Notes:** Loading prepares the replay in memory but does not start playback. Game grid displays but with no ghost snake yet.

---

#### Story 4.3 — Play Replay at Selected Speed

**As a** player, **I want** to play a replay at my chosen speed **so that** I can watch my game at my own pace.

**Acceptance Criteria:**
- [ ] Clicking "Play" button starts replay playback at selected speed (default 1×)
- [ ] Ghost snake appears on grid and retraces the original game path
- [ ] Replay progresses through all recorded frames in sequence
- [ ] Replay runs at chosen speed multiplier: 0.5× is half-speed, 2× is double-speed, 4× is quadruple-speed
- [ ] Frame timing is accurate: replay duration ÷ speed multiplier = original game duration ÷ 1
- [ ] Replay playback is smooth and does not stutter
- [ ] Score and snake length are visible during replay (showing state progression)
- [ ] When replay finishes, "Replay Ended" message appears
- [ ] When replay finishes, "Restart" and "Back to Replays" buttons appear

**Size:** L  
**Notes:** Speed change does not re-buffer frames; it adjusts the playback rate in the replay game loop.

---

#### Story 4.4 — Pause & Resume Replay

**As a** player, **I want** to pause and resume a replay **so that** I can study specific moments without distraction.

**Acceptance Criteria:**
- [ ] Clicking "Pause" button during replay playback freezes the ghost snake at the current frame
- [ ] Pause button changes to "Resume" button
- [ ] While paused, ghost snake position does not change; score does not increment (frozen in time)
- [ ] Clicking "Resume" resumes playback from where it was paused
- [ ] Pausing does not lose progress; resuming continues from the paused frame
- [ ] Player can pause and resume multiple times in one replay

**Size:** S  
**Notes:** Pausing is independent of speed control; you can pause at any speed then resume at a different speed.

---

#### Story 4.5 — Change Replay Speed During Playback

**As a** player, **I want** to adjust the replay speed while it's playing **so that** I can slow down to watch closely or speed up to save time.

**Acceptance Criteria:**
- [ ] Clicking speed buttons (0.5×, 1×, 2×, 4×) during replay changes the playback speed instantly
- [ ] Speed change is smooth; no frame skipping or stuttering
- [ ] Speed change does not reset the replay; playback continues from the current frame
- [ ] Current speed is visually indicated (e.g., button highlight or label update)
- [ ] Speed can be changed multiple times during one replay
- [ ] Speed can be changed while paused (speeds list updates but playback remains paused)

**Size:** M  
**Notes:** Speed adjustment is a multiplier on the frame interval; does not require re-buffering.

---

## Epic 5: Ghost Snake & Simultaneous Live + Replay Gameplay

**Goal:** Allow users to play a new live game while watching a replay, with ghost snake visually distinct and collision-isolated from the live snake.  
**Priority:** P0  
**Estimated Size:** L

### Stories

#### Story 5.1 — Render Ghost Snake Visually Distinct from Live Snake

**As a** player, **I want** the ghost snake (replay) to be clearly distinguishable from my live snake **so that** I understand which is which during simultaneous gameplay.

**Acceptance Criteria:**
- [ ] Ghost snake is rendered in a different color or style than the live snake (e.g., light gray, dashed outline, or semi-transparent)
- [ ] Visual distinction is based on at least two attributes (color + opacity, or color + pattern), not color alone (accessibility)
- [ ] Ghost snake is readable (sufficient contrast against grid background)
- [ ] Both snakes are visible simultaneously on the same grid without overlap confusion
- [ ] Ghost snake opacity is approximately 0.5 (50% transparent) or similar
- [ ] Live snake is fully opaque (alpha 1.0)

**Size:** M  
**Notes:** Two-attribute distinction ensures screen-reader users and color-blind users can distinguish the snakes.

---

#### Story 5.2 — Start New Live Game While Replay is Playing

**As a** player, **I want** to start a new live game while watching a replay **so that** I can practice alongside the ghost snake.

**Acceptance Criteria:**
- [ ] During replay playback, user can click "New Game" button (or equivalent)
- [ ] New live game initializes on the same grid as the running replay
- [ ] Both the live game and replay continue running simultaneously
- [ ] Live snake and ghost snake are both visible
- [ ] User can control live snake with arrow keys; ghost snake is unaffected
- [ ] Live game score, food, and collision detection work independently of the replay
- [ ] Replay speed is independent of live game speed

**Size:** M  
**Notes:** This requires two separate game loops (live + replay) running concurrently. Rendering merges both onto one canvas.

---

#### Story 5.3 — Isolate Live & Ghost Collision Logic

**As a** developer, **I want** ghost snake collisions to not affect live game outcomes **so that** the ghost is purely a visual overlay.

**Acceptance Criteria:**
- [ ] Live snake collision detection ignores ghost snake entirely (ghost is not a valid collision target)
- [ ] Ghost snake collision detection does not run during simultaneous play (read-only overlay)
- [ ] If live snake head occupies same cell as ghost snake, no collision occurs; live game continues
- [ ] If live snake body overlaps ghost snake, no collision occurs
- [ ] If ghost snake food spawn coincides with ghost body, no conflict (food spawns only on empty cells relative to live snake)
- [ ] Test: live snake can pass through ghost snake without triggering game over

**Size:** M  
**Notes:** Collision checks for live snake must include a condition: `if (!isGhost)` before applying collision logic.

---

#### Story 5.4 — Handle Simultaneous Play End States

**As a** player, **I want** to understand when each snake ends so I can proceed to the next action **so that** I know when my live game or the replay is complete.

**Acceptance Criteria:**
- [ ] If live snake collides first, live game ends; replay continues (if still running)
- [ ] If replay ends first, replay stops; live game continues (if still running)
- [ ] When live game ends, end screen appears with live game score (only the live score, not replay score)
- [ ] When replay ends while live game is active, ghost snake disappears; live game continues uninterrupted
- [ ] Messages appear to indicate which snake ended (e.g., "Replay ended", "Game Over")
- [ ] User can start another live game, view replays, or exit

**Size:** M  
**Notes:** End screen should show live game score only, not replay score (to avoid confusion).

---

#### Story 5.5 — Ensure Deterministic Replay Accuracy During Simultaneous Play

**As a** developer, **I want** the ghost snake to replay identically whether playing solo or alongside a live game **so that** replay integrity is maintained.

**Acceptance Criteria:**
- [ ] Ghost snake playback is deterministic: replaying the same game always produces the same sequence of frames
- [ ] Simultaneous live game does not affect ghost snake state or timing
- [ ] Ghost snake uses recorded frame history; does not regenerate or recalculate
- [ ] Replay frame advancement is based on a separate replay timer (independent of live game tick)
- [ ] Random food spawn for live game does not affect ghost snake food positions (ghost uses recorded food from original game)
- [ ] Test: replay game A solo at 1× speed, then replay game A alongside live game B; ghost snake moves identically in both scenarios

**Size:** L  
**Notes:** This is critical for correctness. Requires careful separation of state and timing between live and replay loops.

---

## Technical Tasks

Non-user-facing work required to support the stories above. These are not user stories.

| ID | Task | Related Stories | Notes |
|----|------|-----------------|-------|
| T-01 | Set up HTML5 Canvas rendering with 2D context | 1.1, 5.1 | Initialize canvas element; create drawing context |
| T-02 | Implement fixed-tick game loop | 1.2, 3.1 | Game loop runs at fixed rate (e.g., 10 ticks/sec); independent of render frame rate |
| T-03 | Create GameEngine core class | 1.2–1.8, 2.2 | Encapsulates game logic; manages state, collision, movement |
| T-04 | Create InputManager class | 2.1–2.3 | Handles keyboard events; buffers input; checks for reversals |
| T-05 | Create StateManager class | 3.1–3.3 | Manages current game state; serialization; storage |
| T-06 | Create ReplayRecorder class | 3.1–3.3 | Records frames; finalizes on game end |
| T-07 | Create ReplayPlayer class | 4.1–4.5, 5.5 | Loads replays; manages playback timing and speed |
| T-08 | Create Renderer class | 1.1–1.8, 5.1 | Draws grid, snake (live + ghost), food, score, UI elements |
| T-09 | Create GameController orchestration layer | All stories | Coordinates all components; manages game lifecycle |
| T-10 | Implement random food spawn algorithm | 1.5 | Ensure food never spawns on snake; handle grid fullness edge case |
| T-11 | Create speed progression formula | 1.6 | Document deterministic formula for speed; test consistency |
| T-12 | Set up UI scaffolding (buttons, modals, replay list) | 4.1, 1.8 | HTML elements for play/pause/speed controls, end screen, replay list |
| T-13 | Implement localStorage or session storage for replay list | 3.3 | Store replay list for current session; clear on reload |
| T-14 | Write unit tests for input buffering & reversal logic | 2.1–2.3 | Test 100+ key-press sequences; verify no reversals |
| T-15 | Write unit tests for collision detection | 1.3–1.4 | Test all walls, self-collision, edge cases (tail safety) |
| T-16 | Write integration tests for simultaneous play | 5.1–5.5 | Live + ghost gameplay; verify isolation and determinism |
| T-17 | Write replay accuracy tests (bit-exact) | 3.1–3.3, 5.5 | Record game, replay, compare frame-by-frame; verify 100% match |

---

## Traceability Matrix

_Map each story to its source inputs so implementation can be validated against product, technical, and UX intent._

| Story ID | PRD Source | Architecture Source | UX Source |
|----------|------------|---------------------|-----------|
| 1.1 | FR-01 (Live Movement) | Component: GameEngine, Renderer | Flow: Initial App Load (Step 2) |
| 1.2 | FR-01 (Live Movement) | Component: InputManager, GameEngine | Flow: Live Game Happy Path (Step 3) |
| 1.3 | FR-06 (Wall Collision) | Component: GameEngine (collision) | Flow: Live Game Happy Path (Step 7) |
| 1.4 | FR-07 (Self-Collision) | Component: GameEngine (collision) | Flow: Live Game Happy Path (Step 7) |
| 1.5 | FR-02, FR-03, FR-04 (Food, Score, Growth) | Component: GameEngine, StateManager | Flow: Live Game Happy Path (Step 6) |
| 1.6 | FR-05 (Speed Progression) | Component: GameEngine (speed curve) | UX: Game Board — Default State; no explicit flow |
| 1.7 | FR-03 (Score Tracking) | Component: Renderer (UI display) | UX: Game Board — Score Label |
| 1.8 | FR-13 (none explicit) | Component: GameController (lifecycle) | Flow: Live Game Happy Path (Step 8) |
| 2.1 | FR-13 (Rapid Input Handling) | Component: InputManager (buffering) | Flow: Live Game — Input Edge Case (Step 2) |
| 2.2 | FR-13 (Direction Reversal Prevention) | Component: InputManager (reversal check) | Flow: Live Game — Input Edge Case (Step 4) |
| 2.3 | FR-01 (Live Movement) | Component: InputManager (event capture) | Flow: Live Game Happy Path (Step 3) |
| 3.1 | FR-08 (State Serialization) | Component: StateManager, ReplayRecorder | UX: not explicitly flow; architectural requirement |
| 3.2 | FR-08 (State Serialization) | Component: ReplayRecorder (finalization) | UX: not explicitly flow; architectural requirement |
| 3.3 | FR-09 (Replay List) | Component: StateManager, ReplayList | Flow: Initial App Load (Step 5) |
| 4.1 | FR-09 (Replay List) | Component: Renderer (list display) | Flow: Initial App Load (Step 5); Replay Selection & Playback |
| 4.2 | FR-10 (Replay Playback) | Component: ReplayPlayer (load), Renderer (controls) | Flow: Replay Selection & Playback (Step 5–6) |
| 4.3 | FR-10 (Replay Playback at Variable Speeds) | Component: ReplayPlayer (playback) | Flow: Replay Selection & Playback (Step 7) |
| 4.4 | FR-10 (implicit pause/resume) | Component: ReplayPlayer (pause state) | Flow: Replay Selection & Playback (Step 7 — User Action: Pause) |
| 4.5 | FR-10 (Variable Speeds) | Component: ReplayPlayer (speed multiplier) | Flow: Replay Selection & Playback (Step 7 — User Action: Change Speed) |
| 5.1 | FR-11 (Ghost Snake Rendering) | Component: Renderer (ghost rendering), ReplayPlayer | Flow: Live Game with Simultaneous Replay (Step 3) |
| 5.2 | FR-12 (Simultaneous Play & Replay) | Component: GameController (dual loops) | Flow: Live Game with Simultaneous Replay (Step 2) |
| 5.3 | FR-12 (Ghost Isolation) | Component: GameEngine (collision check condition) | Flow: Live Game with Simultaneous Replay (Step 7–8) |
| 5.4 | FR-12 (simultaneous end states) | Component: GameController (lifecycle coordination) | Flow: Live Game with Simultaneous Replay (Step 8) |
| 5.5 | NFR-01 (Bit-exact replay), FR-12 | Component: ReplayPlayer, StateManager, GameEngine | UX: not explicit flow; correctness requirement |

---

## Open Questions & Assumptions

- **Assumption:** Grid size remains fixed at 20×20; no runtime configuration in MVP.
- **Assumption:** Initial snake length is 3 segments; no configuration.
- **Assumption:** Speed progression formula is simple (e.g., +10% per food or fixed tick-rate increase); will be documented during implementation.
- **Assumption:** Replay list limit is 50 games; oldest auto-purged on overflow to prevent memory bloat.
- **Assumption:** In-memory storage only for MVP; no localStorage or backend persistence.
- **Assumption:** All stories are independently testable (no story depends on another).
- **Open question:** Should speed adjustment be available during live game (not just replay)? (Answer: No, not in MVP. Speed auto-progresses only with growth.)
- **Open question:** Should replays be deletable by user? (Answer: No, not in MVP. Auto-purge oldest on overflow only.)
- **Open question:** Should we log replay metadata (e.g., highest score, average survival time)? (Answer: Nice-to-have for future; not in MVP.)
- **Open question:** Is 50-replay limit sufficient, or should it be higher? (Answer: 50 is reasonable for MVP; adjust based on memory testing.)

---

## Out of Scope

The following features and stories are explicitly deferred from this breakdown:

- **AI Autopilot:** Pathfinding (A*, BFS) to navigate toward food automatically. (Marked as stretch goal in PRD)
- **Time Rewind:** Undo/rewind last N moves during live game. (Marked as stretch goal in PRD)
- **Leaderboard:** Score ranking, persistence, or sharing. (Marked as stretch goal in PRD)
- **Obstacles & Power-ups:** Speed boosts, wall pass-through, moving obstacles. (Marked as stretch goal in PRD)
- **Persistent Storage:** localStorage, server backend, or cross-session replay saving. (In-memory only for MVP)
- **Mobile Touch Controls:** Swipe or button-based input. (Keyboard only for MVP; WASD is stretch goal)
- **Sound & Music:** Audio effects or background music. (Not in MVP)
- **Fullscreen Mode:** Maximize game to viewport. (Not in MVP)
- **Custom Grid Sizes:** User-configurable grid dimensions. (Fixed at 20×20 for MVP)
- **Difficulty Levels:** Settings to adjust speed curve, grid size, or spawn rate. (Fixed for MVP)
- **Replay URL Sharing:** Encode replays in URL parameters for sharing. (Not in MVP)

---

## Appendix

### Key Links
- **PRD:** [prd_final.md](prd_final.md)
- **Architecture:** [architecture_final.md](architecture_final.md)
- **UX Design:** [ux_final.md](ux_final.md)
- **Requirements:** [Requirements 1.md](Requirements%201.md)
- **Expected Outcomes:** [Expected-Outcomes 1.md](Expected-Outcomes%201.md)

### Story Format Reference
All stories follow the format: **"As a [persona], I want [action] so that [benefit]."**
- Each story is independently deliverable and testable.
- Each story includes acceptance criteria as testable conditions.
- Each story includes an estimated size (XS/S/M/L/XL).
- Each story has notes on dependencies, edge cases, or open questions.

### Traceability Strategy
Every story maps to at least one source from PRD (Functional Requirements), Architecture (Components & Constraints), or UX (Flows & States). This ensures that no requirement is missed and every story aligns with product vision.
