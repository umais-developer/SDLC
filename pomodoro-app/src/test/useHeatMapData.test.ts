import { describe, it, expect } from 'vitest';
import { buildGrid, getDateString, TOTAL_DAYS } from '../hooks/useHeatMapData';

describe('useHeatMapData — buildGrid', () => {
  it('produces exactly 12 columns and 7 rows', () => {
    const grid = buildGrid({}, new Date('2026-05-05'));
    expect(grid).toHaveLength(7); // rows (days of week)
    expect(grid[0]).toHaveLength(12); // 12 weeks
  });

  it('total cells equals TOTAL_DAYS (84)', () => {
    const grid = buildGrid({}, new Date('2026-05-05'));
    const total = grid.reduce((sum, row) => sum + row.length, 0);
    expect(total).toBe(TOTAL_DAYS);
  });

  it('marks today as isToday=true', () => {
    const today = new Date('2026-05-05');
    const grid = buildGrid({}, today);
    const todayStr = getDateString(today);
    const todayCells = grid.flat().filter((c) => c.isToday);
    expect(todayCells).toHaveLength(1);
    expect(todayCells[0].date).toBe(todayStr);
  });

  it('correctly attributes session count to the right date', () => {
    const today = new Date('2026-05-05');
    const todayStr = getDateString(today);
    const history = { [todayStr]: 4 };
    const grid = buildGrid(history, today);
    const todayCell = grid.flat().find((c) => c.isToday)!;
    expect(todayCell.count).toBe(4);
  });

  it('midnight boundary: 23:58 session belongs to that day', () => {
    // Simulate a date just before midnight
    const date = new Date('2026-05-04T23:58:00');
    const dateStr = getDateString(date);
    expect(dateStr).toBe('2026-05-04');
  });

  it('midnight boundary: 00:02 session belongs to next day', () => {
    const date = new Date('2026-05-05T00:02:00');
    const dateStr = getDateString(date);
    expect(dateStr).toBe('2026-05-05');
  });

  it('sessions for unknown dates do not appear in today cell', () => {
    const today = new Date('2026-05-05');
    const history = { '2020-01-01': 99 }; // outside the 12-week window
    const grid = buildGrid(history, today);
    const todayCell = grid.flat().find((c) => c.isToday)!;
    expect(todayCell.count).toBe(0);
  });

  it('aria label includes count in correct singular/plural form', () => {
    const today = new Date('2026-05-05');
    const todayStr = getDateString(today);
    const grid1 = buildGrid({ [todayStr]: 1 }, today);
    const todayCell1 = grid1.flat().find((c) => c.isToday)!;
    expect(todayCell1.label).toContain('1 session');
    expect(todayCell1.label).not.toContain('sessions');

    const grid2 = buildGrid({ [todayStr]: 3 }, today);
    const todayCell2 = grid2.flat().find((c) => c.isToday)!;
    expect(todayCell2.label).toContain('3 sessions');
  });
});

describe('getDateString', () => {
  it('formats date as YYYY-MM-DD', () => {
    expect(getDateString(new Date(2026, 4, 5))).toBe('2026-05-05'); // Month is 0-indexed
    expect(getDateString(new Date(2026, 0, 1))).toBe('2026-01-01');
    expect(getDateString(new Date(2026, 11, 31))).toBe('2026-12-31');
  });
});
