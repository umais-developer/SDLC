export interface PomodoroSettings {
  workDuration: number;
  shortBreakDuration: number;
  longBreakDuration: number;
  longBreakInterval: number;
}

export interface DistractionEntry {
  id: string;
  sessionDate: string;
  sessionIndex: number;
  text: string;
  timestamp: string;
}

export type SessionHistory = Record<string, number>;

export type SessionType = 'work' | 'shortBreak' | 'longBreak';

export type TimerState = 'idle' | 'running' | 'paused';

export interface HeatMapCell {
  date: string;
  count: number;
  isToday: boolean;
  label: string;
}

export type HeatMapGrid = HeatMapCell[][];
