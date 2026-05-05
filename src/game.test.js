// game.test.js — Unit tests for GameState module
// Run with: node --test src/game.test.js  (Node 18+)

'use strict';

const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { createGame, getLegalMoves, checkWinner, applyMove } = require('./game.js');

// ---------------------------------------------------------------------------
// checkWinner
// ---------------------------------------------------------------------------

describe('checkWinner', () => {
  it('detects row 0 win for X', () => {
    const cells = ['X','X','X', null,null,null, null,null,null];
    const r = checkWinner(cells);
    assert.equal(r.type, 'win');
    assert.equal(r.winner, 'X');
    assert.deepEqual(r.line, [0,1,2]);
  });

  it('detects row 1 win for O', () => {
    const cells = [null,null,null, 'O','O','O', null,null,null];
    const r = checkWinner(cells);
    assert.equal(r.type, 'win');
    assert.equal(r.winner, 'O');
    assert.deepEqual(r.line, [3,4,5]);
  });

  it('detects row 2 win', () => {
    const cells = [null,null,null, null,null,null, 'X','X','X'];
    assert.equal(checkWinner(cells).type, 'win');
    assert.deepEqual(checkWinner(cells).line, [6,7,8]);
  });

  it('detects column 0 win', () => {
    const cells = ['O',null,null, 'O',null,null, 'O',null,null];
    assert.equal(checkWinner(cells).winner, 'O');
    assert.deepEqual(checkWinner(cells).line, [0,3,6]);
  });

  it('detects column 1 win', () => {
    const cells = [null,'X',null, null,'X',null, null,'X',null];
    assert.equal(checkWinner(cells).winner, 'X');
  });

  it('detects column 2 win', () => {
    const cells = [null,null,'O', null,null,'O', null,null,'O'];
    assert.equal(checkWinner(cells).winner, 'O');
  });

  it('detects main diagonal win', () => {
    const cells = ['X',null,null, null,'X',null, null,null,'X'];
    const r = checkWinner(cells);
    assert.equal(r.type, 'win');
    assert.deepEqual(r.line, [0,4,8]);
  });

  it('detects anti-diagonal win', () => {
    const cells = [null,null,'O', null,'O',null, 'O',null,null];
    const r = checkWinner(cells);
    assert.equal(r.type, 'win');
    assert.deepEqual(r.line, [2,4,6]);
  });

  it('detects draw (full board, no winner)', () => {
    const cells = ['X','O','X', 'X','O','O', 'O','X','X'];
    const r = checkWinner(cells);
    assert.equal(r.type, 'draw');
    assert.equal(r.winner, null);
    assert.equal(r.line, null);
  });

  it('returns ongoing for partial board with no winner', () => {
    const cells = ['X',null,null, null,'O',null, null,null,null];
    assert.equal(checkWinner(cells).type, 'ongoing');
  });

  it('returns ongoing for empty board', () => {
    assert.equal(checkWinner(Array(9).fill(null)).type, 'ongoing');
  });
});

// ---------------------------------------------------------------------------
// getLegalMoves
// ---------------------------------------------------------------------------

describe('getLegalMoves', () => {
  it('returns all 9 indices for empty board', () => {
    const state = createGame('pvp');
    assert.deepEqual(getLegalMoves(state), [0,1,2,3,4,5,6,7,8]);
  });

  it('returns empty array for full board', () => {
    const state = { cells: ['X','O','X','X','O','O','O','X','X'], current:'X', mode:'pvp', status:{type:'draw',winner:null,line:null} };
    assert.deepEqual(getLegalMoves(state), []);
  });

  it('returns only empty cell indices for mid-game board', () => {
    const cells = ['X',null,'O', null,'X',null, null,null,'O'];
    const state = { cells, current:'X', mode:'pvp', status:{type:'ongoing',winner:null,line:null} };
    assert.deepEqual(getLegalMoves(state), [1,3,5,6,7]);
  });
});

// ---------------------------------------------------------------------------
// applyMove
// ---------------------------------------------------------------------------

describe('applyMove', () => {
  it('places X on first move and switches turn to O', () => {
    const state = createGame('pvp');
    const next = applyMove(state, 4);
    assert.equal(next.cells[4], 'X');
    assert.equal(next.current, 'O');
  });

  it('places O on second move and switches turn to X', () => {
    let state = createGame('pvp');
    state = applyMove(state, 0);
    state = applyMove(state, 4);
    assert.equal(state.cells[4], 'O');
    assert.equal(state.current, 'X');
  });

  it('does not mutate the original state', () => {
    const state = createGame('pvp');
    const original = state.cells.slice();
    applyMove(state, 0);
    assert.deepEqual(state.cells, original);
  });

  it('throws RangeError for index < 0', () => {
    assert.throws(() => applyMove(createGame('pvp'), -1), RangeError);
  });

  it('throws RangeError for index > 8', () => {
    assert.throws(() => applyMove(createGame('pvp'), 9), RangeError);
  });

  it('throws Error when cell is already occupied', () => {
    const state = applyMove(createGame('pvp'), 0);
    assert.throws(() => applyMove(state, 0), /occupied/i);
  });

  it('throws Error when applied to a terminal state', () => {
    let state = createGame('pvp');
    // Force a win: X plays 0,1,2; O plays 3,4
    state = applyMove(state, 0); // X
    state = applyMove(state, 3); // O
    state = applyMove(state, 1); // X
    state = applyMove(state, 4); // O
    state = applyMove(state, 2); // X wins
    assert.equal(state.status.type, 'win');
    assert.throws(() => applyMove(state, 5), /game is over/i);
  });

  it('detects win immediately after winning move', () => {
    let state = createGame('pvp');
    state = applyMove(state, 0); // X
    state = applyMove(state, 3); // O
    state = applyMove(state, 1); // X
    state = applyMove(state, 4); // O
    state = applyMove(state, 2); // X wins row 0
    assert.equal(state.status.type, 'win');
    assert.equal(state.status.winner, 'X');
    assert.deepEqual(state.status.line, [0,1,2]);
  });

  it('detects draw on last move', () => {
    // X O X / X O O / O X X — draw
    const moves = [0,1,2,4,3,5,7,6,8]; // alternating to reach draw
    // Manually build: X O X X O O O X X
    const sequence = [0, 4, 2, 1, 3, 5, 7, 6, 8];
    let state = createGame('pvp');
    for (const m of sequence) {
      if (state.status.type !== 'ongoing') break;
      state = applyMove(state, m);
    }
    assert.equal(state.status.type, 'draw');
  });
});
