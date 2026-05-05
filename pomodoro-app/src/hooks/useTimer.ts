import { useCallback, useEffect, useRef, useState } from 'react';
import type { TimerState } from '../types';

interface UseTimerReturn {
  remaining: number; // ms
  state: TimerState;
  start: (durationMs: number) => void;
  pause: () => void;
  resume: () => void;
  reset: (durationMs: number) => void;
}

/**
 * Drift-corrected countdown timer using Date.now() delta + requestAnimationFrame.
 * Even if rAF is throttled in background tabs, remaining is always computed from
 * the absolute endTime so accuracy is maintained to within one frame interval.
 */
export function useTimer(onComplete: () => void): UseTimerReturn {
  const [remaining, setRemaining] = useState(25 * 60 * 1000);
  const [timerState, setTimerState] = useState<TimerState>('idle');

  const endTimeRef = useRef<number | null>(null);
  const rafRef = useRef<number | null>(null);
  const onCompleteRef = useRef(onComplete);
  // Always keep ref current so stale closures are never an issue
  useEffect(() => {
    onCompleteRef.current = onComplete;
  });

  const tick = useCallback(() => {
    if (endTimeRef.current === null) return;
    const now = Date.now();
    const rem = Math.max(0, endTimeRef.current - now);
    setRemaining(rem);
    if (rem > 0) {
      rafRef.current = requestAnimationFrame(tick);
    } else {
      setTimerState('idle');
      endTimeRef.current = null;
      onCompleteRef.current();
    }
  }, []);

  const start = useCallback(
    (durationMs: number) => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      endTimeRef.current = Date.now() + durationMs;
      setRemaining(durationMs);
      setTimerState('running');
      rafRef.current = requestAnimationFrame(tick);
    },
    [tick],
  );

  const pause = useCallback(() => {
    if (rafRef.current !== null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    setTimerState('paused');
  }, []);

  const resume = useCallback(() => {
    setRemaining((prev) => {
      endTimeRef.current = Date.now() + prev;
      return prev;
    });
    setTimerState('running');
    rafRef.current = requestAnimationFrame(tick);
  }, [tick]);

  const reset = useCallback((durationMs: number) => {
    if (rafRef.current !== null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    endTimeRef.current = null;
    setRemaining(durationMs);
    setTimerState('idle');
  }, []);

  useEffect(() => {
    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return { remaining, state: timerState, start, pause, resume, reset };
}
