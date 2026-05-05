# B4: Pomodoro Timer with Analytics — Expected Outcomes

---

## What the Completed Application Delivers

A user starts the timer and it counts down 25 minutes. At the end, an audio notification plays and the timer automatically transitions to a 5-minute break. At the end of the break, another notification plays and a new work session begins. Completed sessions accumulate in the daily count.

The heat map shows the current week and prior weeks as a calendar grid. Each day's cell is color-coded by session count. The data persists — reloading the page or restarting the browser shows the same heat map. The user can customize work and break durations. During a work session, the user can add entries to the distraction log without interrupting the timer.

---

## Correctness Bar

Timer accuracy is the key correctness requirement. After a 25-minute session, the elapsed time must be 25 minutes ± 1 second, regardless of whether the browser tab was in the background or the system was under load. A timer that drifts 5–10 seconds over a 25-minute session fails this bar.

The heat map must correctly attribute sessions to the correct calendar day — a session completed at 11:58 PM belongs to that day, and one completed at 12:02 AM belongs to the next. Session counts must never reset unexpectedly on reload.
