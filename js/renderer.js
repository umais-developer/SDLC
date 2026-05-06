/**
 * Renderer
 * Handles all canvas rendering for the game board, snake, food, and UI
 */
class Renderer {
    constructor() {
        this.colors = {
            background: '#f9f9f9',
            grid: '#cccccc',
            snake: '#4CAF50',
            snakeHead: '#2e7d32',
            food: '#FF5252',
            ghost: '#888888'
        };
    }

    /**
     * Set canvas for rendering
     */
    setCanvas(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            throw new Error(`Canvas with id ${canvasId} not found`);
        }
        
        // Ensure canvas has explicit dimensions (fix for 0 dimensions)
        if (this.canvas.width === 0) this.canvas.width = 400;
        if (this.canvas.height === 0) this.canvas.height = 400;
        
        this.ctx = this.canvas.getContext('2d');
        if (!this.ctx) {
            throw new Error(`Failed to get 2D context for canvas ${canvasId}`);
        }
        
        this.cellWidth = this.canvas.width / 20;
        this.cellHeight = this.canvas.height / 20;
        console.log(`Renderer initialized for canvas ${canvasId}:`, {
            canvasWidth: this.canvas.width,
            canvasHeight: this.canvas.height,
            cellWidth: this.cellWidth,
            cellHeight: this.cellHeight,
            context: this.ctx ? 'OK' : 'FAILED'
        });
    }

    /**
     * Draw the grid
     */
    drawGrid() {
        this.ctx.fillStyle = this.colors.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.ctx.strokeStyle = this.colors.grid;
        this.ctx.lineWidth = 1;

        // Draw vertical lines
        for (let i = 0; i <= 20; i++) {
            const x = i * this.cellWidth;
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }

        // Draw horizontal lines
        for (let j = 0; j <= 20; j++) {
            const y = j * this.cellHeight;
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }

    /**
     * Draw a single cell (for snake or food)
     */
    drawCell(x, y, color) {
        const cellX = x * this.cellWidth + 1;
        const cellY = y * this.cellHeight + 1;
        const cellSize = this.cellWidth - 2;

        this.ctx.fillStyle = color;
        this.ctx.fillRect(cellX, cellY, cellSize, cellSize);
    }

    /**
     * Draw the snake
     */
    drawSnake(snakeBody, isGhost = false) {
        const color = isGhost ? this.colors.ghost : this.colors.snake;
        const headColor = isGhost ? this.colors.ghost : this.colors.snakeHead;

        // Draw body segments
        snakeBody.forEach((segment, index) => {
            if (index === 0) {
                // Head
                this.drawCell(segment.x, segment.y, headColor);
            } else {
                // Body
                this.drawCell(segment.x, segment.y, color);
            }
        });
    }

    /**
     * Draw food
     */
    drawFood(foodPos) {
        if (foodPos) {
            this.drawCell(foodPos.x, foodPos.y, this.colors.food);
        }
    }

    /**
     * Draw a complete frame (grid, snake, food)
     */
    drawFrame(gameState, ghostState = null) {
        if (!this.ctx) {
            console.error('Canvas context not initialized');
            return;
        }
        
        // Draw grid
        this.drawGrid();

        // Draw ghost snake if provided
        if (ghostState && ghostState.snakeBody && ghostState.snakeBody.length > 0) {
            // Ghost snake with reduced opacity
            this.ctx.globalAlpha = 0.5;
            this.drawSnake(ghostState.snakeBody, true);
            this.ctx.globalAlpha = 1.0;
        }

        // Draw live snake
        if (gameState.snakeBody && gameState.snakeBody.length > 0) {
            this.drawSnake(gameState.snakeBody, false);
        }

        // Draw food
        this.drawFood(gameState.foodPos);
    }

    /**
     * Clear the canvas
     */
    clear() {
        this.ctx.fillStyle = this.colors.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
}
