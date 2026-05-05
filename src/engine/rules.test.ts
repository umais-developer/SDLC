/**
 * Unit tests for Conway's Game of Life rules engine
 */

import { describe, it, expect } from 'vitest';
import { countNeighbors, computeNextGeneration, isAlive } from '../engine/rules';
import { createGrid, toggleCell } from '../engine/grid';

describe('countNeighbors', () => {
  it('should count neighbors for a center cell', () => {
    let grid = createGrid(5, 5);

    // Place cells around (2, 2)
    grid = toggleCell(grid, 1, 1); // top-left
    grid = toggleCell(grid, 2, 1); // top
    grid = toggleCell(grid, 3, 1); // top-right
    grid = toggleCell(grid, 3, 2); // right
    grid = toggleCell(grid, 3, 3); // bottom-right
    grid = toggleCell(grid, 2, 3); // bottom
    grid = toggleCell(grid, 1, 3); // bottom-left
    grid = toggleCell(grid, 1, 2); // left

    const neighbors = countNeighbors(grid, 2, 2);
    expect(neighbors).toBe(8);
  });

  it('should count 3 neighbors for a corner cell with wrapping', () => {
    let grid = createGrid(3, 3);

    // Place cells to wrap around corner (0, 0)
    grid = toggleCell(grid, 2, 2); // wraps to top-left neighbor
    grid = toggleCell(grid, 0, 2); // above wrapped
    grid = toggleCell(grid, 2, 0); // left of wrapped

    const neighbors = countNeighbors(grid, 0, 0);
    expect(neighbors).toBe(3);
  });

  it('should return 0 for isolated cell', () => {
    const grid = createGrid(5, 5);
    const neighbors = countNeighbors(grid, 2, 2);
    expect(neighbors).toBe(0);
  });

  it('should count only 3 neighbors for edge cell', () => {
    let grid = createGrid(5, 5);

    // Place neighbors for edge cell (0, 2)
    grid = toggleCell(grid, 1, 1);
    grid = toggleCell(grid, 1, 2);
    grid = toggleCell(grid, 1, 3);

    const neighbors = countNeighbors(grid, 0, 2);
    expect(neighbors).toBe(3);
  });
});

describe('isAlive', () => {
  it('should return true for alive cell', () => {
    let grid = createGrid(5, 5);
    grid = toggleCell(grid, 2, 2);

    expect(isAlive(grid, 2, 2)).toBe(true);
  });

  it('should return false for dead cell', () => {
    const grid = createGrid(5, 5);
    expect(isAlive(grid, 2, 2)).toBe(false);
  });

  it('should wrap for boundary cells', () => {
    let grid = createGrid(3, 3);
    grid = toggleCell(grid, 0, 0);

    expect(isAlive(grid, -1, -1)).toBe(true); // wraps to (2, 2)... no, wraps to (0, 0)
  });
});

describe('computeNextGeneration', () => {
  it('should make blinker oscillate (period 2)', () => {
    // Create a horizontal blinker
    let grid = createGrid(5, 5);
    grid = toggleCell(grid, 1, 2);
    grid = toggleCell(grid, 2, 2);
    grid = toggleCell(grid, 3, 2);

    expect(grid.cells[2][1]).toBe(true);
    expect(grid.cells[2][2]).toBe(true);
    expect(grid.cells[2][3]).toBe(true);
    expect(grid.liveCellCount).toBe(3);

    // Advance one generation
    const nextGen1 = computeNextGeneration(grid);
    expect(nextGen1.generation).toBe(1);
    expect(nextGen1.liveCellCount).toBe(3);
    // Should now be vertical
    expect(nextGen1.cells[1][2]).toBe(true);
    expect(nextGen1.cells[2][2]).toBe(true);
    expect(nextGen1.cells[3][2]).toBe(true);

    // Advance again
    const nextGen2 = computeNextGeneration(nextGen1);
    expect(nextGen2.generation).toBe(2);
    expect(nextGen2.cells[2][1]).toBe(true);
    expect(nextGen2.cells[2][2]).toBe(true);
    expect(nextGen2.cells[2][3]).toBe(true);
  });

  it('should keep a 2x2 block static', () => {
    // Create a 2x2 block
    let grid = createGrid(5, 5);
    grid = toggleCell(grid, 1, 1);
    grid = toggleCell(grid, 2, 1);
    grid = toggleCell(grid, 1, 2);
    grid = toggleCell(grid, 2, 2);

    expect(grid.liveCellCount).toBe(4);

    const nextGen = computeNextGeneration(grid);
    expect(nextGen.liveCellCount).toBe(4);
    expect(nextGen.cells[1][1]).toBe(true);
    expect(nextGen.cells[2][1]).toBe(true);
    expect(nextGen.cells[1][2]).toBe(true);
    expect(nextGen.cells[2][2]).toBe(true);
  });

  it('should kill isolated cells', () => {
    let grid = createGrid(5, 5);
    grid = toggleCell(grid, 2, 2);

    const nextGen = computeNextGeneration(grid);
    expect(nextGen.liveCellCount).toBe(0);
    expect(nextGen.cells[2][2]).toBe(false);
  });

  it('should birth a cell with exactly 3 neighbors', () => {
    let grid = createGrid(5, 5);
    // Create an L-shape (3 neighbors for the empty cell at 2,2)
    grid = toggleCell(grid, 1, 1);
    grid = toggleCell(grid, 2, 1);
    grid = toggleCell(grid, 1, 2);
    // (2,2) has 3 neighbors and should birth

    const nextGen = computeNextGeneration(grid);
    expect(nextGen.cells[2][2]).toBe(true);
  });

  it('should increment generation counter', () => {
    const grid = createGrid(5, 5);
    expect(grid.generation).toBe(0);

    const nextGen = computeNextGeneration(grid);
    expect(nextGen.generation).toBe(1);

    const nextGen2 = computeNextGeneration(nextGen);
    expect(nextGen2.generation).toBe(2);
  });
});
