/**
 * GameController
 * Orchestrates all game components: engine, input, rendering, recording, replay
 */
class GameController {
    constructor() {
        // Initialize components
        this.stateManager = new StateManager();
        this.gameEngine = new GameEngine(this.stateManager);
        this.inputManager = new InputManager(this.gameEngine);
        this.renderer = new Renderer();
        this.replayRenderer = null;  // Will be initialized in initialize()
        this.replayRecorder = new ReplayRecorder();
        this.replayPlayer = new ReplayPlayer();

        // Game state
        this.isLiveGameActive = false;
        this.gameLoop = null;
        this.replayLoop = null;
        this.replayList = [];

        // Screen management
        this.currentScreen = 'home';
    }

    /**
     * Initialize the controller
     */
    initialize() {
        // Set up renderers
        this.renderer.setCanvas('gameCanvas');
        this.replayRenderer = new Renderer();
        this.replayRenderer.setCanvas('replayCanvas');
        
        // Set up event listeners
        this.setupEventListeners();

        console.log('GameController initialized');
    }

    /**
     * Set up UI event listeners
     */
    setupEventListeners() {
        // Home screen
        document.getElementById('playBtn').addEventListener('click', () => this.startLiveGame());
        document.getElementById('replayBtn').addEventListener('click', () => this.showReplayList());

        // Game screen
        // (No listeners needed; game runs via loop)

        // Game over screen
        document.getElementById('playAgainBtn').addEventListener('click', () => this.startLiveGame());
        document.getElementById('viewReplaysBtn').addEventListener('click', () => this.showReplayList());

        // Replay list screen
        document.getElementById('backToHomeBtn').addEventListener('click', () => this.showHome());

        // Replay screen
        document.getElementById('playReplayBtn').addEventListener('click', () => this.playSelectedReplay());
        document.getElementById('pauseReplayBtn').addEventListener('click', () => this.pauseReplay());
        document.getElementById('speedSelector').addEventListener('change', (e) => {
            this.replayPlayer.setSpeed(parseFloat(e.target.value));
        });
        document.getElementById('backToReplaysBtn').addEventListener('click', () => this.showReplayList());
    }

    /**
     * Show home screen
     */
    showHome() {
        this.setScreen('home');
    }

    /**
     * Start a live game
     */
    startLiveGame() {
        try {
            console.log('[startLiveGame] Starting new game...');
            this.gameEngine.initialize();
            console.log('[startLiveGame] GameEngine initialized');
            
            this.replayRecorder.clear();
            console.log('[startLiveGame] ReplayRecorder cleared');
            
            this.replayRecorder.startRecording();
            console.log('[startLiveGame] Recording started');
            
            this.isLiveGameActive = true;
            this.inputManager.clearBuffer();
            console.log('[startLiveGame] Game state: isLiveGameActive=true, input buffer cleared');

            this.setScreen('game');
            console.log('[startLiveGame] Game screen set');
            
            this.startGameLoop();
            console.log('[startLiveGame] Game loop started');
        } catch (error) {
            console.error('[startLiveGame] ERROR:', error);
            this.isLiveGameActive = false;
        }
    }

    /**
     * Start the game loop
     */
    startGameLoop() {
        const tickInterval = 100; // 10 ticks per second

        if (this.gameLoop) clearInterval(this.gameLoop);

        this.gameLoop = setInterval(() => {
            if (!this.isLiveGameActive) {
                return;
            }

            try {
                // Execute game tick
                this.gameEngine.tick();

                // Get the current state
                const gameState = this.gameEngine.getState();

                // Record frame
                this.replayRecorder.recordFrame(gameState);

                // Render frame
                const ghostState = this.replayPlayer.isPlaying ? this.replayPlayer.getCurrentFrameState() : null;
                
                // Update replay if playing
                if (this.replayPlayer.isPlaying) {
                    this.replayPlayer.update();
                }

                this.renderer.drawFrame(gameState, ghostState);

                // Update UI
                const scoreEl = document.getElementById('score');
                if (scoreEl) {
                    scoreEl.textContent = `Score: ${gameState.score}`;
                }

                // Check if game is over
                if (gameState.gameOver) {
                    console.log('Game Over detected. Final state:', gameState);
                    this.endLiveGame();
                }
            } catch (error) {
                console.error('Error in game loop:', error);
                this.isLiveGameActive = false;
                if (this.gameLoop) clearInterval(this.gameLoop);
            }
        }, tickInterval);
    }

    /**
     * End the live game
     */
    endLiveGame() {
        this.isLiveGameActive = false;
        if (this.gameLoop) clearInterval(this.gameLoop);

        const finalState = this.gameEngine.getState();
        const replay = this.replayRecorder.stopRecording(finalState);

        // Add to replay list
        this.replayList.push(replay);

        // Show game over screen
        this.showGameOver(finalState.score);
    }

    /**
     * Show game over screen
     */
    showGameOver(finalScore) {
        document.getElementById('finalScore').textContent = `Final Score: ${finalScore}`;
        this.setScreen('gameOver');
    }

    /**
     * Show replay list
     */
    showReplayList() {
        const listContainer = document.getElementById('replayListContainer');
        const emptyMessage = document.getElementById('emptyReplayMessage');
        const table = document.getElementById('replayTable');
        const tableBody = document.getElementById('replayTableBody');

        if (this.replayList.length === 0) {
            emptyMessage.style.display = 'block';
            table.style.display = 'none';
        } else {
            emptyMessage.style.display = 'none';
            table.style.display = 'table';
            tableBody.innerHTML = '';

            // Sort replays by most recent first
            const sortedReplays = [...this.replayList].reverse();

            sortedReplays.forEach((replay, index) => {
                const date = new Date(replay.timestamp);
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${replay.finalScore}</td>
                    <td>${date.toLocaleString()}</td>
                    <td><button class="btn btn-small" onclick="gameController.selectReplay('${replay.id}')">Play</button></td>
                `;
                tableBody.appendChild(row);
            });
        }

        this.setScreen('replayList');
    }

    /**
     * Select a replay to view
     */
    selectReplay(replayId) {
        const replay = this.replayList.find(r => r.id === replayId);
        if (replay) {
            this.replayPlayer.loadReplay(replay);
            document.getElementById('pauseReplayBtn').style.display = 'none';
            document.getElementById('playReplayBtn').style.display = 'inline';
            document.getElementById('speedSelector').value = '1';
            this.replayPlayer.setSpeed(1);
            this.setScreen('replay');
            this.startReplayLoop();
        }
    }

    /**
     * Play selected replay
     */
    playSelectedReplay() {
        if (this.replayPlayer.currentReplay) {
            this.replayPlayer.play();
            document.getElementById('playReplayBtn').style.display = 'none';
            document.getElementById('pauseReplayBtn').style.display = 'inline';
        }
    }

    /**
     * Pause replay
     */
    pauseReplay() {
        this.replayPlayer.pause();
        document.getElementById('pauseReplayBtn').style.display = 'none';
        document.getElementById('playReplayBtn').style.display = 'inline';
    }

    /**
     * Start the replay loop
     */
    startReplayLoop() {
        const tickInterval = 100; // 10 ticks per second (same as live game)

        if (this.replayLoop) clearInterval(this.replayLoop);

        this.replayLoop = setInterval(() => {
            if (this.replayPlayer.isPlaying) {
                const stillPlaying = this.replayPlayer.update();

                const frameState = this.replayPlayer.getCurrentFrameState();
                if (frameState) {
                    this.replayRenderer.drawFrame(frameState);
                }

                if (!stillPlaying) {
                    document.getElementById('replayStatus').textContent = 'Replay ended';
                    this.pauseReplay();
                }
            }
        }, tickInterval);
    }

    /**
     * Set current screen
     */
    setScreen(screenName) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });

        // Show selected screen
        const screenMap = {
            'home': 'homeScreen',
            'game': 'gameScreen',
            'gameOver': 'gameOverScreen',
            'replayList': 'replayListScreen',
            'replay': 'replayScreen'
        };

        if (screenMap[screenName]) {
            document.getElementById(screenMap[screenName]).classList.add('active');
        }

        this.currentScreen = screenName;
    }
}

// Global instance
let gameController;
