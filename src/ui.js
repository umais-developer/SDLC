// ui.js — BoardRenderer and UIController
// All DOM manipulation lives here. No game logic.

'use strict';

const { createGame, getLegalMoves, applyMove } = require('./game.js');
const { easyBestMove, impossibleBestMove, scoreAllMoves } = require('./minimax.js');

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const OVERLAY_DISPLAY_MS = 150; // milliseconds the score overlay is visible before AI moves

// Copy — sourced from ux_final.md
const COPY = {
  turnX:      "X's turn",
  turnO:      "O's turn",
  winsX:      'X wins!',
  winsO:      'O wins!',
  draw:       "It's a draw!",
  newGame:    'New Game',
  modeHeading:'Choose a mode',
  pvp:        'Player vs Player',
  easy:       'Easy AI',
  impossible: 'Impossible AI',
};

// ---------------------------------------------------------------------------
// BoardRenderer
// ---------------------------------------------------------------------------

const BoardRenderer = {
  /** @type {HTMLElement[]} */
  cells: [],
  /** @type {HTMLElement} */
  statusEl: null,
  /** @type {HTMLElement} */
  turnEl: null,
  /** @type {HTMLElement} */
  newGameBtn: null,

  init() {
    this.cells = Array.from(document.querySelectorAll('.cell'));
    this.statusEl = document.getElementById('status');
    this.turnEl = document.getElementById('turn-indicator');
    this.newGameBtn = document.getElementById('new-game-btn');
  },

  /**
   * Render the full board from a GameState.
   * @param {import('./game').GameState} state
   */
  render(state) {
    const { cells, current, status } = state;

    // Cells
    this.cells.forEach((el, i) => {
      el.textContent = cells[i] || '';
      const isEmpty = cells[i] === null;
      const isOver  = status.type !== 'ongoing';

      el.setAttribute('aria-label', cells[i] ? `Cell ${i + 1}: ${cells[i]}` : `Cell ${i + 1}: empty`);
      el.setAttribute('aria-disabled', String(!isEmpty || isOver));
      el.classList.toggle('cell--filled', !isEmpty);
      el.classList.toggle('cell--inert', isOver || !isEmpty);
      el.style.cursor = (isEmpty && !isOver) ? 'pointer' : 'default';

      // Tab order: only empty playable cells in tab order
      el.setAttribute('tabindex', (isEmpty && !isOver) ? '0' : '-1');
    });

    // Winning line highlight
    this.cells.forEach(el => el.classList.remove('cell--win'));
    if (status.line) {
      status.line.forEach(i => this.cells[i].classList.add('cell--win'));
    }

    // Turn indicator / status banner
    if (status.type === 'ongoing') {
      this.turnEl.textContent = current === 'X' ? COPY.turnX : COPY.turnO;
      this.statusEl.textContent = '';
      this.statusEl.removeAttribute('aria-live');
      this.newGameBtn.hidden = true;
    } else {
      this.turnEl.textContent = '';
      const msg = status.winner === 'X' ? COPY.winsX
                : status.winner === 'O' ? COPY.winsO
                : COPY.draw;
      this.statusEl.textContent = msg;
      this.statusEl.setAttribute('aria-live', 'polite');
      this.newGameBtn.hidden = false;
    }
  },

  /**
   * Render minimax scores on open cells.
   * @param {Object.<number, number>} scores
   */
  renderScoreOverlay(scores) {
    this.cells.forEach((el, i) => {
      if (Object.prototype.hasOwnProperty.call(scores, i)) {
        const score = scores[i];
        const overlay = document.createElement('span');
        overlay.className = 'score-overlay';
        overlay.textContent = score;
        overlay.setAttribute('aria-label', `Minimax score: ${score}`);
        el.appendChild(overlay);
      }
    });
  },

  /** Remove all score overlay elements. */
  clearScoreOverlay() {
    this.cells.forEach(el => {
      el.querySelectorAll('.score-overlay').forEach(s => s.remove());
    });
  },
};

// ---------------------------------------------------------------------------
// UIController
// ---------------------------------------------------------------------------

const UIController = {
  /** @type {import('./game').GameState|null} */
  state: null,
  /** @type {string|null} */
  lastMode: null,

  init() {
    BoardRenderer.init();
    this._bindModeButtons();
    this._bindNewGame();
    this._showModeSelection();
  },

  _bindModeButtons() {
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        this.startGame(mode);
      });
    });
  },

  _bindNewGame() {
    document.getElementById('new-game-btn').addEventListener('click', () => {
      this._showModeSelection();
    });
  },

  /**
   * Show the mode selection screen; pre-select the last-used mode button.
   */
  _showModeSelection() {
    document.getElementById('mode-selection').hidden = false;
    document.getElementById('game-board').hidden = true;
    document.getElementById('status').textContent = '';
    document.getElementById('turn-indicator').textContent = '';

    // Pre-highlight last-used mode button
    document.querySelectorAll('.mode-btn').forEach(btn => {
      btn.classList.toggle('mode-btn--active', btn.dataset.mode === this.lastMode);
    });
  },

  /**
   * Start a new game in the given mode.
   * @param {'pvp'|'easy'|'impossible'} mode
   */
  startGame(mode) {
    this.lastMode = mode;
    this.state = createGame(mode);

    document.getElementById('mode-selection').hidden = true;
    document.getElementById('game-board').hidden = false;

    BoardRenderer.render(this.state);
    this._bindCells();

    // If Impossible AI goes first (O goes first — not applicable since X always goes first)
    // X is human; no AI turn needed at start.
  },

  _bindCells() {
    BoardRenderer.cells.forEach((el, i) => {
      // Remove old listeners by cloning
      const fresh = el.cloneNode(true);
      el.parentNode.replaceChild(fresh, el);
      BoardRenderer.cells[i] = fresh;

      fresh.addEventListener('click', () => this._handleCellActivation(i));
      fresh.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this._handleCellActivation(i);
        }
      });
    });
  },

  /**
   * Handle a human cell activation (click or keyboard).
   * @param {number} index
   */
  _handleCellActivation(index) {
    const { state } = this;
    if (!state) return;
    if (state.status.type !== 'ongoing') return;
    if (state.cells[index] !== null) return;
    // During AI turn, board is locked (cells are aria-disabled)
    if (this._aiTurnLocked) return;

    this.state = applyMove(state, index);
    BoardRenderer.render(this.state);

    if (this.state.status.type !== 'ongoing') return;

    const mode = this.state.mode;
    if (mode === 'easy') {
      this._runEasyAI();
    } else if (mode === 'impossible') {
      this._runImpossibleAI();
    }
    // pvp: no AI turn
  },

  _aiTurnLocked: false,

  _runEasyAI() {
    this._aiTurnLocked = true;
    // Easy AI moves instantly (no overlay)
    const move = easyBestMove(this.state);
    this.state = applyMove(this.state, move);
    BoardRenderer.render(this.state);
    this._bindCells();
    this._aiTurnLocked = false;
  },

  _runImpossibleAI() {
    this._aiTurnLocked = true;

    // 1. Compute and show score overlay
    const scores = scoreAllMoves(this.state);
    BoardRenderer.renderScoreOverlay(scores);

    // 2. After OVERLAY_DISPLAY_MS, commit the move and clear overlay
    setTimeout(() => {
      BoardRenderer.clearScoreOverlay();
      const move = impossibleBestMove(this.state);
      this.state = applyMove(this.state, move);
      BoardRenderer.render(this.state);
      this._bindCells();
      this._aiTurnLocked = false;
    }, OVERLAY_DISPLAY_MS);
  },
};

// ---------------------------------------------------------------------------
// Bootstrap
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  UIController.init();
});
