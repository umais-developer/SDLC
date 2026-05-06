# PRD: Snake with Replay System

**Status:** Draft  
**Author:** SDLC Pipeline  
**Date:** May 6, 2026  
**Version:** 1.0  

---

## 1. Overview
Build a web-based Snake game with real-time gameplay, scoring, and speed progression, paired with a complete replay system that records all game states for accurate playback. Users can replay completed games at variable speeds while simultaneously playing new games with ghosted replays visible on the same grid. This combines classic arcade mechanics with modern replay functionality.

---

## 2. Problem Statement
Casual gamers and puzzle enthusiasts want an engaging Snake game with the ability to review their gameplay. Current implementations lack:
- **Accurate state recording:** Most implementations cannot replay games bit-for-bit identical.
- **Simultaneous play & replay:** No mechanism to watch a ghost replay while playing live without interference.
- **Variable replay speeds:** Standard implementations offer no speed control during replay.
- **Clear visual distinction:** Ghost replays and live snakes are not visually distinguished.

---

## 3. Goals & Success Metrics
| Goal | Metric | Target | Timeframe |
|------|--------|--------|-----------|
| Core gameplay works correctly | Snake moves, eats food, scores, grows, dies on collision | 100% P0 requirement coverage | MVP |
| Replay is bit-exact accurate | Game replay produces identical sequence of states as original | 0 mismatches in test replays | MVP |
| Ghost snake coexists with live game | Ghost plays overlay on same grid; live game unaffected by ghost collision | 100% isolation verified in testing | MVP |
| User can control replay speed | Replay playback supports 0.5×, 1×, 2×, 4× speeds | All 4 speeds functional | MVP |
| Rapid input handling is safe | Pressing two keys in succession cannot reverse snake direction | Directional reversal prevented in 100% of test cases | MVP |

---

## 4. User Personas & Stakeholders
- **Primary users:** Casual gamers (ages 13–50) seeking quick, replayable arcade gameplay.
- **Secondary users / stakeholders:** Game designers/developers evaluating replay system architecture; educators using game as algorithmic teaching tool.

---

## 5. User Stories
- As a **player**, I want to **play Snake using arrow keys** so that **I can navigate and score**.
- As a **player**, I want to **see my score and the snake grow with each food item** so that **I have immediate feedback on my progress**.
- As a **player**, I want to **press arrow keys rapidly without the snake reversing direction** so that **my reflexes work as expected**.
- As a **player**, I want to **watch a replay of a previous game at multiple speeds** so that **I can analyze my performance**.
- As a **player**, I want to **play a new game while watching a ghost replay** so that **I can compare my live gameplay against a prior attempt**.
- As a **designer**, I want to **see the ghost snake visually distinct from the live snake** so that **there is no confusion about which is which**.

---

## 6. Functional Requirements
| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-01 | Live Snake Movement: Arrow keys control direction (↑↓←→) | P0 | Must prevent direction reversal in single move |
| FR-02 | Food Generation: Random food placement on grid when eaten | P0 | Food must not spawn on snake body |
| FR-03 | Score Tracking: +1 point per food consumed | P0 | Display score in real-time |
| FR-04 | Snake Growth: Snake grows by one segment per food eaten | P0 | Length determines speed increase |
| FR-05 | Speed Progression: Snake speed increases as length increases | P0 | Clear relationship between growth and velocity |
| FR-06 | Wall Collision: Game ends when snake hits grid boundary | P0 | Detect all four walls |
| FR-07 | Self-Collision: Game ends when snake head touches own body | P0 | Tail is safe until fully coiled |
| FR-08 | State Recording: All game states recorded throughout session | P0 | Every frame captured for replay |
| FR-09 | Replay List: Completed games appear in selectable list | P0 | Persisted per session |
| FR-10 | Replay Playback: Play back recorded game at variable speeds | P0 | Supports 0.5×, 1×, 2×, 4× |
| FR-11 | Ghost Snake Rendering: Replay plays as semi-transparent ghost on same grid | P0 | Distinct visual style from live snake |
| FR-12 | Simultaneous Play & Replay: Start new live game while replay runs | P0 | Ghost and live snakes coexist; ghost cannot collide with live snake |
| FR-13 | Rapid Input Safety: Two consecutive key presses cannot reverse direction | P0 | Directional buffer prevents reversal logic |

---

## 7. Non-Functional Requirements
| ID | Requirement | Category |
|----|-------------|----------|
| NFR-01 | Replay is bit-exact: any replayed game produces identical state sequence as original | Correctness |
| NFR-02 | Game loop runs at 60 FPS or better; replay playback frame-independent | Performance |
| NFR-03 | State serialization efficient enough for 1000+ frame games without lag | Performance |
| NFR-04 | Web-based; runs in modern browsers (Chrome, Firefox, Safari, Edge) | Compatibility |
| NFR-05 | Responsive canvas/grid scales to viewport without distortion | Accessibility |
| NFR-06 | Ghost snake rendering does not cause collision logic errors | Correctness |
| NFR-07 | No external libraries required for replay system (vanilla JS acceptable) | Tech Stack |

---

## 8. Scope

### In Scope
- Single-player live Snake gameplay with keyboard controls
- Score tracking and snake growth mechanics
- Collision detection (walls and self)
- Speed progression based on snake length
- Complete state recording for every game
- Replay list with selectable prior games
- Variable-speed replay playback (0.5×, 1×, 2×, 4×)
- Simultaneous live and ghost snake rendering on same grid
- Visual distinction between ghost and live snake
- Rapid input handling to prevent direction reversal
- Session-level persistence (replays stored in memory during session)

### Out of Scope
- **Multi-player or networked gameplay:** Single-player only
- **Persistent storage across sessions:** Replays clear on page reload
- **AI autopilot / pathfinding:** Not in MVP (marked as stretch goal)
- **Leaderboard or score sharing:** Out of MVP
- **Undo/rewind functionality:** Out of MVP
- **Power-ups, obstacles, or game mode variations:** Out of MVP
- **Sound effects or music:** Not required
- **Mobile touch controls:** MVP uses keyboard only

---

## 9. Dependencies & Risks
| Item | Type | Owner | Mitigation |
|------|------|-------|-----------|
| Canvas rendering performance | Risk | Dev | Profile with large grids; optimize redraw logic |
| Bit-exact replay accuracy | Dependency | Dev | Frozen random seed for food placement in replay mode; deterministic input processing |
| Ghost/live collision isolation | Risk | Dev | Ghost snake uses read-only collision lookup; live snake collision ignores ghost positions |
| Input buffering edge cases | Risk | Dev | Unit test all two-key sequences; verify no direction reversal in rapid input test suite |
| Browser compatibility | Risk | Infra | Test on Chrome, Firefox, Safari, Edge before release |

---

## 10. Open Questions & Assumptions
- **Assumption:** Grid size is fixed at 20×20 cells (standard Snake dimensions). Can adjust post-launch if needed.
- **Assumption:** All state persistence occurs in-memory during session; no backend database needed.
- **Assumption:** Replay accuracy is prioritized over storage size; no compression required for MVP.
- **Open question:** Should replay list persist across page reloads? (Answer: No, in-memory only for MVP)
- **Open question:** Should game rules (grid size, food spawn, speed curve) be configurable? (Answer: Fixed for MVP)

---

## 11. Release Criteria
- ✅ All P0 functional requirements (FR-01 through FR-13) implemented and tested
- ✅ All P0 non-functional requirements verified (NFR-01 through NFR-07)
- ✅ Bit-exact replay tested on 10+ sample games with 100% match
- ✅ Directional reversal test passes: 100 rapid two-key sequences produce no self-collision
- ✅ Ghost + live simultaneous test: 5+ concurrent games with no collision logic interference
- ✅ QA sign-off on all manual test cases
- ✅ Code review pass; no critical or blocker issues
- ✅ Deployed to production (GitHub Pages or equivalent)

---

## 12. Appendix

### References
- **Expected Outcomes:** [Expected-Outcomes 1.md](Expected-Outcomes%201.md)
- **Technical Requirements:** [Requirements 1.md](Requirements%201.md)

### Challenge Level
**Beginner** – Primary challenge areas: State (high), Algorithm (medium), UI (medium).

### Out-of-Scope Stretch Goals (for Future Releases)
- AI autopilot using A* or BFS pathfinding
- Time rewind (undo last N moves during live game)
- Leaderboard with shareable replay links encoded in URL parameters
- Obstacles and power-ups (speed boost, temporary wall pass-through)
