/**
 * ReplayPlayer
 * Handles replay playback at variable speeds
 */
class ReplayPlayer {
    constructor() {
        this.currentReplay = null;
        this.currentFrameIndex = 0;
        this.isPlaying = false;
        this.playbackSpeed = 1;
        this.frameInterval = 100; // Base interval in ms (10 FPS)
        this.lastFrameTime = 0;
    }

    /**
     * Load a replay
     */
    loadReplay(replay) {
        this.currentReplay = replay;
        this.currentFrameIndex = 0;
        this.isPlaying = false;
        console.log(`Replay loaded. Total frames: ${replay.totalFrames}`);
    }

    /**
     * Start playback
     */
    play() {
        if (this.currentReplay && !this.isPlaying) {
            this.isPlaying = true;
            this.lastFrameTime = Date.now();
            console.log('Replay playback started');
        }
    }

    /**
     * Pause playback
     */
    pause() {
        this.isPlaying = false;
        console.log('Replay playback paused');
    }

    /**
     * Resume playback
     */
    resume() {
        if (this.currentReplay) {
            this.play();
        }
    }

    /**
     * Set playback speed
     */
    setSpeed(multiplier) {
        if ([0.5, 1, 2, 4].includes(multiplier)) {
            this.playbackSpeed = multiplier;
            console.log(`Playback speed set to ${multiplier}x`);
        }
    }

    /**
     * Get current frame state
     */
    getCurrentFrameState() {
        if (this.currentReplay && this.currentFrameIndex < this.currentReplay.frameHistory.length) {
            return this.currentReplay.frameHistory[this.currentFrameIndex];
        }
        return null;
    }

    /**
     * Update replay playback (call from game loop)
     */
    update() {
        if (!this.isPlaying || !this.currentReplay) {
            return;
        }

        const now = Date.now();
        const elapsed = now - this.lastFrameTime;
        const adjustedInterval = this.frameInterval / this.playbackSpeed;

        if (elapsed >= adjustedInterval) {
            this.currentFrameIndex++;
            this.lastFrameTime = now;

            // Check if replay has ended
            if (this.currentFrameIndex >= this.currentReplay.frameHistory.length) {
                this.pause();
                console.log('Replay ended');
                return false; // Replay finished
            }

            return true; // Replay is still playing
        }

        return true; // Replay is still playing
    }

    /**
     * Check if replay is finished
     */
    isFinished() {
        if (!this.currentReplay) return true;
        return this.currentFrameIndex >= this.currentReplay.frameHistory.length;
    }

    /**
     * Reset replay to beginning
     */
    restart() {
        this.currentFrameIndex = 0;
        this.isPlaying = false;
        this.lastFrameTime = 0;
    }

    /**
     * Clear replay
     */
    clear() {
        this.currentReplay = null;
        this.currentFrameIndex = 0;
        this.isPlaying = false;
    }
}
