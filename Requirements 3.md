# B4: Pomodoro Timer with Analytics — Requirements

**Difficulty:** Beginner
**Primary challenge areas:** UI (high), State (high), Visualization (medium)

---

## Challenge

Create a Pomodoro timer with 25-minute work intervals and 5-minute break intervals, with audio notifications at each transition. Track completed sessions per day and visualize weekly productivity as a heat map (similar to a GitHub contributions chart) where each cell represents one day and color intensity represents the number of sessions completed. Include customizable interval durations and a distraction log where users can note interruptions during a work session.

---

## Key Technical Requirements

- Accurate timing with drift correction — JavaScript's `setInterval` drifts over long sessions; the timer must compensate to maintain accuracy
- Browser notification API integration with graceful handling when permission is denied
- Local storage persistence so heat map data survives page refreshes and browser restarts
- Heat map rendered as a calendar-like grid with color-coded cells representing session counts

---

## Optional Stretch Goals

- Task association: track time spent per named task across sessions
- Long break logic: after every 4 completed pomodoros, offer a 15-minute break instead of 5
- Streak tracking with daily and weekly goals and visual badges for completed streaks
- Data export as CSV or ICS calendar file
