import { useCallback, useRef, useState } from 'react';
import type { DistractionEntry, SessionType } from '../types';
import { StorageService, getTodayDateString } from '../services/StorageService';

interface DistractionLogProps {
  sessionType: SessionType;
  pomodoroCount: number;
}

export function DistractionLog({ sessionType, pomodoroCount }: DistractionLogProps) {
  const [entries, setEntries] = useState<DistractionEntry[]>(() =>
    StorageService.getDistractions(),
  );
  const [inputVisible, setInputVisible] = useState(false);
  const [inputText, setInputText] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const isWorkSession = sessionType === 'work';

  const showInput = useCallback(() => {
    setInputVisible(true);
    setTimeout(() => inputRef.current?.focus(), 50);
  }, []);

  const hideInput = useCallback(() => {
    setInputVisible(false);
    setInputText('');
  }, []);

  const saveEntry = useCallback(() => {
    const text = inputText.trim();
    if (!text) return;
    const entry: DistractionEntry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      sessionDate: getTodayDateString(),
      sessionIndex: pomodoroCount,
      text,
      timestamp: new Date().toISOString(),
    };
    StorageService.appendDistractionEntry(entry);
    setEntries(StorageService.getDistractions());
    setInputText('');
    setInputVisible(false);
  }, [inputText, pomodoroCount]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') saveEntry();
      if (e.key === 'Escape') hideInput();
    },
    [saveEntry, hideInput],
  );

  // Entries for today, newest first
  const todayStr = getTodayDateString();
  const todayEntries = entries
    .filter((e) => e.sessionDate === todayStr)
    .slice()
    .reverse();

  const formatTime = (iso: string) => {
    try {
      return new Date(iso).toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
      });
    } catch {
      return iso;
    }
  };

  return (
    <section className="distraction-section" aria-label="Distraction log">
      <div className="distraction-header">
        <h2 className="section-title">Distraction Log</h2>
        <button
          className="btn btn--ghost"
          onClick={showInput}
          disabled={!isWorkSession}
          aria-label={
            isWorkSession
              ? 'Log a distraction'
              : 'Distraction log is available during work sessions only'
          }
          title={
            isWorkSession ? undefined : 'Distraction log is available during work sessions only'
          }
        >
          + Log Distraction
        </button>
      </div>

      {inputVisible && (
        <div className="distraction-input-row" role="group" aria-label="New distraction entry">
          <input
            ref={inputRef}
            className="distraction-input"
            type="text"
            placeholder="What distracted you?"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            maxLength={200}
            aria-label="Distraction note"
          />
          <button className="btn btn--small btn--primary-ghost" onClick={saveEntry} aria-label="Add distraction entry">
            Add
          </button>
          <button className="btn btn--small btn--ghost" onClick={hideInput} aria-label="Cancel">
            Cancel
          </button>
        </div>
      )}

      {todayEntries.length === 0 && !inputVisible ? (
        <p className="distraction-empty">No distractions logged today. Stay focused!</p>
      ) : (
        <ul
          className="distraction-list"
          aria-live="polite"
          aria-label="Today's distraction entries"
        >
          {todayEntries.map((entry) => (
            <li key={entry.id} className="distraction-entry">
              <span className="distraction-time">{formatTime(entry.timestamp)}</span>
              <span className="distraction-text">{entry.text}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
