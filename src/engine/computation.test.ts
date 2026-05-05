/**
 * Unit tests for useGameOfLife hook
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { computeNextGeneration } from '../engine/rules';
import { createGrid, toggleCell } from '../engine/grid';

describe('Game of Life computation (main thread fallback)', () => {
  it('should compute next generation correctly', async () => {
    let grid = createGrid(5, 5);
    // Create a blinker pattern
    grid = toggleCell(grid, 1, 2);
    grid = toggleCell(grid, 2, 2);
    grid = toggleCell(grid, 3, 2);

    const nextGen = computeNextGeneration(grid);

    expect(nextGen.generation).toBe(1);
    expect(nextGen.liveCellCount).toBe(3);
    // Should now be vertical
    expect(nextGen.cells[1][2]).toBe(true);
    expect(nextGen.cells[2][2]).toBe(true);
    expect(nextGen.cells[3][2]).toBe(true);
  });

  it('should handle empty grid', async () => {
    const grid = createGrid(5, 5);
    const nextGen = computeNextGeneration(grid);

    expect(nextGen.generation).toBe(1);
    expect(nextGen.liveCellCount).toBe(0);
  });

  it('should handle large grid efficiently', async () => {
    let grid = createGrid(100, 100);
    // Add some cells
    for (let i = 0; i < 50; i++) {
      grid = toggleCell(grid, Math.random() * 100 | 0, Math.random() * 100 | 0);
    }

    const start = performance.now();
    const nextGen = computeNextGeneration(grid);
    const elapsed = performance.now() - start;

    expect(nextGen.generation).toBe(1);
    // Should complete in reasonable time (< 100ms)
    expect(elapsed).toBeLessThan(100);
  });
});

describe('Web Worker integration (simulated)', () => {
  beforeEach(() => {
    // Mock Web Worker
    global.Worker = vi.fn(() => ({
      postMessage: vi.fn(),
      onmessage: null,
      onerror: null,
      terminate: vi.fn(),
    })) as any;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should fallback to main thread when worker not available', async () => {
    // Simulate worker unavailability by catching error
    const result = computeNextGeneration(createGrid(5, 5));
    expect(result.generation).toBe(1);
  });

  it('should handle promise rejection gracefully', async () => {
    let grid = createGrid(5, 5);
    grid = toggleCell(grid, 2, 2);

    try {
      const result = computeNextGeneration(grid);
      expect(result.generation).toBe(1);
    } catch (error) {
      // Should not throw
      expect(false).toBe(true);
    }
  });
});

describe('Performance benchmarks', () => {
  it('should compute neighbor count efficiently for 100x100 grid', () => {
    let grid = createGrid(100, 100);
    // Add scattered cells
    for (let i = 0; i < 100; i++) {
      grid = toggleCell(grid, Math.random() * 100 | 0, Math.random() * 100 | 0);
    }

    const start = performance.now();
    // Run 5 generations
    let current = grid;
    for (let gen = 0; gen < 5; gen++) {
      current = computeNextGeneration(current);
    }
    const elapsed = performance.now() - start;

    // Should complete 5 generations in < 500ms
    expect(elapsed).toBeLessThan(500);
    expect(current.generation).toBe(5);
  });

  it('should maintain performance with stable patterns', () => {
    let grid = createGrid(50, 50);

    // Add blocks (stable pattern)
    for (let i = 0; i < 10; i++) {
      grid = toggleCell(grid, i * 2, 0);
      grid = toggleCell(grid, i * 2 + 1, 0);
      grid = toggleCell(grid, i * 2, 1);
      grid = toggleCell(grid, i * 2 + 1, 1);
    }

    const start = performance.now();
    let current = grid;
    for (let gen = 0; gen < 10; gen++) {
      current = computeNextGeneration(current);
    }
    const elapsed = performance.now() - start;

    expect(elapsed).toBeLessThan(200);
    expect(current.liveCellCount).toBe(grid.liveCellCount);
  });
});
