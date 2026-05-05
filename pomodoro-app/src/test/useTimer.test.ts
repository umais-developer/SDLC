import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useTimer } from '../hooks/useTimer';

// Mock requestAnimationFrame and cancelAnimationFrame
let rafCallbacks: Map<number, FrameRequestCallback> = new Map();
let rafId = 0;

beforeEach(() => {
  rafCallbacks.clear();
  rafId = 0;

  vi.spyOn(globalThis, 'requestAnimationFrame').mockImplementation((cb: FrameRequestCallback) => {
    const id = ++rafId;
    rafCallbacks.set(id, cb);
    return id;
  });

  vi.spyOn(globalThis, 'cancelAnimationFrame').mockImplementation((id: number) => {
    rafCallbacks.delete(id);
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

function flushRaf(timestamp = Date.now()) {
  const callbacks = new Map(rafCallbacks);
  rafCallbacks.clear();
  callbacks.forEach((cb) => cb(timestamp));
}

describe('useTimer', () => {
  it('starts in idle state with correct initial remaining', () => {
    const onComplete = vi.fn();
    const { result } = renderHook(() => useTimer(onComplete));
    expect(result.current.state).toBe('idle');
    expect(result.current.remaining).toBeGreaterThan(0);
  });

  it('transitions to running when start() is called', () => {
    const onComplete = vi.fn();
    const { result } = renderHook(() => useTimer(onComplete));
    act(() => {
      result.current.start(5000);
    });
    expect(result.current.state).toBe('running');
  });

  it('transitions to paused when pause() is called', () => {
    const onComplete = vi.fn();
    const { result } = renderHook(() => useTimer(onComplete));
    act(() => {
      result.current.start(5000);
    });
    act(() => {
      result.current.pause();
    });
    expect(result.current.state).toBe('paused');
  });

  it('transitions back to running when resume() is called', () => {
    const onComplete = vi.fn();
    const { result } = renderHook(() => useTimer(onComplete));
    act(() => {
      result.current.start(5000);
      result.current.pause();
    });
    act(() => {
      result.current.resume();
    });
    expect(result.current.state).toBe('running');
  });

  it('resets to idle with specified duration', () => {
    const onComplete = vi.fn();
    const { result } = renderHook(() => useTimer(onComplete));
    act(() => {
      result.current.start(5000);
    });
    act(() => {
      result.current.reset(10000);
    });
    expect(result.current.state).toBe('idle');
    expect(result.current.remaining).toBe(10000);
  });

  it('calls onComplete when timer reaches zero', () => {
    const onComplete = vi.fn();
    const { result } = renderHook(() => useTimer(onComplete));

    // Mock Date.now to control time
    const startTime = 1000;
    let currentTime = startTime;
    vi.spyOn(Date, 'now').mockImplementation(() => currentTime);

    act(() => {
      result.current.start(100); // 100ms duration
    });

    // Advance past the end time
    currentTime = startTime + 200; // past 100ms duration

    act(() => {
      flushRaf(currentTime);
    });

    expect(onComplete).toHaveBeenCalledTimes(1);
    expect(result.current.state).toBe('idle');
    vi.restoreAllMocks();
  });

  it('remaining is computed from Date.now delta, not tick count', () => {
    const onComplete = vi.fn();
    const { result } = renderHook(() => useTimer(onComplete));
    const startTime = 10000;
    let currentTime = startTime;
    vi.spyOn(Date, 'now').mockImplementation(() => currentTime);

    act(() => {
      result.current.start(5000); // 5 second timer
    });

    // Simulate 2.5 seconds elapsed without many ticks
    currentTime = startTime + 2500;
    act(() => {
      flushRaf(currentTime);
    });

    // Remaining should be ~2500ms, not based on tick count
    expect(result.current.remaining).toBeLessThanOrEqual(2500);
    expect(result.current.remaining).toBeGreaterThanOrEqual(2400);
    vi.restoreAllMocks();
  });
});
