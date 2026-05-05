import { describe, it, expect, beforeEach } from 'vitest';
import {
  StorageService,
  getTodayDateString,
  isStorageAvailable,
} from '../services/StorageService';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock });

describe('StorageService', () => {
  beforeEach(() => {
    localStorageMock.clear();
  });

  describe('loadSettings / saveSettings', () => {
    it('returns defaults when no settings are stored', () => {
      const settings = StorageService.loadSettings();
      expect(settings.workDuration).toBe(25);
      expect(settings.shortBreakDuration).toBe(5);
      expect(settings.longBreakDuration).toBe(15);
      expect(settings.longBreakInterval).toBe(4);
    });

    it('returns saved settings after save', () => {
      StorageService.saveSettings({
        workDuration: 30,
        shortBreakDuration: 10,
        longBreakDuration: 20,
        longBreakInterval: 3,
      });
      const loaded = StorageService.loadSettings();
      expect(loaded.workDuration).toBe(30);
      expect(loaded.shortBreakDuration).toBe(10);
    });
  });

  describe('incrementSessionCount / getSessionHistory', () => {
    it('starts at 0 for a new day and increments correctly', () => {
      const date = '2026-05-05';
      expect(StorageService.getSessionHistory()[date]).toBeUndefined();
      StorageService.incrementSessionCount(date);
      expect(StorageService.getSessionHistory()[date]).toBe(1);
      StorageService.incrementSessionCount(date);
      expect(StorageService.getSessionHistory()[date]).toBe(2);
    });

    it('tracks separate days independently', () => {
      StorageService.incrementSessionCount('2026-05-05');
      StorageService.incrementSessionCount('2026-05-06');
      StorageService.incrementSessionCount('2026-05-06');
      const history = StorageService.getSessionHistory();
      expect(history['2026-05-05']).toBe(1);
      expect(history['2026-05-06']).toBe(2);
    });
  });

  describe('distraction log', () => {
    it('appends entries and retrieves them', () => {
      const entry = {
        id: 'test-1',
        sessionDate: '2026-05-05',
        sessionIndex: 0,
        text: 'Phone rang',
        timestamp: new Date().toISOString(),
      };
      StorageService.appendDistractionEntry(entry);
      const entries = StorageService.getDistractions();
      expect(entries).toHaveLength(1);
      expect(entries[0].text).toBe('Phone rang');
    });
  });

  describe('notification banner state', () => {
    it('returns false initially and true after marking shown', () => {
      expect(StorageService.isNotificationBannerShown()).toBe(false);
      StorageService.markNotificationBannerShown();
      expect(StorageService.isNotificationBannerShown()).toBe(true);
    });
  });
});

describe('getTodayDateString', () => {
  it('returns YYYY-MM-DD format in local time', () => {
    const result = getTodayDateString();
    expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});

describe('isStorageAvailable', () => {
  it('returns true when localStorage is available', () => {
    expect(isStorageAvailable()).toBe(true);
  });
});
