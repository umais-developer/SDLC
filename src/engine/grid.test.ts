/**
 * Unit tests for grid utilities
 */

import { describe, it, expect } from 'vitest';
import {
  createGrid,
  toggleCell,
  clearGrid,
  copyGrid,
  countLiveCells,
  serializeGrid,
  deserializeGrid,
} from '../engine/grid';

describe('Grid utilities', () => {
  describe('createGrid', () => {
    it('should create a grid with correct dimensions', () => {
      const grid = createGrid(50, 50);
      expect(grid.width).toBe(50);
      expect(grid.height).toBe(50);
      expect(grid.cells.length).toBe(50);
      expect(grid.cells[0].length).toBe(50);
    });

    it('should initialize all cells as dead', () => {
      const grid = createGrid(5, 5);
      for (let y = 0; y < grid.height; y++) {
        for (let x = 0; x < grid.width; x++) {
          expect(grid.cells[y][x]).toBe(false);
        }
      }
    });

    it('should initialize counters to zero', () => {
      const grid = createGrid(10, 10);
      expect(grid.generation).toBe(0);
      expect(grid.liveCellCount).toBe(0);
    });

    it('should set boundary mode to wrap', () => {
      const grid = createGrid(10, 10);
      expect(grid.boundaryMode).toBe('wrap');
    });
  });

  describe('toggleCell', () => {
    it('should toggle a dead cell to alive', () => {
      let grid = createGrid(5, 5);
      grid = toggleCell(grid, 2, 2);

      expect(grid.cells[2][2]).toBe(true);
      expect(grid.liveCellCount).toBe(1);
    });

    it('should toggle an alive cell back to dead', () => {
      let grid = createGrid(5, 5);
      grid = toggleCell(grid, 2, 2);
      grid = toggleCell(grid, 2, 2);

      expect(grid.cells[2][2]).toBe(false);
      expect(grid.liveCellCount).toBe(0);
    });

    it('should only modify target cell', () => {
      let grid = createGrid(5, 5);
      grid = toggleCell(grid, 2, 2);

      expect(grid.cells[2][2]).toBe(true);
      expect(grid.cells[2][1]).toBe(false);
      expect(grid.cells[1][2]).toBe(false);
    });

    it('should not modify out-of-bounds cells', () => {
      let grid = createGrid(5, 5);
      grid = toggleCell(grid, -1, 2);
      grid = toggleCell(grid, 10, 2);
      grid = toggleCell(grid, 2, -1);
      grid = toggleCell(grid, 2, 10);

      expect(grid.liveCellCount).toBe(0);
    });

    it('should correctly update liveCellCount for multiple toggles', () => {
      let grid = createGrid(5, 5);

      grid = toggleCell(grid, 0, 0);
      expect(grid.liveCellCount).toBe(1);

      grid = toggleCell(grid, 1, 1);
      expect(grid.liveCellCount).toBe(2);

      grid = toggleCell(grid, 0, 0);
      expect(grid.liveCellCount).toBe(1);
    });

    it('should not go below zero for liveCellCount', () => {
      let grid = createGrid(5, 5);
      grid = toggleCell(grid, 2, 2);
      grid = toggleCell(grid, 2, 2);

      expect(grid.liveCellCount).toBeGreaterThanOrEqual(0);
    });
  });

  describe('clearGrid', () => {
    it('should set all cells to dead', () => {
      let grid = createGrid(5, 5);
      grid = toggleCell(grid, 0, 0);
      grid = toggleCell(grid, 1, 1);
      grid = toggleCell(grid, 2, 2);

      grid = clearGrid(grid);

      for (let y = 0; y < grid.height; y++) {
        for (let x = 0; x < grid.width; x++) {
          expect(grid.cells[y][x]).toBe(false);
        }
      }
    });

    it('should reset generation to 0', () => {
      let grid = createGrid(5, 5);
      grid.generation = 10;

      grid = clearGrid(grid);
      expect(grid.generation).toBe(0);
    });

    it('should reset liveCellCount to 0', () => {
      let grid = createGrid(5, 5);
      grid = toggleCell(grid, 0, 0);
      grid = toggleCell(grid, 1, 1);

      grid = clearGrid(grid);
      expect(grid.liveCellCount).toBe(0);
    });
  });

  describe('copyGrid', () => {
    it('should create an independent copy', () => {
      let grid1 = createGrid(5, 5);
      grid1 = toggleCell(grid1, 2, 2);

      const grid2 = copyGrid(grid1);
      grid2.cells[2][2] = false;

      expect(grid1.cells[2][2]).toBe(true);
      expect(grid2.cells[2][2]).toBe(false);
    });

    it('should preserve all grid properties', () => {
      let grid = createGrid(10, 10);
      grid.generation = 5;
      grid = toggleCell(grid, 3, 3);
      grid = toggleCell(grid, 4, 4);

      const copy = copyGrid(grid);

      expect(copy.width).toBe(10);
      expect(copy.height).toBe(10);
      expect(copy.generation).toBe(5);
      expect(copy.liveCellCount).toBe(2);
      expect(copy.cells[3][3]).toBe(true);
      expect(copy.cells[4][4]).toBe(true);
    });
  });

  describe('countLiveCells', () => {
    it('should count zero cells in empty grid', () => {
      const grid = createGrid(5, 5);
      const count = countLiveCells(grid.cells);
      expect(count).toBe(0);
    });

    it('should count all alive cells', () => {
      let grid = createGrid(5, 5);
      grid = toggleCell(grid, 0, 0);
      grid = toggleCell(grid, 1, 1);
      grid = toggleCell(grid, 2, 2);
      grid = toggleCell(grid, 3, 3);

      const count = countLiveCells(grid.cells);
      expect(count).toBe(4);
    });

    it('should match liveCellCount after toggling', () => {
      let grid = createGrid(10, 10);

      for (let i = 0; i < 7; i++) {
        grid = toggleCell(grid, i, i);
      }

      const count = countLiveCells(grid.cells);
      expect(count).toBe(grid.liveCellCount);
    });
  });

  describe('serializeGrid and deserializeGrid', () => {
    it('should serialize grid to JSON', () => {
      let grid = createGrid(5, 5);
      grid = toggleCell(grid, 2, 2);
      grid.generation = 5;

      const json = serializeGrid(grid);
      expect(typeof json).toBe('string');
      expect(json).toContain('"generation":5');
    });

    it('should deserialize back to equivalent grid', () => {
      let original = createGrid(5, 5);
      original = toggleCell(original, 1, 1);
      original = toggleCell(original, 3, 3);
      original.generation = 3;

      const json = serializeGrid(original);
      const restored = deserializeGrid(json);

      expect(restored.width).toBe(original.width);
      expect(restored.height).toBe(original.height);
      expect(restored.generation).toBe(original.generation);
      expect(restored.liveCellCount).toBe(original.liveCellCount);
      expect(restored.cells[1][1]).toBe(true);
      expect(restored.cells[3][3]).toBe(true);
    });

    it('should throw on invalid JSON', () => {
      expect(() => deserializeGrid('invalid json {')).toThrow();
    });

    it('should be symmetric (serialize -> deserialize -> serialize)', () => {
      let grid = createGrid(8, 8);
      grid = toggleCell(grid, 2, 3);
      grid = toggleCell(grid, 5, 6);
      grid.generation = 10;

      const json1 = serializeGrid(grid);
      const restored = deserializeGrid(json1);
      const json2 = serializeGrid(restored);

      expect(json1).toBe(json2);
    });
  });
});
