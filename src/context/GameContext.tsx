/**
 * React Context for Game of Life application state
 */

import React, { createContext, useCallback, useReducer, ReactNode } from 'react';
import {
  createGrid,
  toggleCell,
  clearGrid,
  type Grid,
} from '../engine/grid';

interface GameContextType {
  grid: Grid;
  isPlaying: boolean;
  speed: number;
  toggleCell: (x: number, y: number) => void;
  playSimulation: () => void;
  pauseSimulation: () => void;
  stepGeneration: () => void;
  clearGridState: () => void;
  resizeGrid: (width: number, height: number) => void;
  setSpeed: (speed: number) => void;
  setGridState: (grid: Grid) => void;
  updateGrid: (grid: Grid) => void;
}

type GameAction =
  | { type: 'TOGGLE_CELL'; x: number; y: number }
  | { type: 'PLAY' }
  | { type: 'PAUSE' }
  | { type: 'CLEAR' }
  | { type: 'RESIZE'; width: number; height: number }
  | { type: 'SET_SPEED'; speed: number }
  | { type: 'SET_GRID'; grid: Grid }
  | { type: 'UPDATE_GRID'; grid: Grid };

interface GameState {
  grid: Grid;
  isPlaying: boolean;
  speed: number;
}

const initialState: GameState = {
  grid: createGrid(50, 50),
  isPlaying: false,
  speed: 10,
};

function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case 'TOGGLE_CELL':
      return {
        ...state,
        grid: toggleCell(state.grid, action.x, action.y),
      };

    case 'PLAY':
      return {
        ...state,
        isPlaying: true,
      };

    case 'PAUSE':
      return {
        ...state,
        isPlaying: false,
      };

    case 'CLEAR':
      return {
        ...state,
        grid: clearGrid(state.grid),
        isPlaying: false,
      };

    case 'RESIZE':
      return {
        ...state,
        grid: createGrid(action.width, action.height),
        isPlaying: false,
      };

    case 'SET_SPEED': {
      const speed = Math.max(1, Math.min(10, action.speed));
      return {
        ...state,
        speed,
      };
    }

    case 'SET_GRID':
      return {
        ...state,
        grid: action.grid,
        isPlaying: false,
      };

    case 'UPDATE_GRID':
      return {
        ...state,
        grid: action.grid,
      };

    default:
      return state;
  }
}

export const GameContext = createContext<GameContextType | undefined>(undefined);

interface GameProviderProps {
  children: ReactNode;
}

export function GameProvider({ children }: GameProviderProps) {
  const [state, dispatch] = useReducer(gameReducer, initialState);

  const contextValue: GameContextType = {
    grid: state.grid,
    isPlaying: state.isPlaying,
    speed: state.speed,

    toggleCell: useCallback((x: number, y: number) => {
      dispatch({ type: 'TOGGLE_CELL', x, y });
    }, []),

    playSimulation: useCallback(() => {
      dispatch({ type: 'PLAY' });
    }, []),

    pauseSimulation: useCallback(() => {
      dispatch({ type: 'PAUSE' });
    }, []),

    stepGeneration: useCallback(() => {
      // Stepping is handled by the app component with rule engine
    }, []),

    clearGridState: useCallback(() => {
      dispatch({ type: 'CLEAR' });
    }, []),

    resizeGrid: useCallback((width: number, height: number) => {
      dispatch({ type: 'RESIZE', width, height });
    }, []),

    setSpeed: useCallback((speed: number) => {
      dispatch({ type: 'SET_SPEED', speed });
    }, []),

    setGridState: useCallback((grid: Grid) => {
      dispatch({ type: 'SET_GRID', grid });
    }, []),

    updateGrid: useCallback((grid: Grid) => {
      dispatch({ type: 'UPDATE_GRID', grid });
    }, []),
  };

  return (
    <GameContext.Provider value={contextValue}>
      {children}
    </GameContext.Provider>
  );
}

export function useGame(): GameContextType {
  const context = React.useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within GameProvider');
  }
  return context;
}
