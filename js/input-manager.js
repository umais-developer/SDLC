/**
 * InputManager
 * Handles keyboard input, buffering, and directional reversal prevention
 */
class InputManager {
    constructor(gameEngine) {
        this.gameEngine = gameEngine;
        this.inputBuffer = [];
        this.maxBufferSize = 2;
        this.keyMap = {
            'ArrowUp': 'UP',
            'ArrowDown': 'DOWN',
            'ArrowLeft': 'LEFT',
            'ArrowRight': 'RIGHT'
        };
        this.setupListeners();
    }

    /**
     * Set up keyboard event listeners
     */
    setupListeners() {
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
    }

    /**
     * Handle keydown event
     */
    handleKeyDown(e) {
        const direction = this.keyMap[e.key];
        
        if (direction) {
            e.preventDefault();
            this.queueDirection(direction);
        }
    }

    /**
     * Queue a direction input
     */
    queueDirection(direction) {
        // Check if this direction is a reversal of the current direction
        const currentState = this.gameEngine.getState();
        const isReversal = this.gameEngine.isReversal(currentState.direction, direction);

        if (isReversal) {
            // Ignore reversal input
            return;
        }

        // Add to buffer if not already at max size
        if (this.inputBuffer.length < this.maxBufferSize) {
            this.inputBuffer.push(direction);
        } else {
            // Replace the oldest buffered input with the new one
            this.inputBuffer.shift();
            this.inputBuffer.push(direction);
        }

        // Update game engine with buffered direction
        if (this.inputBuffer.length > 0) {
            const nextDirection = this.inputBuffer[0];
            this.gameEngine.setDirection(nextDirection);
            this.inputBuffer.shift();
        }
    }

    /**
     * Get the next buffered direction
     */
    getBufferedDirection() {
        return this.inputBuffer.length > 0 ? this.inputBuffer[0] : null;
    }

    /**
     * Clear input buffer
     */
    clearBuffer() {
        this.inputBuffer = [];
    }
}
