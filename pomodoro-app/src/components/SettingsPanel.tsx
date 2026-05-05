import { useCallback, useEffect, useState } from 'react';
import type { PomodoroSettings } from '../types';

interface SettingsPanelProps {
  settings: PomodoroSettings;
  isTimerRunning: boolean;
  onSave: (settings: PomodoroSettings) => void;
  onClose: () => void;
}

interface FormValues {
  workDuration: string;
  shortBreakDuration: string;
  longBreakDuration: string;
  longBreakInterval: string;
}

interface FormErrors {
  workDuration?: string;
  shortBreakDuration?: string;
  longBreakDuration?: string;
  longBreakInterval?: string;
}

const DURATION_RANGE = { min: 1, max: 60 };
const INTERVAL_RANGE = { min: 1, max: 10 };
const DURATION_ERROR = 'Must be between 1 and 60 minutes';
const INTERVAL_ERROR = 'Must be between 1 and 10';

function validateDuration(val: string, range = DURATION_RANGE): string | undefined {
  const n = parseInt(val, 10);
  if (isNaN(n) || n < range.min || n > range.max) return DURATION_ERROR;
  return undefined;
}

export function SettingsPanel({ settings, isTimerRunning, onSave, onClose }: SettingsPanelProps) {
  const [values, setValues] = useState<FormValues>({
    workDuration: String(settings.workDuration),
    shortBreakDuration: String(settings.shortBreakDuration),
    longBreakDuration: String(settings.longBreakDuration),
    longBreakInterval: String(settings.longBreakInterval),
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [saved, setSaved] = useState(false);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  const handleChange = useCallback((field: keyof FormValues, val: string) => {
    setValues((prev) => ({ ...prev, [field]: val }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
    setSaved(false);
  }, []);

  const validate = (): boolean => {
    const errs: FormErrors = {
      workDuration: validateDuration(values.workDuration),
      shortBreakDuration: validateDuration(values.shortBreakDuration),
      longBreakDuration: validateDuration(values.longBreakDuration),
      longBreakInterval: validateDuration(values.longBreakInterval, INTERVAL_RANGE)
        ? INTERVAL_ERROR
        : undefined,
    };
    setErrors(errs);
    return !Object.values(errs).some(Boolean);
  };

  const handleSave = useCallback(() => {
    if (!validate()) return;
    onSave({
      workDuration: parseInt(values.workDuration, 10),
      shortBreakDuration: parseInt(values.shortBreakDuration, 10),
      longBreakDuration: parseInt(values.longBreakDuration, 10),
      longBreakInterval: parseInt(values.longBreakInterval, 10),
    });
    setSaved(true);
    setTimeout(() => onClose(), 800);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [values, onSave, onClose]);

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Settings"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="modal-panel settings-panel">
        <div className="modal-header">
          <h2 className="modal-title">Settings</h2>
          <button className="modal-close" onClick={onClose} aria-label="Close settings">
            ✕
          </button>
        </div>

        {isTimerRunning && (
          <p className="settings-warning" role="status">
            ℹ Changes will take effect after the current session.
          </p>
        )}

        <div className="settings-form">
          <SettingsField
            label="Work Duration (min)"
            id="work-duration"
            value={values.workDuration}
            error={errors.workDuration}
            onChange={(v) => handleChange('workDuration', v)}
          />
          <SettingsField
            label="Short Break Duration (min)"
            id="short-break-duration"
            value={values.shortBreakDuration}
            error={errors.shortBreakDuration}
            onChange={(v) => handleChange('shortBreakDuration', v)}
          />
          <SettingsField
            label="Long Break Duration (min)"
            id="long-break-duration"
            value={values.longBreakDuration}
            error={errors.longBreakDuration}
            onChange={(v) => handleChange('longBreakDuration', v)}
          />
          <SettingsField
            label="Long Break Every (sessions)"
            id="long-break-interval"
            value={values.longBreakInterval}
            error={errors.longBreakInterval}
            onChange={(v) => handleChange('longBreakInterval', v)}
            min={1}
            max={10}
          />
        </div>

        <div className="modal-footer">
          {saved && (
            <span className="settings-saved-msg" role="status" aria-live="polite">
              ✓ Settings saved
            </span>
          )}
          <button className="btn btn--ghost" onClick={onClose}>
            Cancel
          </button>
          <button className="btn btn--primary" onClick={handleSave}>
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

interface SettingsFieldProps {
  label: string;
  id: string;
  value: string;
  error?: string;
  onChange: (val: string) => void;
  min?: number;
  max?: number;
}

function SettingsField({ label, id, value, error, onChange, min = 1, max = 60 }: SettingsFieldProps) {
  return (
    <div className="settings-field">
      <label className="settings-label" htmlFor={id}>
        {label}
      </label>
      <input
        id={id}
        className={`settings-input ${error ? 'settings-input--error' : ''}`}
        type="number"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        min={min}
        max={max}
        aria-describedby={error ? `${id}-error` : undefined}
        aria-invalid={!!error}
      />
      {error && (
        <span id={`${id}-error`} className="settings-error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
