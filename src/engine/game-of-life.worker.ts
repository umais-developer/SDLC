/**
 * Web Worker for Conway's Game of Life computation
 * Offloads heavy computation from main thread
 */

import { computeNextGeneration } from './rules';
import type { Grid } from './grid';

interface WorkerMessage {
  type: 'compute';
  grid: Grid;
}

interface ResultMessage {
  type: 'result';
  grid: Grid;
}

// Listen for messages from main thread
self.onmessage = (event: MessageEvent<WorkerMessage>) => {
  const { type, grid } = event.data;

  if (type === 'compute') {
    try {
      const nextGrid = computeNextGeneration(grid);
      const result: ResultMessage = {
        type: 'result',
        grid: nextGrid,
      };
      self.postMessage(result);
    } catch (error) {
      console.error('Worker computation error:', error);
      self.postMessage({
        type: 'error',
        message: 'Computation failed',
      });
    }
  }
};
