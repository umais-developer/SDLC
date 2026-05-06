// ============================================================================
// Tic-Tac-Toe with AI - Main Application Logic
// ============================================================================

/**
 * Game State Manager
 * Manages all game state and state transitions
 */
class GameState {
    constructor() {
        this.board = Array(9).fill(null); // null, 'X', or 'O'
        this.currentPlayer = 'X'; // 'X' (human) or 'O' (AI)
        this.gameMode = null; // 'pvp', 'easy', 'impossible'
        this.gameStatus = 'ongoing'; // 'ongoing', 'human_win', 'ai_win', 'draw'
        this.isAIThinking = false;
    }

    reset() {
        this.board = Array(9).fill(null);
        this.currentPlayer = 'X';
        this.gameStatus = 'ongoing';
        this.isAIThinking = false;
    }

    setMode(mode) {
        this.gameMode = mode;
        this.reset();
        if (mode === 'pvp') {
            this.currentPlayer = 'X'; // Player 1
        } else {
            this.currentPlayer = 'X'; // Human
        }
    }

    isTerminal() {
        return this.gameStatus !== 'ongoing';
    }

    getEmptyCells() {
        return this.board
            .map((cell, index) => (cell === null ? index : null))
            .filter(index => index !== null);
    }

    isBoardFull() {
        return this.board.every(cell => cell !== null);
    }
}

/**
 * UI Manager
 * Handles all UI updates and DOM manipulation
 */
class UIManager {
    constructor() {
        this.modeSelector = document.getElementById('mode-selector');
        this.gameScreen = document.getElementById('game-screen');
        this.board = document.getElementById('board');
        this.turnIndicator = document.getElementById('turn-indicator');
        this.gameStatus = document.getElementById('game-status');
        this.statusMessage = document.querySelector('.status-message');
        this.rematchButton = document.getElementById('btn-rematch');
    }

    showModeSelector() {
        this.modeSelector.classList.remove('hidden');
        this.gameScreen.classList.add('hidden');
    }

    showGameBoard() {
        this.modeSelector.classList.add('hidden');
        this.gameScreen.classList.remove('hidden');
    }

    updateBoard(board) {
        const cells = document.querySelectorAll('.cell');
        cells.forEach((cell, index) => {
            cell.classList.remove('x', 'o', 'filled');
            if (board[index] === 'X') {
                cell.classList.add('x', 'filled');
            } else if (board[index] === 'O') {
                cell.classList.add('o', 'filled');
            }
        });
    }

    updateTurnIndicator(gameState) {
        if (gameState.gameMode === 'pvp') {
            const player = gameState.currentPlayer === 'X' ? 1 : 2;
            this.turnIndicator.textContent = `Player ${player}'s turn`;
        } else {
            if (gameState.currentPlayer === 'X') {
                this.turnIndicator.textContent = 'Your turn';
            } else {
                this.turnIndicator.textContent = 'AI is thinking...';
            }
        }
    }

    showGameOver(gameState) {
        this.gameStatus.classList.remove('hidden');
        
        if (gameState.gameStatus === 'human_win') {
            this.statusMessage.textContent = 'You win! 🎉';
        } else if (gameState.gameStatus === 'ai_win') {
            this.statusMessage.textContent = 'AI wins! Well played.';
        } else if (gameState.gameStatus === 'draw') {
            this.statusMessage.textContent = 'Draw! Perfect play.';
        }

        this.board.classList.add('disabled');
        this.rematchButton.focus();
    }

    hideGameOver() {
        this.gameStatus.classList.add('hidden');
        this.board.classList.remove('disabled');
    }

    disableBoard() {
        this.board.classList.add('disabled');
    }

    enableBoard() {
        this.board.classList.remove('disabled');
    }
}

/**
 * Game Logic
 * Core game rules: win detection, draw detection, etc.
 */
class GameLogic {
    // Winning combinations (indices)
    static WINNING_COMBINATIONS = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
        [0, 4, 8], [2, 4, 6]              // Diagonals
    ];

    static checkWin(board, player) {
        return GameLogic.WINNING_COMBINATIONS.some(combo =>
            combo.every(index => board[index] === player)
        );
    }

    static checkDraw(board) {
        return board.every(cell => cell !== null) && !GameLogic.checkWin(board, 'X') && !GameLogic.checkWin(board, 'O');
    }

    static updateGameStatus(gameState) {
        if (GameLogic.checkWin(gameState.board, 'X')) {
            gameState.gameStatus = 'human_win';
        } else if (GameLogic.checkWin(gameState.board, 'O')) {
            gameState.gameStatus = 'ai_win';
        } else if (GameLogic.checkDraw(gameState.board)) {
            gameState.gameStatus = 'draw';
        } else {
            gameState.gameStatus = 'ongoing';
        }
    }

    static makeMove(gameState, cellIndex, player) {
        if (gameState.board[cellIndex] !== null) {
            return false; // Cell already occupied
        }

        gameState.board[cellIndex] = player;
        GameLogic.updateGameStatus(gameState);
        return true;
    }

    static switchPlayer(gameState) {
        gameState.currentPlayer = gameState.currentPlayer === 'X' ? 'O' : 'X';
    }
}

/**
 * Easy AI
 * Random legal move selection
 */
class EasyAI {
    static getMove(gameState) {
        const emptyCells = gameState.getEmptyCells();
        if (emptyCells.length === 0) return null;

        const randomIndex = Math.floor(Math.random() * emptyCells.length);
        return emptyCells[randomIndex];
    }
}

/**
 * Application Controller
 * Orchestrates game flow and integrates all components
 */
class GameController {
    constructor() {
        this.gameState = new GameState();
        this.uiManager = new UIManager();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Mode buttons
        document.getElementById('btn-pvp').addEventListener('click', () => this.startGame('pvp'));
        document.getElementById('btn-easy-ai').addEventListener('click', () => this.startGame('easy'));
        document.getElementById('btn-impossible-ai').addEventListener('click', () => this.startGame('impossible'));

        // Board cells
        document.querySelectorAll('.cell').forEach(cell => {
            cell.addEventListener('click', (e) => this.handleCellClick(e));
            cell.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleCellClick(e);
                }
            });
        });

        // Rematch button
        this.uiManager.rematchButton.addEventListener('click', () => this.reset());
    }

    startGame(mode) {
        this.gameState.setMode(mode);
        this.uiManager.showGameBoard();
        this.uiManager.hideGameOver();
        this.uiManager.updateBoard(this.gameState.board);
        this.uiManager.updateTurnIndicator(this.gameState);
    }

    handleCellClick(event) {
        const cell = event.currentTarget;
        const cellIndex = parseInt(cell.getAttribute('data-index'), 10);

        // Validate move
        if (this.gameState.isTerminal() || this.gameState.board[cellIndex] !== null || this.gameState.isAIThinking) {
            return;
        }

        // Human move
        const moveSuccess = GameLogic.makeMove(this.gameState, cellIndex, 'X');
        if (!moveSuccess) return;

        this.uiManager.updateBoard(this.gameState.board);

        // Check if game ended
        if (this.gameState.isTerminal()) {
            this.uiManager.showGameOver(this.gameState);
            return;
        }

        // AI move (if applicable)
        if (this.gameState.gameMode !== 'pvp') {
            this.executeAIMove();
        } else {
            // PvP: switch to Player 2
            GameLogic.switchPlayer(this.gameState);
            this.uiManager.updateTurnIndicator(this.gameState);
        }
    }

    executeAIMove() {
        this.gameState.isAIThinking = true;
        this.uiManager.disableBoard();
        this.uiManager.updateTurnIndicator(this.gameState);

        // Simulate thinking delay
        setTimeout(() => {
            let aiMove = null;

            if (this.gameState.gameMode === 'easy') {
                aiMove = EasyAI.getMove(this.gameState);
            } else if (this.gameState.gameMode === 'impossible') {
                // Minimax will be implemented in a later story
                aiMove = EasyAI.getMove(this.gameState); // Placeholder
            }

            if (aiMove !== null) {
                GameLogic.makeMove(this.gameState, aiMove, 'O');
                this.uiManager.updateBoard(this.gameState.board);

                if (this.gameState.isTerminal()) {
                    this.uiManager.showGameOver(this.gameState);
                } else {
                    GameLogic.switchPlayer(this.gameState);
                    this.uiManager.updateTurnIndicator(this.gameState);
                    this.uiManager.enableBoard();
                }
            }

            this.gameState.isAIThinking = false;
        }, 500); // 500ms thinking delay
    }

    reset() {
        this.gameState.reset();
        this.uiManager.updateBoard(this.gameState.board);
        this.uiManager.hideGameOver();
        this.uiManager.showModeSelector();
    }
}

// ============================================================================
// Application Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    const gameController = new GameController();
    // Game is ready; mode selector is displayed
});
