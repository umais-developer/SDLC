/**
 * Controls Panel component for simulation control
 */

import { useState } from 'react';
import { useGame } from '../context/GameContext';

interface ControlsPanelProps {
  onStep: () => void;
  isStepDisabled?: boolean;
}

export function ControlsPanel({ onStep, isStepDisabled = false }: ControlsPanelProps) {
  const { isPlaying, playSimulation, pauseSimulation, clearGridState, resizeGrid, speed, setSpeed, grid } =
    useGame();
  const [showResizeModal, setShowResizeModal] = useState(false);
  const [newWidth, setNewWidth] = useState(grid.width);
  const [newHeight, setNewHeight] = useState(grid.height);

  const handleResize = () => {
    const width = parseInt(String(newWidth), 10);
    const height = parseInt(String(newHeight), 10);
    
    // Validate input
    if (isNaN(width) || isNaN(height)) {
      alert('Width and Height must be valid numbers (10–200)');
      return;
    }
    
    // Clamp to valid range
    const validWidth = Math.max(10, Math.min(200, width));
    const validHeight = Math.max(10, Math.min(200, height));
    
    resizeGrid(validWidth, validHeight);
    setShowResizeModal(false);
  };

  return (
    <div className="flex flex-col gap-4 p-4 bg-white rounded-lg shadow-lg">
      <h2 className="text-lg font-bold">Controls</h2>

      {/* Play / Pause */}
      <div className="flex gap-2">
        <button
          onClick={isPlaying ? pauseSimulation : playSimulation}
          disabled={!isPlaying && grid.liveCellCount === 0}
          aria-label={isPlaying ? 'Pause simulation' : 'Start simulation'}
          className="flex-1 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isPlaying ? '⏸ Pause' : '▶ Play'}
        </button>

        <button
          onClick={onStep}
          disabled={isPlaying || isStepDisabled}
          aria-label="Advance one generation"
          className="flex-1 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          ⏭ Step
        </button>
      </div>

      {/* Speed Control */}
      <div className="flex flex-col gap-2">
        <label htmlFor="speed" className="text-sm font-medium">
          Speed: {speed} gen/sec
        </label>
        <input
          id="speed"
          type="range"
          min="1"
          max="10"
          value={speed}
          onChange={e => setSpeed(parseInt(e.target.value))}
          className="w-full"
        />
      </div>

      {/* Grid Info */}
      <div className="text-sm text-gray-600">
        <p>Grid Size: {grid.width}×{grid.height}</p>
        <p>Generation: {grid.generation}</p>
        <p>Live Cells: {grid.liveCellCount}</p>
      </div>

      {/* Resize & Clear */}
      <div className="flex gap-2">
        <button
          onClick={() => setShowResizeModal(true)}
          aria-label="Resize grid"
          className="flex-1 px-3 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
        >
          📐 Resize
        </button>

        <button
          onClick={clearGridState}
          aria-label="Clear all cells from grid"
          className="flex-1 px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
        >
          🗑 Clear
        </button>
      </div>

      {/* Resize Modal */}
      {showResizeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl">
            <h3 className="text-lg font-bold mb-4">Resize Grid</h3>

            <div className="space-y-3 mb-4">
              <div>
                <label htmlFor="width" className="text-sm font-medium">
                  Width (10-200):
                </label>
                <input
                  id="width"
                  type="number"
                  min="10"
                  max="200"
                  value={newWidth}
                  onChange={e => setNewWidth(parseInt(e.target.value))}
                  className="w-full border rounded px-2 py-1 mt-1"
                />
              </div>

              <div>
                <label htmlFor="height" className="text-sm font-medium">
                  Height (10-200):
                </label>
                <input
                  id="height"
                  type="number"
                  min="10"
                  max="200"
                  value={newHeight}
                  onChange={e => setNewHeight(parseInt(e.target.value))}
                  className="w-full border rounded px-2 py-1 mt-1"
                />
              </div>
            </div>

            <p className="text-sm text-red-600 mb-4">
              ⚠️ Resizing will clear the current pattern
            </p>

            <div className="flex gap-2">
              <button
                onClick={handleResize}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Resize
              </button>
              <button
                onClick={() => setShowResizeModal(false)}
                className="flex-1 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
