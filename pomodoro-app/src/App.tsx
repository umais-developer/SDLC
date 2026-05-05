import { useCallback, useEffect, useRef, useState } from 'react';
import { DistractionLog } from './components/DistractionLog';
import { HeatMap } from './components/HeatMap';
import { LongBreakModal } from './components/LongBreakModal';
import { NotificationBanner } from './components/NotificationBanner';
import { SettingsPanel } from './components/SettingsPanel';
import { TimerDisplay } from './components/TimerDisplay';
import { useHeatMapData } from './hooks/useHeatMapData';
import { useTimer } from './hooks/useTimer';
import { NotificationService } from './services/NotificationService';
import {
  DEFAULT_SETTINGS,
  StorageService,
  getTodayDateString,
  isStorageAvailable,
} from './services/StorageService';
import type { PomodoroSettings, SessionType } from './types';
import './index.css';

export default function App() {
  // ── Settings ─────────────────────────────────────────────────────────────────
  const [settings, setSettings] = useState<PomodoroSettings>(() =>
    StorageService.loadSettings(),
  );

  // ── Session state ─────────────────────────────────────────────────────────────
  const [sessionType, setSessionType] = useState<SessionType>('work');
  const [pomodoroCount, setPomodoroCount] = useState(0);
  const [totalDuration, setTotalDuration] = useState(
    () => DEFAULT_SETTINGS.workDuration * 60 * 1000,
  );

  // ── UI state ──────────────────────────────────────────────────────────────────
  const [showSettings, setShowSettings] = useState(false);
  const [showLongBreakModal, setShowLongBreakModal] = useState(false);
  const [showNotifBanner, setShowNotifBanner] = useState(false);
  const [notifPermission, setNotifPermission] = useState<NotificationPermission>(() =>
    NotificationService.getPermission(),
  );
  const [storageAvailable] = useState(() => isStorageAvailable());

  // Refs to avoid stale closures in timer onComplete callback
  const sessionTypeRef = useRef(sessionType);
  const settingsRef = useRef(settings);
  const pomodoroCountRef = useRef(pomodoroCount);
  useEffect(() => {
    sessionTypeRef.current = sessionType;
  });
  useEffect(() => {
    settingsRef.current = settings;
  });
  useEffect(() => {
    pomodoroCountRef.current = pomodoroCount;
  });

  // ── Heat map ──────────────────────────────────────────────────────────────────
  const { grid, totalToday, refresh: refreshHeatMap, error: heatMapError } = useHeatMapData();

  // ── Notification banner on mount ──────────────────────────────────────────────
  useEffect(() => {
    const permission = NotificationService.getPermission();
    if (permission === 'default' && !StorageService.isNotificationBannerShown()) {
      setShowNotifBanner(true);
    }
  }, []);

  // ── Timer ref (forward-declare so handleTimerComplete can reference it) ───────
  const timerRef = useRef<ReturnType<typeof useTimer> | null>(null);

  // ── Timer completion handler ──────────────────────────────────────────────────
  const handleTimerComplete = useCallback(() => {
    const type = sessionTypeRef.current;
    const s = settingsRef.current;
    const count = pomodoroCountRef.current;
    const t = timerRef.current!;

    if (type === 'work') {
      const today = getTodayDateString();
      StorageService.incrementSessionCount(today);
      refreshHeatMap();

      NotificationService.playWorkEndTone();
      NotificationService.notify('Work session complete! 🍅', 'Great focus! Time to take a break.');

      const newCount = count + 1;
      setPomodoroCount(newCount);

      if (newCount >= s.longBreakInterval) {
        setShowLongBreakModal(true);
      } else {
        const dur = s.shortBreakDuration * 60 * 1000;
        setSessionType('shortBreak');
        setTotalDuration(dur);
        t.start(dur);
      }
    } else {
      NotificationService.playBreakEndTone();
      NotificationService.notify("Break's over! ☕", 'Time to focus again.');
      const dur = settingsRef.current.workDuration * 60 * 1000;
      setSessionType('work');
      setTotalDuration(dur);
      t.start(dur);
    }
  }, [refreshHeatMap]);

  const timer = useTimer(handleTimerComplete);
  timerRef.current = timer;

  // ── Controls ───────────────────────────────────────────────────────────────────
  const handleStart = useCallback(() => {
    NotificationService.resumeAudioContext();
    const dur = settingsRef.current.workDuration * 60 * 1000;
    setTotalDuration(dur);
    setSessionType('work');
    timer.start(dur);
  }, [timer]);

  const handleReset = useCallback(() => {
    const dur = settingsRef.current.workDuration * 60 * 1000;
    timer.reset(dur);
    setTotalDuration(dur);
    setSessionType('work');
  }, [timer]);

  // ── Long break modal ────────────────────────────────────────────────────────
  const handleStartLongBreak = useCallback(() => {
    setShowLongBreakModal(false);
    setPomodoroCount(0);
    setSessionType('longBreak');
    const dur = settingsRef.current.longBreakDuration * 60 * 1000;
    setTotalDuration(dur);
    timer.start(dur);
  }, [timer]);

  const handleSkipLongBreak = useCallback(() => {
    setShowLongBreakModal(false);
    setPomodoroCount(0);
    setSessionType('shortBreak');
    const dur = settingsRef.current.shortBreakDuration * 60 * 1000;
    setTotalDuration(dur);
    timer.start(dur);
  }, [timer]);

  // ── Settings save ──────────────────────────────────────────────────────────
  const handleSaveSettings = useCallback(
    (newSettings: PomodoroSettings) => {
      setSettings(newSettings);
      StorageService.saveSettings(newSettings);
      if (timer.state === 'idle') {
        const dur = newSettings.workDuration * 60 * 1000;
        setTotalDuration(dur);
        timer.reset(dur);
      }
    },
    [timer],
  );

  // ── Notification banner ────────────────────────────────────────────────────
  const handleNotifBannerDismiss = useCallback((granted: boolean) => {
    setShowNotifBanner(false);
    setNotifPermission(granted ? 'granted' : NotificationService.getPermission());
  }, []);

  // ── Keyboard shortcuts ──────────────────────────────────────────────────────
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement ||
        showSettings ||
        showLongBreakModal
      )
        return;
      if (e.code === 'Space') {
        e.preventDefault();
        if (timer.state === 'idle') handleStart();
        else if (timer.state === 'running') timer.pause();
        else timer.resume();
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [timer, handleStart, showSettings, showLongBreakModal]);

  return (
    <div className="app">
      {!storageAvailable && (
        <div className="storage-warning" role="alert">
          History won't be saved in private mode.
        </div>
      )}

      {showNotifBanner && <NotificationBanner onDismiss={handleNotifBannerDismiss} />}

      <header className="app-header">
        <div className="app-logo">
          <span aria-hidden="true">🍅</span>
          <span className="app-name">FocusFlow</span>
        </div>
        <div className="header-right">
          {notifPermission === 'denied' && (
            <span
              className="notif-status-chip"
              title="To enable, update notification settings in your browser"
              aria-label="Notifications off — audio only"
            >
              🔕 Audio only
            </span>
          )}
          <button
            className="icon-btn"
            onClick={() => setShowSettings(true)}
            aria-label="Open settings"
            title="Settings"
          >
            ⚙
          </button>
        </div>
      </header>

      <main className="app-main">
        <TimerDisplay
          remaining={timer.remaining}
          totalDuration={totalDuration}
          timerState={timer.state}
          sessionType={sessionType}
          pomodoroCount={pomodoroCount}
          settings={settings}
          onStart={handleStart}
          onPause={timer.pause}
          onResume={timer.resume}
          onReset={handleReset}
          onOpenSettings={() => setShowSettings(true)}
        />

        <HeatMap grid={grid} totalToday={totalToday} error={heatMapError} />

        <DistractionLog sessionType={sessionType} pomodoroCount={pomodoroCount} />
      </main>

      {showLongBreakModal && (
        <LongBreakModal
          longBreakMinutes={settings.longBreakDuration}
          onStartLongBreak={handleStartLongBreak}
          onSkip={handleSkipLongBreak}
        />
      )}

      {showSettings && (
        <SettingsPanel
          settings={settings}
          isTimerRunning={timer.state === 'running'}
          onSave={handleSaveSettings}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  );
}


