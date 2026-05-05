# Implementation Plan: Full Pomodoro Timer with Analytics Application

**Status:** Draft  
**Author:** SDLC Pipeline  
**Date:** May 5, 2026  
**Story:** Complete implementation of all P0/P1 epics: drift-corrected timer with automatic work/break cycling (Epic 1), audio and browser notifications (Epic 2), session persistence and heat map (Epic 3), distraction log (Epic 4), and configurable settings with long-break support (Epic 5).  
**Related Epic:** Epics 1–5 (see `epics_stories_final.md`)  
**Estimate:** L

---

## Acceptance Criteria

### Epic 1 — Core Timer
- [ ] Timer displays `25:00` on initial load with a prominent Start button.
- [ ] Timer uses `Date.now()` delta-based correction; drift ≤ ±1 second over 25 minutes.
- [ ] Start/Pause/Resume/Reset controls work correctly; Reset prompts confirmation if a session is running.
- [ ] Timer automatically transitions work→break and break→work at `0:00`.
- [ ] Session-type label and visual accent change to reflect the active phase.
- [ ] Completed work-session count (pomodoro counter) increments on each natural completion.

### Epic 2 — Notifications & Audio
- [ ] Web Audio API tone plays at each work→break and break→work transition.
- [ ] No audio plays on manual pause or reset.
- [ ] One-time notification-permission banner shown on first load; not shown again after user responds.
- [ ] Browser notification dispatched at each transition when permission is granted.
- [ ] Status chip "Notifications off — audio only" shown when permission is denied.

### Epic 3 — Session Tracking & Heat Map
- [ ] Completed session increments `pomo_session_history[YYYY-MM-DD]` in `localStorage`.
- [ ] Midnight boundary: sessions attributed using local calendar date.
- [ ] Heat map renders 12 rolling weeks (84 cells) with today at right edge.
- [ ] Cells color-coded by intensity; today's cell highlighted.
- [ ] Each cell has `aria-label` with date and session count.
- [ ] Heat map updates in real-time after session completes (no reload needed).
- [ ] Empty-state message shown when no sessions exist.
- [ ] Graceful error handling if `localStorage` read fails.

### Epic 4 — Distraction Log
- [ ] "+ Log Distraction" button visible and enabled during work sessions only.
- [ ] Text input revealed on click; timer continues uninterrupted.
- [ ] Entry saved to `localStorage` with ISO 8601 timestamp on Enter/Add click.
- [ ] Entry appears in list (newest first) with timestamp.
- [ ] Escape/Cancel clears input without saving.
- [ ] Log button disabled with tooltip during break sessions.
- [ ] Entries persist across page reloads.

### Epic 5 — Settings & Customisation
- [ ] Settings panel with Work, Short Break, and Long Break duration inputs (1–60 min).
- [ ] Validation error shown for out-of-range values.
- [ ] Settings persisted to `localStorage`; applied on next session start.
- [ ] Running session not interrupted when settings are changed.
- [ ] Long-break prompt appears after every 4 completed work sessions.
- [ ] "Start Long Break" / "Skip" options work correctly; pomodoro counter resets.

---

## Implementation Tasks

### Frontend
| ID | Task | Definition of Done | Depends On |
|----|------|--------------------|------------|
| FE-01 | Scaffold Vite + React + TypeScript project (`pomodoro-app`) | `npm run dev` serves app at localhost without errors | — |
| FE-02 | Implement `StorageService` module | All CRUD methods pass unit tests; try/catch guards present | FE-01 |
| FE-03 | Implement `useTimer` custom hook | Hook returns correct `remaining`, `isRunning` state; drift ≤ 1 s validated in test | FE-01 |
| FE-04 | Implement `useSessionCycle` custom hook | Pomodoro counter increments correctly; work↔break transitions fire; long-break at count=4 | FE-03 |
| FE-05 | Build `TimerDisplay` component | Renders MM:SS, session label, Start/Pause/Resume/Reset buttons; all states match UX spec | FE-03, FE-04 |
| FE-06 | Implement `NotificationService` module | Audio tone plays via Web Audio API; browser notification dispatched; graceful fallback confirmed | FE-01 |
| FE-07 | Build notification permission banner | One-time banner with Allow/Maybe Later; state persisted to localStorage; not shown after user responds | FE-02, FE-06 |
| FE-08 | Implement `useHeatMapData` hook | Returns correctly structured 12-week grid from localStorage; today's date at right edge | FE-02 |
| FE-09 | Build `HeatMap` component | 84 cells rendered; color-coded by intensity; today highlighted; aria-labels on every cell; tooltip on hover/focus; empty state message shown when no data | FE-08 |
| FE-10 | Build `DistractionLog` component | Add/cancel input; entries list (newest first) with timestamps; disabled during break; persists to localStorage | FE-02, FE-04 |
| FE-11 | Build `SettingsPanel` component | Work/short-break/long-break inputs with validation; save persists to localStorage; warning shown if timer running | FE-02, FE-04 |
| FE-12 | Build long-break prompt modal/overlay | Appears at pomodoro count=4; Start Long Break / Skip buttons work; pomodoro counter resets correctly | FE-04, FE-11 |
| FE-13 | Assemble `App` root layout | All components composed; responsive layout ≥ 320 px viewport; global styles applied | FE-05, FE-07, FE-09, FE-10, FE-11, FE-12 |
| FE-14 | Apply visual design — attractive, user-friendly styling | Dark/light theme with warm accent for work, cool for break; smooth animations; accessible color contrast ≥ 4.5:1 | FE-13 |
| FE-15 | Add keyboard shortcuts | Space = Start/Pause; R = Reset (with confirm); D = focus distraction log input | FE-13 |

### Data / Migrations
| ID | Task | Definition of Done | Depends On |
|----|------|--------------------|------------|
| DB-01 | Define and document localStorage schema | `pomo_session_history`, `pomo_distractions`, `pomo_settings` keys implemented in StorageService with correct TypeScript interfaces | FE-02 |
| DB-02 | Implement `localStorage` read on app init | On mount, settings and session history loaded; defaults applied when keys absent | FE-02 |

### Testing
| ID | Task | Type | Definition of Done |
|----|------|------|--------------------|
| TEST-01 | Unit test `useTimer` drift correction | Unit | Test simulates 25-min session; asserts elapsed time ≤ 26 s; mock `Date.now()` for determinism |
| TEST-02 | Unit test `useSessionCycle` transitions | Unit | Work→break, break→work, and long-break-at-4 transitions all verified |
| TEST-03 | Unit test `StorageService` | Unit | All methods tested; graceful failure on `localStorage` unavailable simulated |
| TEST-04 | Unit test `useHeatMapData` midnight boundary | Unit | Session at 23:58 → attributed to that day; session at 00:02 → next day |
| TEST-05 | Component test `HeatMap` | Integration | Renders 84 cells; aria-labels correct; today cell highlighted; empty state shown when data is empty |
| TEST-06 | Component test `DistractionLog` | Integration | Entry saved on Enter; list updates; button disabled during break state |
| TEST-07 | Component test `SettingsPanel` | Integration | Validation fires for out-of-range values; save persists to localStorage |
| TEST-08 | E2E smoke test — full session cycle | E2E | Start timer, fast-forward to 0:00 (mock timer), verify break starts, session count increments, heat map updates |

---

## Task Dependency Order

1. **FE-01** — Scaffold project (unblocks everything)
2. **FE-02, FE-03** — StorageService and useTimer hook (parallel; both unblock downstream work)
3. **DB-01, DB-02** — localStorage schema and init (parallel with FE-03)
4. **FE-04** — useSessionCycle hook (depends on FE-03)
5. **FE-06** — NotificationService (parallel with FE-04)
6. **FE-05, FE-08** — TimerDisplay component and useHeatMapData hook (parallel; FE-05 depends on FE-04)
7. **FE-07, FE-09, FE-10, FE-11** — Notification banner, HeatMap, DistractionLog, SettingsPanel components (parallel)
8. **FE-12** — Long-break prompt modal (depends on FE-04, FE-11)
9. **FE-13** — Root App assembly (depends on all components)
10. **FE-14, FE-15** — Visual design and keyboard shortcuts (depends on FE-13)
11. **TEST-01 through TEST-07** — Unit and component tests (can run in parallel with FE-14/FE-15)
12. **TEST-08** — E2E smoke test (depends on all components assembled)

---

## Risks & Unknowns
| Item | Type | Impact | Mitigation / Next Step |
|------|------|--------|------------------------|
| Browser `setInterval` throttled in background tabs (may fire as rarely as 1/min) | Risk | High — timer would drift severely | Mitigated by using `Date.now()` delta; `endTime - Date.now()` is immune to throttling |
| Web Audio API `AudioContext` blocked until user gesture | Risk | Medium — tone may not play on first transition | Resume `AudioContext` inside the Start button click handler |
| `localStorage` unavailable in strict private browsing | Unknown | Medium — data not persisted | Wrap all storage calls in try/catch; show non-blocking warning banner |
| Midnight boundary during active session | Risk | Medium — session attributed to wrong day | Use `new Date()` at `0:00` moment, not at session start |
| Heat map color contrast for adjacent intensity levels | Risk | Low-medium — accessibility failure | Choose a sequential color scale (e.g., green shades) with ≥ 3:1 contrast between adjacent levels; verify with contrast checker |

## Out of Scope / Follow-up Items
- CSV / ICS data export (deferred P2 stretch).
- Streak tracking with daily/weekly badges (deferred P2 stretch).
- Task association (linking sessions to named tasks) — deferred.
- Data pruning / retention policy for old localStorage entries — deferred.
- Service Worker / offline support — out of scope for this sprint.
- Per-session distraction entry association (entries currently tied to date only) — follow-up.

## Open Questions
- Should the pomodoro counter persist across page reloads, or reset to 0 on reload? (Current plan: reset on reload to keep implementation simple; in-progress session state is not persisted.)
- Should the app attempt to resume a session that was running when the user closed the tab? (Current plan: no — too complex for initial sprint; note in UX that reloading loses the in-progress session.)
- Exact color palette for heat map intensity scale — any brand preference, or default to GitHub-style greens?
