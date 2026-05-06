/**
 * ReplayRecorder
 * Records game states frame-by-frame for replay playback
 */
class ReplayRecorder {
    constructor() {
        this.isRecording = false;
        this.frameHistory = [];
        this.inputHistory = [];
    }

    /**
     * Start recording
     */
    startRecording() {
        this.isRecording = true;
        this.frameHistory = [];
        this.inputHistory = [];
        console.log('Recording started');
    }

    /**
     * Record a frame
     */
    recordFrame(gameState, input = null) {
        if (this.isRecording) {
            // Store a deep copy of the state
            this.frameHistory.push(JSON.parse(JSON.stringify(gameState)));
            
            if (input) {
                this.inputHistory.push(input);
            }
        }
    }

    /**
     * Stop recording and finalize the replay
     */
    stopRecording(gameState) {
        this.isRecording = false;

        const replay = {
            id: this.generateId(),
            timestamp: Date.now(),
            gridWidth: gameState.gridWidth,
            gridHeight: gameState.gridHeight,
            frameHistory: this.frameHistory,
            inputHistory: this.inputHistory,
            finalScore: gameState.score,
            totalFrames: this.frameHistory.length
        };

        console.log(`Recording stopped. Total frames: ${this.frameHistory.length}`);
        return replay;
    }

    /**
     * Generate a unique ID for the replay
     */
    generateId() {
        return 'replay_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Clear recording
     */
    clear() {
        this.frameHistory = [];
        this.inputHistory = [];
        this.isRecording = false;
    }
}
