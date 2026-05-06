/**
 * StateManager
 * Manages the current game state and serialization for replays
 */
class StateManager {
    constructor() {
        this.gameState = {
            snakeBody: [],
            foodPos: null,
            score: 0,
            speed: 1,
            direction: 'RIGHT',
            nextDirection: null,
            gameOver: false,
            frameCount: 0,
            gridWidth: 20,
            gridHeight: 20
        };
    }

    /**
     * Initialize a new game state
     */
    initializeNewGame() {
        this.gameState = {
            snakeBody: [
                { x: 10, y: 10 },  // head
                { x: 9, y: 10 },   // body segment 1
                { x: 8, y: 10 }    // tail
            ],
            foodPos: null,
            score: 0,
            speed: 1,
            direction: 'RIGHT',
            nextDirection: null,
            gameOver: false,
            frameCount: 0,
            gridWidth: 20,
            gridHeight: 20
        };
    }

    /**
     * Get the current game state
     */
    getState() {
        return JSON.parse(JSON.stringify(this.gameState));
    }

    /**
     * Update the game state
     */
    setState(newState) {
        this.gameState = { ...this.gameState, ...newState };
    }

    /**
     * Serialize game state for storage
     */
    serializeState() {
        return JSON.stringify(this.gameState);
    }

    /**
     * Deserialize game state from storage
     */
    deserializeState(serialized) {
        return JSON.parse(serialized);
    }
}
