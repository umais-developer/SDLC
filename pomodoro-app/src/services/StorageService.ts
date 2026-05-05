import type { DistractionEntry, PomodoroSettings, SessionHistory } from '../types';

const STORAGE_KEYS = {
  SESSION_HISTORY: 'pomo_session_history',
  DISTRACTIONS: 'pomo_distractions',
  SETTINGS: 'pomo_settings',
  NOTIFICATION_BANNER: 'pomo_notif_banner_shown',
} as const;

export const DEFAULT_SETTINGS: PomodoroSettings = {
  workDuration: 25,
  shortBreakDuration: 5,
  longBreakDuration: 15,
  longBreakInterval: 4,
};

function safeRead<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (raw === null) return fallback;
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

function safeWrite(key: string, value: unknown): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // localStorage unavailable (private browsing or quota exceeded)
  }
}

export function isStorageAvailable(): boolean {
  try {
    const testKey = '__pomo_test__';
    localStorage.setItem(testKey, '1');
    localStorage.removeItem(testKey);
    return true;
  } catch {
    return false;
  }
}

export function getTodayDateString(): string {
  // Returns YYYY-MM-DD in local time
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

export const StorageService = {
  loadSettings(): PomodoroSettings {
    const saved = safeRead<Partial<PomodoroSettings>>(STORAGE_KEYS.SETTINGS, {});
    return { ...DEFAULT_SETTINGS, ...saved };
  },

  saveSettings(settings: PomodoroSettings): void {
    safeWrite(STORAGE_KEYS.SETTINGS, settings);
  },

  getSessionHistory(): SessionHistory {
    return safeRead<SessionHistory>(STORAGE_KEYS.SESSION_HISTORY, {});
  },

  incrementSessionCount(date: string): void {
    const history = StorageService.getSessionHistory();
    history[date] = (history[date] ?? 0) + 1;
    safeWrite(STORAGE_KEYS.SESSION_HISTORY, history);
  },

  getDistractions(): DistractionEntry[] {
    return safeRead<DistractionEntry[]>(STORAGE_KEYS.DISTRACTIONS, []);
  },

  appendDistractionEntry(entry: DistractionEntry): void {
    const entries = StorageService.getDistractions();
    entries.push(entry);
    safeWrite(STORAGE_KEYS.DISTRACTIONS, entries);
  },

  isNotificationBannerShown(): boolean {
    return safeRead<boolean>(STORAGE_KEYS.NOTIFICATION_BANNER, false);
  },

  markNotificationBannerShown(): void {
    safeWrite(STORAGE_KEYS.NOTIFICATION_BANNER, true);
  },
};
