---
name: "Implementation - Entry Points & Build (Sub-agent)"
description: "Sub-agent for creating HTML, CSS, and build configuration"
---

# Implementation Task: Entry Points & Build Verification

**Subagent Role**: Create HTML/CSS entry points and verify build
- Group D: index.html, style.css, main.ts, build verification

## Context

- **Tech Stack**: {{tech_stack_json}}
- **Components Contract**: {{components_json}}
- **Tasks to Execute**: T-33, T-34, T-35 from {{tasks_json}}
- **Dependencies**: Group A, B, C must be completed first

## Acceptance Criteria

✅ Entry point files created:
- `src/index.html` - HTML template with canvas and controls
- `src/style.css` - Styling for game UI
- `src/main.ts` - Module initialization

✅ HTML includes:
- Canvas element (id="gameCanvas")
- Score display (id="score")
- Speed display (id="speed")
- New Game button (id="newGameBtn")
- Pause/Resume button (id="pauseResumeBtn")
- Stop button (id="stopBtn")
- View Replays button (id="viewReplaysBtn")
- Replay list container (id="replayList")
- Instructions sidebar
- Proper semantic markup

✅ CSS styling:
- Dark theme (black background, white text)
- Grid layout (game area + controls + instructions)
- Responsive design
- Button hover/active states
- Canvas centered and properly sized
- Accessibility (focus styles, ARIA labels)

✅ main.ts:
- Imports UIController
- Handles DOMContentLoaded
- Initializes game controller
- Exports for testing

✅ Build succeeds:
- Command: `npm run build` exits 0
- Produces `dist/` with all assets
- No TypeScript errors
- No unresolved imports

## Requirements (from PRD Goals)

**GOAL-1: Game UI**
- All controls present and functional
- Instructions visible to new players
- Score and speed visible during gameplay

**GOAL-2: Styling**
- Professional appearance
- Dark theme for screen fatigue reduction
- Clear visual hierarchy

## Implementation Strategy

1. **Create index.html**
   - Semantic HTML structure
   - All required input elements with correct IDs
   - Links to CSS and JS entry point

2. **Create style.css**
   - CSS Grid for layout
   - Dark theme variables
   - Button styling with hover/active states
   - Canvas styling (pixelated rendering)
   - Accessibility (focus outlines)

3. **Create main.ts**
   - Import CSS
   - Import UIController
   - Initialize on DOM ready
   - Export for test modules

4. **Build verification**
   - Run `npm run build`
   - Verify all files in dist/
   - Check for no errors

## Testing Approach

- Manual: Open dist/index.html in browser, verify rendering
- Automated: Verify HTML structure (canvas, buttons present)
- Automated: Verify CSS loads and applies
- Automated: Verify build output exists

## Definition of Done

1. ✅ HTML file created with all required elements
2. ✅ CSS file created with full styling
3. ✅ main.ts created and initializes game
4. ✅ Build command succeeds: `npm run build`
5. ✅ dist/ directory contains index.html, CSS bundle, JS bundle
6. ✅ No TypeScript errors
7. ✅ Ready for Stage 7 (UAT testing)
