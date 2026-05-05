import React, { useCallback, useState } from 'react';
import type { PomodoroSettings, SessionType, TimerState } from '../types';
import { CircularProgress } from './CircularProgress';

interface TimerDisplayProps {
  remaining: number; // ms
  totalDuration: number; // ms
  timerState: TimerState;
  sessionType: SessionType;
  pomodoroCount: number;
  settings: PomodoroSettings;
  onStart: () => void;
  onPause: () => void;
  onResume: () => void;
  onReset: () => void;
  onOpenSettings: () => void;
}

const SESSION_LABELS: Record<SessionType, string> = {
  work: 'Work Session',
  shortBreak: 'Short Break',
  longBreak: 'Long Break',
};

const SESSION_COLORS: Record<SessionType, string> = {
  work: '#ff6b6b',
  shortBreak: '#4ecdc4',
  longBreak: '#a78bfa',
};

function formatTime(ms: number): string {
  const totalSeconds = Math.ceil(ms / 1000);
  const m = Math.floor(totalSeconds / 60);
  const s = totalSeconds % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

export function TimerDisplay({
  remaining,
  totalDuration,
  timerState,
  sessionType,
  pomodoroCount,
  settings,
  onStart,
  onPause,
  onResume,
  onReset,
}: TimerDisplayProps) {
  const [resetConfirm, setResetConfirm] = useState(false);
  const progress = totalDuration > 0 ? remaining / totalDuration : 1;
  const color = SESSION_COLORS[sessionType];
  const label = SESSION_LABELS[sessionType];
  const timeStr = formatTime(remaining);

  const handleResetClick = useCallback(() => {
    if (timerState === 'running' || timerState === 'paused') {
      if (!resetConfirm) {
        setResetConfirm(true);
        setTimeout(() => setResetConfirm(false), 3000);
        return;
      }
    }
    setResetConfirm(false);
    onReset();
  }, [timerState, resetConfirm, onReset]);

  const handleStartPause = useCallback(() => {
    setResetConfirm(false);
    if (timerState === 'idle') onStart();
    else if (timerState === 'running') onPause();
    else onResume();
  }, [timerState, onStart, onPause, onResume]);

  const startPauseLabel =
    timerState === 'running' ? 'Pause' : timerState === 'paused' ? 'Resume' : 'Start';
  const startPauseAriaLabel =
    timerState === 'running'
      ? 'Pause timer'
      : timerState === 'paused'
        ? 'Resume timer'
        : 'Start timer';

  // Pomodoro dot indicators (show up to longBreakInterval dots)
  const dots = Array.from({ length: settings.longBreakInterval }, (_, i) => (
    <span
      key={i}
      className={`pomo-dot ${i < pomodoroCount % settings.longBreakInterval ? 'pomo-dot--filled' : ''}`}
      aria-hidden="true"
    />
  ));

  return (
    <section className="timer-section" aria-label="Pomodoro timer">
      {/* Session type badge */}
      <div className="session-badge" style={{ '--session-color': color } as React.CSSProperties}>
        {label}
      </div>

      {/* Pomodoro dots */}
      <div className="pomo-dots" aria-label={`${pomodoroCount % settings.longBreakInterval} of ${settings.longBreakInterval} pomodoros completed`}>
        {dots}
      </div>

      {/* Circular timer */}
      <CircularProgress progress={progress} sessionColor={color} size={260} strokeWidth={10}>
        <div
          className="timer-digits"
          role="timer"
          aria-live="polite"
          aria-label={`Time remaining: ${timeStr}`}
          style={{ color }}
        >
          {timeStr}
        </div>
        <div className="timer-state-hint">
          {timerState === 'paused' ? 'Paused' : timerState === 'idle' ? 'Ready' : ''}
        </div>
      </CircularProgress>

      {/* Controls */}
      <div className="timer-controls">
        <button
          className="btn btn--primary"
          style={{ '--btn-color': color } as React.CSSProperties}
          onClick={handleStartPause}
          aria-label={startPauseAriaLabel}
        >
          {timerState === 'running' ? (
            <span>⏸ {startPauseLabel}</span>
          ) : timerState === 'paused' ? (
            <span>▶ {startPauseLabel}</span>
          ) : (
            <span>▶ {startPauseLabel}</span>
          )}
        </button>

        <button
          className={`btn btn--secondary ${resetConfirm ? 'btn--confirm' : ''}`}
          onClick={handleResetClick}
          aria-label={resetConfirm ? 'Click again to confirm reset' : 'Reset timer'}
          disabled={timerState === 'idle'}
        >
          {resetConfirm ? '⚠ Confirm Reset?' : '↺ Reset'}
        </button>
      </div>
    </section>
  );
}
