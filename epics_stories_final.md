# Epics & Stories: Pomodoro Timer with Analytics

**Status:** Draft  
**Author:** SDLC Pipeline  
**Date:** May 5, 2026  
**Version:** 1.0  
**Related PRD:** `prd_final.md`

---

## Summary
The Pomodoro Timer with Analytics feature is broken into five epics covering: (1) the core drift-corrected timer and work/break cycling, (2) notifications and audio alerts, (3) session tracking and heat map visualisation, (4) the distraction log, and (5) user settings and customisation. All epics deliver a fully usable experience when combined; individual stories within each epic are independently deliverable and testable.

---

## Epic 1: Core Timer

**Goal:** Deliver a functional, drift-corrected countdown timer that automatically cycles between work and break sessions.  
**Priority:** P0  
**Estimated Size:** L

### Stories

#### Story 1.1 — Drift-Corrected Work Session Timer
**As a** focused worker, **I want** a countdown timer that accurately counts down 25 minutes with at most ±1 second of drift **so that** I can trust the timer to end precisely when my work session is supposed to be over.

**Acceptance Criteria:**
- [ ] Timer displays `25:00` on initial load (using default 25-minute work duration).
- [ ] Clicking **Start** begins the countdown; the display updates every second.
- [ ] Timer uses `Date.now()` delta-based correction — it does not rely solely on `setInterval` ticks for accuracy.
- [ ] After a full 25-minute session, total elapsed wall-clock time is ≤ 26 seconds from the moment Start was clicked (±1 second tolerance per the requirements).
- [ ] Clicking **Pause** freezes the countdown; clicking **Resume** continues from where it paused.
- [ ] Clicking **Reset** returns the timer to `25:00`; if the timer is running, a confirmation prompt appears before resetting.
- [ ] Timer display shows minutes and seconds in `MM:SS` format.
- [ ] Start/Pause/Reset buttons are keyboard-accessible (focus + Enter/Space).

**Size:** M  
**Notes:** Use `Date.now()` stored at start-time; each tick computes `remaining = endTime - Date.now()`. This handles background tab throttling.

---

#### Story 1.2 — Automatic Work/Break Cycling
**As a** focused worker, **I want** the timer to automatically switch between work and break sessions at each transition **so that** I don't have to manually restart the timer at the end of each session.

**Acceptance Criteria:**
- [ ] When a 25-minute work session countdown reaches `0:00`, a 5-minute break timer starts automatically without any user interaction.
- [ ] When the 5-minute break countdown reaches `0:00`, a new 25-minute work session starts automatically.
- [ ] The session-type label (e.g., "Work Session" / "Short Break") updates to reflect the active session type.
- [ ] The UI visually distinguishes work sessions from break sessions (e.g., different color accent or label).
- [ ] The timer's displayed duration resets to the correct value (work or break duration) at each transition.
- [ ] The pomodoro count (number of completed work sessions) increments by 1 each time a work session naturally completes.

**Size:** S  
**Notes:** The pomodoro count is used by the long-break logic (Story 5.2) and session history (Story 3.1); it must be tracked in shared component state.

---

## Epic 2: Notifications & Audio

**Goal:** Alert the user at every work↔break transition via audio and browser notifications, with graceful degradation when permission is denied.  
**Priority:** P0  
**Estimated Size:** M

### Stories

#### Story 2.1 — Audio Notification at Session Transitions
**As a** focused worker, **I want** an audio tone to play at each session transition **so that** I know when to switch between work and break without watching the screen.

**Acceptance Criteria:**
- [ ] A distinct audio tone plays when a work session ends (work→break transition).
- [ ] A distinct audio tone plays when a break ends (break→work transition).
- [ ] Audio is generated using the Web Audio API — no external audio files or network requests are required.
- [ ] If the Web Audio API is unavailable in the browser, the transition still occurs silently without throwing an error.
- [ ] Audio does not play when the user manually pauses or resets the timer.

**Size:** S  
**Notes:** Use `AudioContext.createOscillator()` for a simple beep tone. Ensure the `AudioContext` is resumed on user interaction to comply with browser autoplay policy.

---

#### Story 2.2 — Browser Notification at Session Transitions
**As a** focused worker, **I want** a browser push notification to appear at each session transition **so that** I'm alerted even when the Pomodoro tab is in the background.

**Acceptance Criteria:**
- [ ] On first load (and only once), a non-blocking banner prompts the user to allow browser notifications.
- [ ] If the user clicks **Allow**, the browser Notification API permission is requested.
- [ ] If permission is granted, a browser notification is dispatched at each work→break and break→work transition.
- [ ] The notification title and body clearly identify the transition (e.g., "Work session complete — take a break!" / "Break over — time to focus!").
- [ ] If permission is denied or not yet granted, a subtle status chip reads "Notifications off — audio only"; no notification is dispatched.
- [ ] The banner is shown at most once per session; it does not re-appear on subsequent page loads if the user has already responded.
- [ ] All banner controls are keyboard-accessible.

**Size:** S  
**Notes:** Store permission-request state in `localStorage` so the banner is not shown again once the user has interacted with it. Re-check `Notification.permission` on each session transition — the user may revoke permission after granting it.

---

## Epic 3: Session Tracking & Heat Map

**Goal:** Persist daily session counts and visualise them in a 12-week calendar heat map so the user can see their productivity over time.  
**Priority:** P0  
**Estimated Size:** L

### Stories

#### Story 3.1 — Daily Session Count Persistence
**As a** habit builder, **I want** each completed Pomodoro session to be recorded against the correct calendar day and persisted in the browser **so that** my productivity history is never lost when I reload the page or restart the browser.

**Acceptance Criteria:**
- [ ] When a work session naturally completes (reaches `0:00`), the count for the current calendar day (`YYYY-MM-DD`) is incremented by 1 in `localStorage`.
- [ ] Session data is stored under the key `pomo_session_history` as a JSON object mapping date strings to counts.
- [ ] On page reload, the stored data is read from `localStorage` and the counts reflect all previously completed sessions.
- [ ] A session that completes at 11:58 PM is attributed to that day; a session completing at 12:02 AM is attributed to the next day.
- [ ] If a session is paused and reset (not naturally completed), no count is recorded.
- [ ] If `localStorage` is unavailable (e.g., private browsing), the app shows a non-blocking warning "History won't be saved in private mode" and continues to function.

**Size:** S  
**Notes:** Use `new Date().toLocaleDateString('en-CA')` (returns `YYYY-MM-DD`) to ensure day attribution uses local time, not UTC.

---

#### Story 3.2 — Weekly Heat Map Visualisation
**As a** habit builder, **I want** a calendar-style heat map showing session counts for the past 12 weeks **so that** I can see patterns in my productivity at a glance.

**Acceptance Criteria:**
- [ ] A heat map grid is rendered on the page showing 12 complete weeks (84 days) with today at the right edge.
- [ ] Each cell represents one calendar day and is color-coded by session count: 0 sessions = lightest shade; high counts (≥ 8) = darkest shade; intermediate counts use proportional intermediate shades.
- [ ] Today's cell has a distinct border or highlight to make it identifiable.
- [ ] Hovering or focusing a cell shows a tooltip with the date and session count (e.g., "Monday, May 5: 3 sessions").
- [ ] Each cell has an `aria-label` in the format "[Weekday, Month DD]: [N] session(s)" for screen reader accessibility.
- [ ] When there are no sessions at all, an empty-state message is shown: "No sessions yet — start your first Pomodoro!"
- [ ] The heat map updates in real-time when a session completes during the current page load (no reload required).
- [ ] If `localStorage` data cannot be read, a non-blocking error message is shown and the heat map renders with all cells at zero.

**Size:** M  
**Notes:** The heat map reads directly from `localStorage` via the `useHeatMapData` hook defined in the architecture. Build the 12-week grid by computing the date for each of the 84 days relative to today using `new Date()` arithmetic.

---

## Epic 4: Distraction Log

**Goal:** Allow users to capture distraction notes mid-session without interrupting the running timer.  
**Priority:** P1  
**Estimated Size:** M

### Stories

#### Story 4.1 — In-Session Distraction Logging
**As an** interrupter, **I want** to type a quick distraction note during a work session and have it saved with a timestamp **so that** I can review what interrupted me without pausing my timer.

**Acceptance Criteria:**
- [ ] A **+ Log Distraction** button is visible during an active work session.
- [ ] Clicking the button reveals a text input field; the timer continues running uninterrupted.
- [ ] The user can type a distraction note and submit it by pressing **Enter** or clicking **Add**.
- [ ] On submission, the entry is saved to `localStorage` under the key `pomo_distractions` with the current timestamp (ISO 8601) and the current date.
- [ ] The submitted entry appears in a list below the input, newest first, with its timestamp displayed.
- [ ] Pressing **Escape** or clicking **Cancel** closes the input without saving.
- [ ] The **+ Log Distraction** button is disabled and visually greyed out during break sessions; a tooltip reads "Distraction log is available during work sessions only."
- [ ] Distraction entries persist across page reloads.
- [ ] All log controls are keyboard-accessible.

**Size:** M  
**Notes:** Entries are associated with the current date. If a future feature requires per-session association, the `sessionIndex` field in the data model (see architecture) already supports this. The log input gaining focus must not scroll the timer out of view on small viewports.

---

## Epic 5: Settings & Customisation

**Goal:** Allow users to configure timer durations and enable the long-break feature to adapt the Pomodoro Technique to their preferences.  
**Priority:** P1 / P2  
**Estimated Size:** M

### Stories

#### Story 5.1 — Configurable Work and Break Durations
**As a** focused worker, **I want** to set custom work and short-break durations **so that** I can adapt the Pomodoro Technique to match my personal focus capacity.

**Acceptance Criteria:**
- [ ] A **Settings** panel is accessible via a gear icon at all times (during and between sessions).
- [ ] The panel contains numeric inputs for: Work Duration (default 25 min), Short Break Duration (default 5 min).
- [ ] Each input accepts integer values from 1 to 60 (inclusive); values outside this range show an inline validation error "Must be between 1 and 60 minutes."
- [ ] Clicking **Save** persists the settings to `localStorage` under the key `pomo_settings` and closes the panel.
- [ ] If the timer is not running, the timer display immediately reflects the new work duration after saving.
- [ ] If the timer is currently running, a message informs the user "Changes will take effect after the current session"; the running session is not interrupted.
- [ ] On page load, saved settings are read from `localStorage`; if none exist, defaults are used.
- [ ] All settings inputs have associated `<label>` elements; the panel is fully keyboard-navigable.

**Size:** S  
**Notes:** Settings changes apply to the next session start, not the currently-running session.

---

#### Story 5.2 — Long Break After 4 Pomodoros
**As a** focused worker, **I want** to be offered a 15-minute long break after completing 4 consecutive Pomodoros **so that** I can recover more fully before the next focused block.

**Acceptance Criteria:**
- [ ] After every 4 completed work sessions (tracked by the internal pomodoro counter), a prompt appears: "You've completed 4 Pomodoros! Take a long break?" with **Start Long Break** and **Skip** buttons.
- [ ] Clicking **Start Long Break** starts a countdown using the long break duration (default 15 min, configurable in the Settings panel).
- [ ] Clicking **Skip** starts a regular short break immediately; the pomodoro counter resets to 0.
- [ ] After the long break ends, the pomodoro counter resets to 0 and a new work session starts automatically.
- [ ] The Long Break Duration input (default 15 min, range 1–60 min) is present in the Settings panel alongside Work Duration and Short Break Duration.
- [ ] The session-type label clearly indicates "Long Break" during a long break.
- [ ] On page reload mid-long-break, the timer does not automatically resume (consistent with normal pause behaviour).

**Size:** S  
**Notes:** This is a P2 stretch goal. The pomodoro counter needed for this story is already produced by Story 1.2.

---

## Technical Tasks
| ID | Task | Related Story | Notes |
|----|------|---------------|-------|
| T-01 | Scaffold Vite + React + TypeScript project | All | `npm create vite@latest pomodoro-app -- --template react-ts` |
| T-02 | Implement `StorageService` utility module | 3.1, 4.1, 5.1 | Wraps all `localStorage` reads/writes with try/catch |
| T-03 | Implement `useTimer` custom hook | 1.1, 1.2 | Drift-corrected timer using `Date.now()` delta |
| T-04 | Implement `useSessionCycle` custom hook | 1.2, 5.2 | Manages work/break/long-break sequencing and pomodoro counter |
| T-05 | Configure Vite base path for GitHub Pages | Stage 8 | Set `base` in `vite.config.ts` to repo name |
| T-06 | Set up GitHub Actions deploy workflow | Stage 8 | `.github/workflows/deploy.yml` triggers on `deploy/**` branches |

## Open Questions & Assumptions
- **Assumption:** The heat map shows 12 rolling weeks (84 days) with today at the right edge, matching the GitHub contributions chart pattern.
- **Assumption:** Distraction log entries are associated with the current calendar date; per-session association is deferred.
- **Assumption:** Long break (Story 5.2) is implemented as part of the initial build but is a P2 stretch.
- **Open question:** Should the pomodoro counter reset after a long break only, or also reset each calendar day?
- **Open question:** Should old `localStorage` entries be pruned after a configurable retention period to avoid storage quota issues?

## Out of Scope
- User accounts or cloud sync.
- CSV/ICS data export (optional stretch, explicitly deferred).
- Streak tracking badges (P2 stretch, deferred to a future iteration).
- Task association (linking sessions to named tasks).
- Multi-user or shared session features.
