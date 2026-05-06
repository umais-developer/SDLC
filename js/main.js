/**
 * main.js
 * Application entry point - initializes the game on page load
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Snake with Replay System...');

    // Create global controller instance
    gameController = new GameController();

    // Initialize the controller
    gameController.initialize();

    // Show home screen
    gameController.showHome();

    console.log('Application initialized successfully');
});
