/**
 * Grid data structure and utilities for Conway's Game of Life
 */

export interface Grid {
  cells: boolean[][];
  width: number;
  height: number;
  generation: number;
  liveCellCount: number;
  boundaryMode: 'wrap' | 'death';
}

export interface GameState {
  grid: Grid;
  isPlaying: boolean;
  speed: number;
  generation: number;
  liveCellCount: number;
}

/**
 * Create a new empty grid with specified dimensions
 */
export function createGrid(width: number, height: number): Grid {
  const cells = Array.from({ length: height }, () =>
    Array.from({ length: width }, () => false)
  );

  return {
    cells,
    width,
    height,
    generation: 0,
    liveCellCount: 0,
    boundaryMode: 'wrap',
  };
}

/**
 * Toggle a cell state (alive <-> dead)
 */
export function toggleCell(grid: Grid, x: number, y: number): Grid {
  if (x < 0 || x >= grid.width || y < 0 || y >= grid.height) {
    return grid;
  }

  const newCells = grid.cells.map(row => [...row]);
  const wasAlive = newCells[y][x];
  newCells[y][x] = !wasAlive;

  const liveCellCount = grid.liveCellCount + (wasAlive ? -1 : 1);

  return {
    ...grid,
    cells: newCells,
    liveCellCount: Math.max(0, liveCellCount),
  };
}

/**
 * Serialize grid to JSON
 */
export function serializeGrid(grid: Grid): string {
  return JSON.stringify({
    cells: grid.cells,
    width: grid.width,
    height: grid.height,
    generation: grid.generation,
    liveCellCount: grid.liveCellCount,
    boundaryMode: grid.boundaryMode,
  });
}

/**
 * Deserialize grid from JSON
 */
export function deserializeGrid(json: string): Grid {
  try {
    return JSON.parse(json) as Grid;
  } catch {
    throw new Error('Invalid grid data');
  }
}

/**
 * Copy grid without mutation
 */
export function copyGrid(grid: Grid): Grid {
  return {
    ...grid,
    cells: grid.cells.map(row => [...row]),
  };
}

/**
 * Count live cells in grid
 */
export function countLiveCells(cells: boolean[][]): number {
  return cells.reduce((sum, row) =>
    sum + row.reduce((rowSum, cell) => rowSum + (cell ? 1 : 0), 0), 0
  );
}

/**
 * Set all cells to dead
 */
export function clearGrid(grid: Grid): Grid {
  const cells = Array.from({ length: grid.height }, () =>
    Array.from({ length: grid.width }, () => false)
  );

  return {
    ...grid,
    cells,
    generation: 0,
    liveCellCount: 0,
  };
}
