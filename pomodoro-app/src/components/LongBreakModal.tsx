interface LongBreakModalProps {
  longBreakMinutes: number;
  onStartLongBreak: () => void;
  onSkip: () => void;
}

export function LongBreakModal({ longBreakMinutes, onStartLongBreak, onSkip }: LongBreakModalProps) {
  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Long break prompt"
    >
      <div className="modal-panel long-break-modal">
        <div className="long-break-icon" aria-hidden="true">🎉</div>
        <h2 className="modal-title">You've completed 4 Pomodoros!</h2>
        <p className="modal-body">
          Great work! You've earned a {longBreakMinutes}-minute long break. Ready to rest?
        </p>
        <div className="modal-footer modal-footer--centered">
          <button className="btn btn--primary btn--large" onClick={onStartLongBreak} autoFocus>
            Start Long Break ({longBreakMinutes} min)
          </button>
          <button className="btn btn--ghost" onClick={onSkip}>
            Skip — Short Break
          </button>
        </div>
      </div>
    </div>
  );
}
