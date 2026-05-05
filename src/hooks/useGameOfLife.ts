/**
 * React hook for Game of Life engine with Web Worker support
 */

import { useEffect, useRef, useState } from 'react';
import { computeNextGeneration } from '../engine/rules';
import type { Grid } from '../engine/grid';

interface UseGameOfLifeOptions {
  useWorker?: boolean;
}

export function useGameOfLife(options: UseGameOfLifeOptions = {}) {
  const { useWorker = true } = options;
  const workerRef = useRef<Worker | null>(null);
  const [isWorkerAvailable, setIsWorkerAvailable] = useState(true);
  const computePromiseRef = useRef<{
    resolve: (grid: Grid) => void;
    reject: (error: Error) => void;
  } | null>(null);

  // Initialize Web Worker
  useEffect(() => {
    if (!useWorker) return;

    try {
      // Dynamically import worker
      const worker = new Worker(
        new URL('../engine/game-of-life.worker.ts', import.meta.url),
        { type: 'module' }
      );

      worker.onmessage = (event: MessageEvent) => {
        const { type, grid, message } = event.data;

        if (type === 'result' && computePromiseRef.current) {
          computePromiseRef.current.resolve(grid);
          computePromiseRef.current = null;
        } else if (type === 'error' && computePromiseRef.current) {
          computePromiseRef.current.reject(new Error(message));
          computePromiseRef.current = null;
        }
      };

      worker.onerror = (error) => {
        console.error('Worker error:', error);
        // Reject any pending computation
        if (computePromiseRef.current) {
          computePromiseRef.current.reject(new Error('Worker crashed'));
          computePromiseRef.current = null;
        }
        setIsWorkerAvailable(false);
      };

      workerRef.current = worker;
      return () => {
        worker.terminate();
      };
    } catch (error) {
      console.warn('Web Worker not available, falling back to main thread:', error);
      setIsWorkerAvailable(false);
    }
  }, [useWorker]);

  /**
   * Compute next generation using worker or main thread
   */
  const computeNext = async (grid: Grid): Promise<Grid> => {
    if (workerRef.current && isWorkerAvailable) {
      return new Promise((resolve, reject) => {
        computePromiseRef.current = { resolve, reject };
        
        // Set timeout to catch hung promises (worker doesn't respond)
        const timeoutId = setTimeout(() => {
          if (computePromiseRef.current) {
            computePromiseRef.current.reject(new Error('Worker computation timeout'));
            computePromiseRef.current = null;
            setIsWorkerAvailable(false);
          }
        }, 5000);

        try {
          workerRef.current!.postMessage({
            type: 'compute',
            grid,
          });
          // Clear timeout on successful message (will be cleared again on result)
          clearTimeout(timeoutId);
        } catch (error) {
          clearTimeout(timeoutId);
          reject(error as Error);
        }
      });
    } else {
      // Fallback: compute on main thread
      try {
        return Promise.resolve(computeNextGeneration(grid));
      } catch (error) {
        return Promise.reject(error);
      }
    }
  };

  return {
    computeNext,
    isWorkerAvailable,
  };
}
