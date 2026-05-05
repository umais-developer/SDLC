/**
 * Grid component for rendering Conway's Game of Life grid
 */

import React, { useEffect, useRef, useMemo } from 'react';
import { useGame } from '../context/GameContext';
import type { Grid } from '../engine/grid';

const CELL_SIZE = 10;
const GRID_COLOR = '#e5e7eb';
const ALIVE_COLOR = '#10b981';
const DEAD_COLOR = '#f3f4f6';

interface GridProps {
  onCellClick?: (x: number, y: number) => void;
  onCellDrag?: (x: number, y: number) => void;
}

export function GridComponent({ onCellClick, onCellDrag }: GridProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { grid } = useGame();
  const isDraggingRef = useRef(false);
  const lastCellRef = useRef<{ x: number; y: number } | null>(null);

  const canvasWidth = grid.width * CELL_SIZE;
  const canvasHeight = grid.height * CELL_SIZE;

  /**
   * Render grid to canvas
   */
  const renderGrid = useMemo(
    () => (canvas: HTMLCanvasElement, gridData: Grid) => {
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const { cells, width, height } = gridData;

      // Clear canvas
      ctx.fillStyle = DEAD_COLOR;
      ctx.fillRect(0, 0, width * CELL_SIZE, height * CELL_SIZE);

      // Draw grid lines
      ctx.strokeStyle = GRID_COLOR;
      ctx.lineWidth = 0.5;

      for (let x = 0; x <= width; x++) {
        ctx.beginPath();
        ctx.moveTo(x * CELL_SIZE, 0);
        ctx.lineTo(x * CELL_SIZE, height * CELL_SIZE);
        ctx.stroke();
      }

      for (let y = 0; y <= height; y++) {
        ctx.beginPath();
        ctx.moveTo(0, y * CELL_SIZE);
        ctx.lineTo(width * CELL_SIZE, y * CELL_SIZE);
        ctx.stroke();
      }

      // Draw alive cells
      ctx.fillStyle = ALIVE_COLOR;
      for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
          if (cells[y][x]) {
            ctx.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
          }
        }
      }
    },
    []
  );

  /**
   * Draw grid on canvas when grid changes
   */
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.width = canvasWidth;
    canvas.height = canvasHeight;

    renderGrid(canvas, grid);
  }, [grid, canvasWidth, canvasHeight, renderGrid]);

  /**
   * Handle mouse down on canvas
   */
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    isDraggingRef.current = true;
    const { x, y } = getCellCoordinates(e, canvas);

    onCellClick?.(x, y);
    lastCellRef.current = { x, y };
  };

  /**
   * Handle mouse move on canvas (for dragging)
   */
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || !isDraggingRef.current) return;

    const { x, y } = getCellCoordinates(e, canvas);

    if (lastCellRef.current && (lastCellRef.current.x !== x || lastCellRef.current.y !== y)) {
      onCellDrag?.(x, y);
      lastCellRef.current = { x, y };
    }
  };

  /**
   * Handle mouse up
   */
  const handleMouseUp = () => {
    isDraggingRef.current = false;
    lastCellRef.current = null;
  };

  /**
   * Get cell coordinates from mouse event
   */
  const getCellCoordinates = (
    e: React.MouseEvent<HTMLCanvasElement>,
    canvas: HTMLCanvasElement
  ): { x: number; y: number } => {
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) / CELL_SIZE);
    const y = Math.floor((e.clientY - rect.top) / CELL_SIZE);

    return {
      x: Math.max(0, Math.min(x, grid.width - 1)),
      y: Math.max(0, Math.min(y, grid.height - 1)),
    };
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <canvas
        ref={canvasRef}
        width={canvasWidth}
        height={canvasHeight}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className="border-2 border-gray-300 bg-gray-100 cursor-crosshair select-none"
        style={{
          maxWidth: '100%',
          maxHeight: '70vh',
        }}
        aria-label={`Game of Life grid (${grid.width}×${grid.height}). Click or drag to toggle cells. Generation: ${grid.generation}, Live cells: ${grid.liveCellCount}`}
        role="img"
      />
      <div className="text-sm text-gray-600">
        {grid.liveCellCount === 0 ? (
          <p>Click to draw cells or select a pattern from the library</p>
        ) : (
          <p>Generation: {grid.generation} | Live Cells: {grid.liveCellCount}</p>
        )}
      </div>
    </div>
  );
}
