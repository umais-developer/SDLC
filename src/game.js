// game.js — GameState module
// Pure functions: no DOM access, no side effects.

'use strict';

/** All 8 win lines as cell-index triples */
const WIN_LINES = [
  [0, 1, 2], [3, 4, 5], [6, 7, 8], // rows
  [0, 3, 6], [1, 4, 7], [2, 5, 8], // columns
  [0, 4, 8], [2, 4, 6],             // diagonals
];

/**
 * @typedef {'X'|'O'|null} Cell
 * @typedef {'pvp'|'easy'|'impossible'} GameMode
 * @typedef {'ongoing'|'win'|'draw'} StatusType
 *
 * @typedef {Object} TerminalStatus
 * @property {StatusType} type
 * @property {'X'|'O'|null} winner
 * @property {number[]|null} line  — winning cell indices, or null
 *
 * @typedef {Object} GameState
 * @property {Cell[]} cells        — length-9 array, index 0-8, row-major
 * @property {'X'|'O'} current    — whose turn it is
 * @property {GameMode} mode
 * @property {TerminalStatus} status
 */

/**
 * Create a fresh game state.
 * @param {GameMode} mode
 * @returns {GameState}
 */
function createGame(mode) {
  return {
    cells: Array(9).fill(null),
    current: 'X',
    mode,
    status: { type: 'ongoing', winner: null, line: null },
  };
}

/**
 * Return all indices of empty cells.
 * @param {GameState} state
 * @returns {number[]}
 */
function getLegalMoves(state) {
  return state.cells.reduce((acc, cell, i) => {
    if (cell === null) acc.push(i);
    return acc;
  }, []);
}

/**
 * Check a cell array for a winner.
 * @param {Cell[]} cells
 * @returns {TerminalStatus}
 */
function checkWinner(cells) {
  for (const [a, b, c] of WIN_LINES) {
    if (cells[a] !== null && cells[a] === cells[b] && cells[a] === cells[c]) {
      return { type: 'win', winner: cells[a], line: [a, b, c] };
    }
  }
  if (cells.every(c => c !== null)) {
    return { type: 'draw', winner: null, line: null };
  }
  return { type: 'ongoing', winner: null, line: null };
}

/**
 * Apply a move and return a new GameState. Throws if the move is illegal.
 * @param {GameState} state
 * @param {number} cellIndex  0-8
 * @returns {GameState}
 */
function applyMove(state, cellIndex) {
  if (cellIndex < 0 || cellIndex > 8) {
    throw new RangeError(`Cell index ${cellIndex} is out of range (0–8).`);
  }
  if (state.cells[cellIndex] !== null) {
    throw new Error(`Cell ${cellIndex} is already occupied.`);
  }
  if (state.status.type !== 'ongoing') {
    throw new Error('Game is over — cannot apply a move to a terminal state.');
  }

  const cells = state.cells.slice();
  cells[cellIndex] = state.current;
  const status = checkWinner(cells);
  const current = state.current === 'X' ? 'O' : 'X';

  return { cells, current, mode: state.mode, status };
}

// CommonJS + ESM-compatible export
if (typeof module !== 'undefined') {
  module.exports = { createGame, getLegalMoves, checkWinner, applyMove, WIN_LINES };
}
