/**
 * Conway's Game of Life rules engine
 */

import type { Grid } from './grid';
import { countLiveCells } from './grid';

/**
 * Count alive neighbors for a cell at (x, y) using toroidal wrapping
 */
export function countNeighbors(grid: Grid, x: number, y: number): number {
  const { cells, width, height, boundaryMode } = grid;
  let count = 0;

  for (let dy = -1; dy <= 1; dy++) {
    for (let dx = -1; dx <= 1; dx++) {
      if (dx === 0 && dy === 0) continue;

      let nx = x + dx;
      let ny = y + dy;

      if (boundaryMode === 'wrap') {
        // Toroidal wrapping
        nx = (nx + width) % width;
        ny = (ny + height) % height;
      } else {
        // Boundary death: cells outside grid are dead
        if (nx < 0 || nx >= width || ny < 0 || ny >= height) {
          continue;
        }
      }

      if (cells[ny][nx]) {
        count++;
      }
    }
  }

  return count;
}

/**
 * Check if cell at (x, y) is alive, handling boundary conditions
 */
export function isAlive(grid: Grid, x: number, y: number): boolean {
  const { cells, width, height, boundaryMode } = grid;

  if (boundaryMode === 'death') {
    if (x < 0 || x >= width || y < 0 || y >= height) {
      return false;
    }
  } else {
    // Wrap boundary
    x = (x + width) % width;
    y = (y + height) % height;
  }

  return cells[y][x];
}

/**
 * Apply Conway's Game of Life rules to compute the next generation
 * Rules:
 * - A live cell with 2 or 3 neighbors survives
 * - A dead cell with exactly 3 neighbors becomes alive
 * - All other cells die or remain dead
 */
export function computeNextGeneration(grid: Grid): Grid {
  const { cells, width, height } = grid;
  const newCells = Array.from({ length: height }, () =>
    Array.from({ length: width }, () => false)
  );

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const neighbors = countNeighbors(grid, x, y);
      const isCurrentlyAlive = cells[y][x];

      if (isCurrentlyAlive && (neighbors === 2 || neighbors === 3)) {
        // Live cell survives
        newCells[y][x] = true;
      } else if (!isCurrentlyAlive && neighbors === 3) {
        // Dead cell births
        newCells[y][x] = true;
      }
      // All other cases: cell dies or stays dead
    }
  }

  const liveCellCount = countLiveCells(newCells);

  return {
    ...grid,
    cells: newCells,
    generation: grid.generation + 1,
    liveCellCount,
  };
}
