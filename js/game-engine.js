/**
 * GameEngine
 * Core game logic: movement, collisions, food, scoring, speed
 */
class GameEngine {
    constructor(stateManager) {
        this.stateManager = stateManager;
    }

    /**
     * Initialize the game
     */
    initialize() {
        this.stateManager.initializeNewGame();
        
        // Spawn initial food
        this.spawnFood();
        
        const state = this.getState();
        console.log('[GameEngine.initialize] Game initialized with state:');
        console.log('  Snake body:', state.snakeBody);
        console.log('  Food position:', state.foodPos);
        console.log('  Score:', state.score);
        console.log('  GameOver:', state.gameOver);
        console.log('  Direction:', state.direction);
        console.log('  NextDirection:', state.nextDirection);
    }

    /**
     * Get current game state
     */
    getState() {
        return this.stateManager.getState();
    }

    /**
     * Update state
     */
    updateState(updates) {
        this.stateManager.setState(updates);
    }

    /**
     * Spawn food at a random empty cell
     */
    spawnFood() {
        let foodPos;
        let retries = 0;
        const maxRetries = 10;
        const state = this.getState();

        do {
            foodPos = {
                x: Math.floor(Math.random() * state.gridWidth),
                y: Math.floor(Math.random() * state.gridHeight)
            };
            retries++;
        } while (this.isOccupiedBySnake(foodPos) && retries < maxRetries);

        this.updateState({ foodPos });
        console.log(`[SpawnFood] Food spawned at (${foodPos.x},${foodPos.y}) after ${retries} attempts. Snake body:`, state.snakeBody);
        return foodPos;
    }

    /**
     * Check if a position is occupied by the snake
     */
    isOccupiedBySnake(pos) {
        const state = this.getState();
        return state.snakeBody.some(segment => segment.x === pos.x && segment.y === pos.y);
    }

    /**
     * Move the snake in the current direction
     */
    moveSnake() {
        const state = this.getState();
        const head = state.snakeBody[0];
        const direction = state.direction;

        let newHead = { ...head };
        switch (direction) {
            case 'UP':
                newHead.y--;
                break;
            case 'DOWN':
                newHead.y++;
                break;
            case 'LEFT':
                newHead.x--;
                break;
            case 'RIGHT':
                newHead.x++;
                break;
        }

        return newHead;
    }

    /**
     * Check for collisions (wall or self)
     */
    checkCollision(head) {
        const state = this.getState();
        
        // Check wall collision
        if (head.x < 0 || head.x >= state.gridWidth ||
            head.y < 0 || head.y >= state.gridHeight) {
            console.log(`[Collision] Wall hit at (${head.x}, ${head.y}). Grid bounds: 0-${state.gridWidth-1}`);
            return 'wall';
        }

        // Check self-collision (excluding tail, which will move away)
        for (let i = 0; i < state.snakeBody.length - 1; i++) {
            if (head.x === state.snakeBody[i].x && 
                head.y === state.snakeBody[i].y) {
                console.log(`[Collision] Self-collision at (${head.x}, ${head.y}) with segment ${i}`);
                return 'self';
            }
        }

        return null;
    }

    /**
     * Check if food was eaten
     */
    isFoodEaten(head) {
        const state = this.getState();
        return head.x === state.foodPos.x && head.y === state.foodPos.y;
    }

    /**
     * Execute one game tick
     */
    tick() {
        let state = this.getState();
        
        if (state.gameOver) {
            console.log(`[Tick ${state.frameCount}] Game already over, skipping tick`);
            return;
        }

        // Apply next direction if it's not a reversal
        if (state.nextDirection) {
            const isReversal = this.isReversal(state.direction, state.nextDirection);
            if (!isReversal) {
                this.updateState({ direction: state.nextDirection, nextDirection: null });
            } else {
                this.updateState({ nextDirection: null });
            }
            state = this.getState();
        }

        // Move snake
        const newHead = this.moveSnake();
        console.log(`[Tick ${state.frameCount}] Snake moving from (${state.snakeBody[0].x},${state.snakeBody[0].y}) to (${newHead.x},${newHead.y}) - Direction: ${state.direction}`);

        // Check collision
        const collision = this.checkCollision(newHead);
        if (collision) {
            this.updateState({ gameOver: true });
            console.log(`[Tick ${state.frameCount}] COLLISION DETECTED: ${collision} at (${newHead.x},${newHead.y})`);
            return;
        }

        // Update snake body
        const newBody = [newHead, ...state.snakeBody];

        // Check if food was eaten
        if (this.isFoodEaten(newHead)) {
            // Snake grows (don't remove tail)
            this.updateState({ 
                snakeBody: newBody,
                score: state.score + 1,
                speed: this.calculateSpeed(newBody.length),
                frameCount: state.frameCount + 1
            });
            this.spawnFood();
            console.log(`[Tick ${state.frameCount}] FOOD EATEN! Score: ${state.score + 1}, Snake length: ${newBody.length}`);
            this.updateState({ frameCount: state.frameCount + 1 });
        } else {
            // Snake moves (remove tail)
            newBody.pop();
            this.updateState({ snakeBody: newBody, frameCount: state.frameCount + 1 });
        }
    }

    /**
     * Check if a direction is a reversal of the current direction
     */
    isReversal(currentDir, nextDir) {
        const reversals = {
            'UP': 'DOWN',
            'DOWN': 'UP',
            'LEFT': 'RIGHT',
            'RIGHT': 'LEFT'
        };
        return reversals[currentDir] === nextDir;
    }

    /**
     * Calculate speed based on snake length
     */
    calculateSpeed(snakeLength) {
        // Speed increases by 5% for every 5 segments of growth
        return 1 + Math.floor((snakeLength - 3) / 5) * 0.05;
    }

    /**
     * Set the next direction
     */
    setDirection(direction) {
        if (['UP', 'DOWN', 'LEFT', 'RIGHT'].includes(direction)) {
            this.updateState({ nextDirection: direction });
        }
    }

    /**
     * Reset game state
     */
    reset() {
        this.initialize();
    }
}
