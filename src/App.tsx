/**
 * Main App component for Conway's Game of Life
 */

import { useEffect, useRef, useCallback } from 'react';
import { useGame } from './context/GameContext';
import { useGameOfLife } from './hooks/useGameOfLife';
import { GridComponent } from './components/Grid';
import { ControlsPanel } from './components/ControlsPanel';
import { PatternLibrary } from './components/PatternLibrary';

function App() {
  const {
    grid,
    isPlaying,
    speed,
    pauseSimulation,
    updateGrid,
    toggleCell,
  } = useGame();

  const { computeNext } = useGameOfLife();
  const animationFrameRef = useRef<number | null>(null);
  const lastTickTimeRef = useRef<number>(Date.now());
  const isSteppingRef = useRef(false);

  /**
   * Handle cell click on grid
   */
  const handleCellClick = useCallback(
    (x: number, y: number) => {
      toggleCell(x, y);
    },
    [toggleCell]
  );

  /**
   * Handle cell drag on grid
   */
  const handleCellDrag = useCallback(
    (x: number, y: number) => {
      toggleCell(x, y);
    },
    [toggleCell]
  );

  /**
   * Handle step button
   */
  const handleStep = useCallback(async () => {
    if (isSteppingRef.current) return;

    isSteppingRef.current = true;
    try {
      const nextGrid = await computeNext(grid);
      updateGrid(nextGrid);
    } catch (error) {
      console.error('Step error:', error);
    } finally {
      isSteppingRef.current = false;
    }
  }, [grid, computeNext, updateGrid]);

  /**
   * Main simulation loop
   */
  useEffect(() => {
    if (!isPlaying) return;

    const tickInterval = 1000 / speed; // ms per tick

    const animate = async () => {
      const now = Date.now();
      const timeSinceLastTick = now - lastTickTimeRef.current;

      if (timeSinceLastTick >= tickInterval) {
        try {
          const nextGrid = await computeNext(grid);
          updateGrid(nextGrid);
          lastTickTimeRef.current = now;
        } catch (error) {
          console.error('Simulation error:', error);
          pauseSimulation();
        }
      }

      if (isPlaying) {
        animationFrameRef.current = requestAnimationFrame(animate);
      }
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isPlaying, speed, grid, computeNext, updateGrid, pauseSimulation]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🎮 Conway's Game of Life
          </h1>
          <p className="text-gray-600">
            Interactive cellular automaton simulator
          </p>
        </div>

        {/* Main Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Grid */}
          <div className="lg:col-span-3">
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <GridComponent onCellClick={handleCellClick} onCellDrag={handleCellDrag} />
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            <ControlsPanel onStep={handleStep} isStepDisabled={isPlaying} />
            <PatternLibrary />
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-600">
          <p>
            Drag to draw • Select patterns • Use Play/Pause to control simulation
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
