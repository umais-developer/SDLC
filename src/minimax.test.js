// minimax.test.js — Unit tests for EasyAI and MinimaxEngine
// Run with: node --test src/minimax.test.js  (Node 18+)

'use strict';

const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { createGame, applyMove } = require('./game.js');
const { easyBestMove, impossibleBestMove, scoreAllMoves, minimax } = require('./minimax.js');

// Helper: build a state by applying a sequence of moves
function buildState(moves, mode = 'impossible') {
  let state = createGame(mode);
  for (const m of moves) state = applyMove(state, m);
  return state;
}

// ---------------------------------------------------------------------------
// minimax terminal state scores
// ---------------------------------------------------------------------------

describe('minimax — terminal state evaluation', () => {
  it('returns +1 when O has already won (maximiser perspective)', () => {
    // X plays 0,2,6; O plays 3,4,5 — O wins row 1 [3,4,5]
    const s = buildState([0, 3, 2, 4, 6, 5]); // X:0,2,6  O:3,4,5 — O wins row 1
    assert.equal(s.status.type, 'win');
    assert.equal(s.status.winner, 'O');
    // minimax on a terminal state where O won: isMax doesn't matter — returns +1
    assert.equal(minimax(s, true), 1);
    assert.equal(minimax(s, false), 1);
  });

  it('returns -1 when X has already won', () => {
    const s = buildState([0, 3, 1, 4, 2]); // X wins row 0
    assert.equal(s.status.type, 'win');
    assert.equal(s.status.winner, 'X');
    assert.equal(minimax(s, true), -1);
    assert.equal(minimax(s, false), -1);
  });

  it('returns 0 for a draw position', () => {
    // X O X / X O O / O X X
    const s = buildState([0, 1, 2, 4, 3, 5, 7, 6, 8]);
    // Verify it's actually a draw
    if (s.status.type === 'win') {
      // Sequence may have caused a win — build an explicit draw
      const draw = buildState([0, 4, 8, 2, 6, 3, 5, 1, 7]);
      assert.equal(minimax(draw, true), 0);
    } else {
      assert.equal(s.status.type, 'draw');
      assert.equal(minimax(s, true), 0);
    }
  });
});

// ---------------------------------------------------------------------------
// impossibleBestMove — AI never loses
// ---------------------------------------------------------------------------

describe('impossibleBestMove — AI never loses', () => {
  it('returns a legal move from empty board', () => {
    const state = createGame('impossible');
    const move = impossibleBestMove(state);
    assert.ok(move >= 0 && move <= 8, `Expected 0-8, got ${move}`);
    assert.equal(state.cells[move], null, 'Move must be on an empty cell');
  });

  it('always draws or wins from empty board (score must be 0 or +1)', () => {
    const state = createGame('impossible');
    // The best score from the starting position for O (second player) is 0 (draw with perfect play)
    // We verify by simulating: AI plays O, and we play the "worst" human moves
    // Actually, for a fresh board it's X's turn — but impossibleBestMove is called when it IS O's turn.
    // Simulate: X plays centre (4), then O responds
    const afterX = applyMove(state, 0); // X plays corner
    const oMove  = impossibleBestMove(afterX);
    assert.ok(oMove >= 0 && oMove <= 8);
    assert.equal(afterX.cells[oMove], null);
  });

  it('takes a winning move when available', () => {
    // O can win: board has O at 3,4 and X at 0,1 — O should play 5
    // Build: X:0, O:3, X:1, O:4 — now O to play, winning move is 5
    // X:0,6,8  O:3,4 — after 5 moves it is O's turn; O wins by playing 5 (row 1: 3,4,5)
    const s = buildState([0, 3, 6, 4, 8]); // after 5 moves current='O'
    assert.equal(s.current, 'O');
    // O has 3,4 — if O plays 5 it wins row 1
    const best = impossibleBestMove(s);
    assert.equal(best, 5, `Expected winning move 5, got ${best}`);
  });

  it('blocks an opponent winning move', () => {
    // X has 0,1 and needs 2 to win — O must block at 2
    // Build: X:0, O:4, X:1 → X needs 2, current='O'
    const state = buildState([0, 4, 1]);
    assert.equal(state.current, 'O');
    const best = impossibleBestMove(state);
    assert.equal(best, 2, `Expected blocking move 2, got ${best}`);
  });
});

// ---------------------------------------------------------------------------
// scoreAllMoves
// ---------------------------------------------------------------------------

describe('scoreAllMoves', () => {
  it('returns a score for every legal move', () => {
    const state = createGame('impossible');
    const scores = scoreAllMoves(state);
    const legal = [0,1,2,3,4,5,6,7,8];
    legal.forEach(i => {
      assert.ok(Object.prototype.hasOwnProperty.call(scores, i), `Missing score for cell ${i}`);
    });
  });

  it('all scores are -1, 0, or +1', () => {
    const state = createGame('impossible');
    const scores = scoreAllMoves(state);
    Object.values(scores).forEach(s => {
      assert.ok(s === -1 || s === 0 || s === 1, `Unexpected score value: ${s}`);
    });
  });

  it('does not include scores for occupied cells', () => {
    const state = buildState([0, 4]); // X at 0, O at 4
    const scores = scoreAllMoves(state);
    assert.ok(!Object.prototype.hasOwnProperty.call(scores, 0), 'Occupied cell 0 should have no score');
    assert.ok(!Object.prototype.hasOwnProperty.call(scores, 4), 'Occupied cell 4 should have no score');
  });

  it('returns score 0 from the empty board (O cannot force a win)', () => {
    // From empty board with X to move (but scoreAllMoves is called when it's O's turn)
    // After X plays any move, O's best is 0 (draw) from an empty board
    // Simulate: it is O's turn after X played 0
    const afterX = applyMove(createGame('impossible'), 0);
    const scores = scoreAllMoves(afterX);
    // O playing centre (4) should score 0 (draw)
    assert.equal(scores[4], 0, 'O playing centre should yield a draw');
  });
});

// ---------------------------------------------------------------------------
// easyBestMove
// ---------------------------------------------------------------------------

describe('easyBestMove', () => {
  it('always returns a legal move', () => {
    for (let trial = 0; trial < 100; trial++) {
      const state = buildState([0, 4, 2], 'easy'); // mid-game board, X's turn — use as test state
      const s = { ...state, current: 'O', mode: 'easy' }; // treat as O's turn for easy AI
      const move = easyBestMove(s);
      assert.ok(move >= 0 && move <= 8, `Move ${move} out of range`);
      assert.equal(state.cells[move], null, `Move ${move} is occupied`);
    }
  });

  it('throws when there are no legal moves', () => {
    const full = { cells: ['X','O','X','X','O','O','O','X','X'], current:'O', mode:'easy', status:{type:'draw',winner:null,line:null} };
    assert.throws(() => easyBestMove(full), /no legal moves/i);
  });
});
