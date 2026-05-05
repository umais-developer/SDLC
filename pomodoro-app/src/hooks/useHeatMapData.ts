import { useCallback, useEffect, useState } from 'react';
import { StorageService } from '../services/StorageService';
import type { HeatMapGrid, SessionHistory } from '../types';

const WEEKS = 12;
const DAYS_PER_WEEK = 7;
const TOTAL_DAYS = WEEKS * DAYS_PER_WEEK; // 84

function getDateString(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}

function formatLabel(dateStr: string): string {
  const [y, m, d] = dateStr.split('-').map(Number);
  const date = new Date(y, m - 1, d);
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  });
}

function buildGrid(history: SessionHistory, today: Date): HeatMapGrid {
  const todayStr = getDateString(today);
  // Compute the Sunday of the week containing today
  const dayOfWeek = today.getDay(); // 0=Sun
  const startDate = new Date(today);
  startDate.setDate(today.getDate() - dayOfWeek - (WEEKS - 1) * 7);

  const grid: HeatMapGrid = Array.from({ length: DAYS_PER_WEEK }, () => []);

  for (let col = 0; col < WEEKS; col++) {
    for (let row = 0; row < DAYS_PER_WEEK; row++) {
      const cellDate = new Date(startDate);
      cellDate.setDate(startDate.getDate() + col * 7 + row);
      const dateStr = getDateString(cellDate);
      const count = history[dateStr] ?? 0;
      const label = formatLabel(dateStr);
      grid[row].push({
        date: dateStr,
        count,
        isToday: dateStr === todayStr,
        label: `${label}: ${count} session${count !== 1 ? 's' : ''}`,
      });
    }
  }

  return grid;
}

interface UseHeatMapDataReturn {
  grid: HeatMapGrid;
  totalToday: number;
  refresh: () => void;
  error: boolean;
}

export function useHeatMapData(): UseHeatMapDataReturn {
  const [history, setHistory] = useState<SessionHistory>({});
  const [error, setError] = useState(false);

  const refresh = useCallback(() => {
    try {
      setHistory(StorageService.getSessionHistory());
      setError(false);
    } catch {
      setError(true);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const today = new Date();
  const grid = buildGrid(history, today);
  const todayStr = getDateString(today);
  const totalToday = history[todayStr] ?? 0;

  return { grid, totalToday, refresh, error };
}

/** Exposed for testing */
export { buildGrid, getDateString, TOTAL_DAYS };
