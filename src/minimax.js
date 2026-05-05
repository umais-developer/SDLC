// minimax.js — EasyAI and MinimaxEngine
// No DOM access. Pure functions only.

'use strict';

const { getLegalMoves, applyMove, checkWinner } = require('./game.js');

// ---------------------------------------------------------------------------
// Easy AI
// ---------------------------------------------------------------------------

/**
 * Return a random legal move index.
 * @param {import('./game').GameState} state
 * @returns {number}
 */
function easyBestMove(state) {
  const moves = getLegalMoves(state);
  if (moves.length === 0) throw new Error('No legal moves available.');
  return moves[Math.floor(Math.random() * moves.length)];
}

// ---------------------------------------------------------------------------
// Minimax (plain — used for score overlay; guarantees accurate per-cell scores)
// ---------------------------------------------------------------------------

/**
 * @param {import('./game').GameState} state
 * @param {boolean} isMaximising  true when it is O's turn (AI maximises)
 * @returns {number}  +1 O wins, -1 X wins, 0 draw
 */
function minimax(state, isMaximising) {
  const { type, winner } = state.status;

  if (type === 'win') return winner === 'O' ? 1 : -1;
  if (type === 'draw') return 0;

  const moves = getLegalMoves(state);

  if (isMaximising) {
    let best = -Infinity;
    for (const move of moves) {
      const next = applyMove(state, move);
      best = Math.max(best, minimax(next, false));
      if (best === 1) break; // can't do better
    }
    return best;
  } else {
    let best = Infinity;
    for (const move of moves) {
      const next = applyMove(state, move);
      best = Math.min(best, minimax(next, true));
      if (best === -1) break; // can't do worse
    }
    return best;
  }
}

// ---------------------------------------------------------------------------
// Minimax with alpha-beta pruning (used for move selection only)
// ---------------------------------------------------------------------------

/**
 * @param {import('./game').GameState} state
 * @param {number} alpha
 * @param {number} beta
 * @param {boolean} isMaximising
 * @returns {number}
 */
function minimaxAB(state, alpha, beta, isMaximising) {
  const { type, winner } = state.status;

  if (type === 'win') return winner === 'O' ? 1 : -1;
  if (type === 'draw') return 0;

  const moves = getLegalMoves(state);

  if (isMaximising) {
    let best = -Infinity;
    for (const move of moves) {
      const next = applyMove(state, move);
      best = Math.max(best, minimaxAB(next, alpha, beta, false));
      alpha = Math.max(alpha, best);
      if (beta <= alpha) break;
    }
    return best;
  } else {
    let best = Infinity;
    for (const move of moves) {
      const next = applyMove(state, move);
      best = Math.min(best, minimaxAB(next, alpha, beta, true));
      beta = Math.min(beta, best);
      if (beta <= alpha) break;
    }
    return best;
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Return the best move index for the Impossible AI using alpha-beta minimax.
 * @param {import('./game').GameState} state
 * @returns {number}
 */
function impossibleBestMove(state) {
  const moves = getLegalMoves(state);
  if (moves.length === 0) throw new Error('No legal moves available.');

  let bestScore = -Infinity;
  let bestMove = moves[0];

  for (const move of moves) {
    const next = applyMove(state, move);
    // After O moves, it's X's turn (minimising)
    const score = minimaxAB(next, -Infinity, Infinity, false);
    if (score > bestScore) {
      bestScore = score;
      bestMove = move;
    }
  }
  return bestMove;
}

/**
 * Return a score map { cellIndex: score } for every legal move using plain minimax.
 * Deliberately does NOT use alpha-beta so each displayed score is the true minimax value.
 * @param {import('./game').GameState} state
 * @returns {Object.<number, number>}
 */
function scoreAllMoves(state) {
  const moves = getLegalMoves(state);
  const scores = {};

  for (const move of moves) {
    const next = applyMove(state, move);
    // After O moves, it's X's turn (minimising from O's perspective)
    scores[move] = minimax(next, false);
  }
  return scores;
}

module.exports = { easyBestMove, impossibleBestMove, scoreAllMoves, minimax, minimaxAB };
