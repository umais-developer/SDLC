/**
 * Pattern Library component
 */

import { useState } from 'react';
import React from 'react';

// Built-in patterns
const PATTERNS = [
  {
    name: 'Glider',
    description: 'A spaceship that travels diagonally. Repeats every 4 generations.',
    cells: [
      [false, true, false],
      [false, false, true],
      [true, true, true],
    ],
  },
  {
    name: 'Blinker',
    description: 'Period 2 oscillator. Alternates between horizontal and vertical.',
    cells: [[true, true, true]],
  },
  {
    name: 'Block',
    description: 'A 2×2 square that remains stable forever.',
    cells: [
      [true, true],
      [true, true],
    ],
  },
  {
    name: 'Pulsar',
    description: 'Period 3 oscillator with complex symmetry.',
    cells: [
      [false, false, true, true, true, false, false],
      [false, false, false, false, false, false, false],
      [true, false, false, false, false, false, true],
      [true, false, false, false, false, false, true],
      [true, false, false, false, false, false, true],
      [false, false, false, false, false, false, false],
      [false, false, true, true, true, false, false],
    ],
  },
];

export function PatternLibrary() {
  const [selectedPattern, setSelectedPattern] = useState<number | null>(null);
  const [showPlacementGuide, setShowPlacementGuide] = useState(false);

  return (
    <div className="flex flex-col gap-4 p-4 bg-white rounded-lg shadow-lg">
      <h2 className="text-lg font-bold">Pattern Library</h2>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {PATTERNS.map((pattern, idx) => (
          <div
            key={idx}
            onClick={() => setSelectedPattern(selectedPattern === idx ? null : idx)}
            className={`p-3 rounded cursor-pointer transition ${
              selectedPattern === idx
                ? 'bg-blue-200 border-2 border-blue-500'
                : 'bg-gray-100 border-2 border-gray-300 hover:bg-gray-200'
            }`}
          >
            <div className="font-medium">{pattern.name}</div>
            <div className="text-sm text-gray-600">{pattern.description}</div>
          </div>
        ))}
      </div>

      {selectedPattern !== null && (
        <div className="border-t pt-4">
          <div className="mb-2 text-sm font-medium">Click on grid to place pattern</div>
          <button
            onClick={() => setShowPlacementGuide(!showPlacementGuide)}
            className="px-3 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 text-sm"
          >
            {showPlacementGuide ? 'Hide Preview' : 'Show Preview'}
          </button>

          {showPlacementGuide && (
            <div className="mt-3 p-2 bg-gray-100 rounded">
              <PatternPreview pattern={PATTERNS[selectedPattern]} />
            </div>
          )}
        </div>
      )}

      {selectedPattern === null && (
        <div className="text-sm text-gray-500 text-center py-4">
          Select a pattern to place it on the grid
        </div>
      )}
    </div>
  );
}

/**
 * Display a preview of a pattern
 */
function PatternPreview({ pattern }: { pattern: (typeof PATTERNS)[0] }) {
  const canvasRef = React.useRef<HTMLCanvasElement>(null);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const cellSize = 12;
    canvas.width = pattern.cells[0].length * cellSize;
    canvas.height = pattern.cells.length * cellSize;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Draw cells
    ctx.fillStyle = '#f3f4f6';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#10b981';
    for (let y = 0; y < pattern.cells.length; y++) {
      for (let x = 0; x < pattern.cells[y].length; x++) {
        if (pattern.cells[y][x]) {
          ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
      }
    }

    // Draw grid
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= pattern.cells[0].length; x++) {
      ctx.beginPath();
      ctx.moveTo(x * cellSize, 0);
      ctx.lineTo(x * cellSize, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y <= pattern.cells.length; y++) {
      ctx.beginPath();
      ctx.moveTo(0, y * cellSize);
      ctx.lineTo(canvas.width, y * cellSize);
      ctx.stroke();
    }
  }, [pattern]);

  return <canvas ref={canvasRef} className="border border-gray-300 bg-white" />;
}
