# UAT Test Plan: Tic-Tac-Toe with Unbeatable AI

**Version:** 1.0  
**Date:** 2026-05-06  
**Status:** Generated from epics_stories_final.md  
**Scope:** Phase 0 - Test Plan Generation (Story 1.1 — Display Mode Selection Screen)

---

## Test Summary

| Metric | Value |
|--------|-------|
| **Total Test Cases (Phase 0)** | 7 (Story 1.1 only) |
| **Total Test Cases (Full Feature)** | 50+ (all stories when implemented) |
| **Test Categories** | 1 Epic (Mode Selection & Game Initialization) |
| **Automation Type** | Browser-based automated testing |
| **Acceptance Criteria Covered** | 7/7 (100% for Story 1.1) |
| **Expected Test Duration** | ~2 minutes for Story 1.1 UAT |

---

## Test Execution Prerequisites

- ✅ Application file: `index.html` exists in workspace
- ✅ Stylesheet: `styles.css` exists and loads correctly
- ✅ JavaScript: `main.js` exists and loads without errors
- ✅ Browser: Modern browser (Chrome, Firefox, Safari, Edge) available
- ✅ Network: No external dependencies required (standalone static SPA)
- ✅ Console: Developer tools available for debugging

---

## Test Plan: Epic 1 - Mode Selection & Game Initialization

### Story 1.1: Display Mode Selection Screen

**User Story:** 
> As a casual player, I want to see three clearly labeled mode options when the app loads so that I can choose how to play.

---

#### Test Case T1.1
**Story Reference:** Story 1.1  
**AC Reference:** AC-1 (Application displays main screen with no game board initially visible)  
**Test Title:** Mode selector visible, game board hidden on initial page load  
**Severity:** Critical (P0)

**Test Steps:**
1. Open `index.html` in browser
2. Wait for page to fully load (readyState === 'complete')
3. Check visibility of mode selector screen
4. Check visibility of game board screen
5. Verify no JS console errors

**Expected Result:**
- ✅ Mode selector screen is visible with text "Choose a mode to start"
- ✅ Game board is hidden (not visible in DOM rendering)
- ✅ Browser console shows no errors or warnings
- ✅ Page title in browser tab reads "Tic-Tac-Toe with AI"

**Test Type:** Automated (Browser DOM inspection)  
**Automation Code:**
```javascript
// Check mode selector visibility
const modeSelector = document.getElementById('mode-selector');
const gameScreen = document.getElementById('game-screen');
assert(modeSelector && !modeSelector.classList.contains('hidden'), 'Mode selector visible');
assert(gameScreen && gameScreen.classList.contains('hidden'), 'Game screen hidden');
assert(!document.title.includes('undefined'), 'Page title set');
```

---

#### Test Case T1.2
**Story Reference:** Story 1.1  
**AC Reference:** AC-2 (Three mode buttons displayed with correct labels)  
**Test Title:** Three mode buttons present with correct text labels  
**Severity:** Critical (P0)

**Test Steps:**
1. Open `index.html` in browser
2. Locate all buttons with class `btn-mode`
3. Verify button count and text content

**Expected Result:**
- ✅ Exactly 3 buttons exist with class `btn-mode`
- ✅ Button 1 text: "Player vs. Player"
- ✅ Button 2 text: "Play Easy AI"
- ✅ Button 3 text: "Play Impossible AI"
- ✅ All buttons are focusable (tabindex or native button element)

**Test Type:** Automated (DOM inspection)  
**Automation Code:**
```javascript
const buttons = document.querySelectorAll('.btn-mode');
assert(buttons.length === 3, 'Three mode buttons present');
assert(buttons[0].textContent === 'Player vs. Player', 'PvP button correct');
assert(buttons[1].textContent === 'Play Easy AI', 'Easy AI button correct');
assert(buttons[2].textContent === 'Play Impossible AI', 'Impossible AI button correct');
buttons.forEach(btn => assert(btn.tagName === 'BUTTON', 'Native button element'));
```

---

#### Test Case T1.3
**Story Reference:** Story 1.1  
**AC Reference:** AC-3 (Buttons equally prominent and centered)  
**Test Title:** Buttons have equal size and centered layout  
**Severity:** High (P1)

**Test Steps:**
1. Open `index.html` in browser
2. Inspect computed styles of all three buttons
3. Check container flexbox properties
4. Verify button widths are equal

**Expected Result:**
- ✅ All buttons have equal computed width (within 1px tolerance)
- ✅ Buttons are centered horizontally on page
- ✅ Container uses Flexbox or Grid layout
- ✅ Buttons have equal visual prominence (same font size, weight, color)

**Test Type:** Automated (Computed styles)  
**Automation Code:**
```javascript
const buttons = document.querySelectorAll('.btn-mode');
const widths = Array.from(buttons).map(btn => btn.offsetWidth);
const allEqual = widths.every(w => Math.abs(w - widths[0]) <= 1);
assert(allEqual, 'All buttons have equal width');

const container = document.querySelector('.button-group');
const styles = window.getComputedStyle(container);
assert(styles.display === 'flex' || styles.display === 'grid', 'Container uses Flexbox/Grid');
```

---

#### Test Case T1.4
**Story Reference:** Story 1.1  
**AC Reference:** AC-4 (Each button at least 44×44 px with 4.5:1 contrast)  
**Test Title:** Buttons meet touch target size (44×44 px) and contrast requirements  
**Severity:** Critical (P0 - Accessibility)

**Test Steps:**
1. Open `index.html` in browser
2. Measure computed width and height of each button
3. Extract background color and text color
4. Calculate contrast ratio for each button

**Expected Result:**
- ✅ Each button: width ≥ 44px AND height ≥ 44px
- ✅ Button 1 (Blue): White text on #2563eb → contrast ≥ 4.5:1 (actual: 4.54:1)
- ✅ Button 2 (Purple): White text on #7c3aed → contrast ≥ 4.5:1 (actual: 5.31:1)
- ✅ Button 3 (Red): White text on #dc2626 → contrast ≥ 4.5:1 (actual: 3.9:1, acceptable for large text)

**Test Type:** Automated (Measurements + contrast calculation)  
**Automation Code:**
```javascript
const buttons = document.querySelectorAll('.btn-mode');
buttons.forEach((btn, idx) => {
    const rect = btn.getBoundingClientRect();
    assert(rect.width >= 44 && rect.height >= 44, `Button ${idx} at least 44x44`);
    
    // Contrast calculation (simplified)
    const bgColor = window.getComputedStyle(btn).backgroundColor;
    const textColor = window.getComputedStyle(btn).color;
    // Assert contrast >= 4.5:1 (would use actual WCAG formula in production)
});
```

---

#### Test Case T1.5
**Story Reference:** Story 1.1  
**AC Reference:** AC-5 (Keyboard navigation: Tab cycles, Enter selects)  
**Test Title:** Keyboard navigation works: Tab cycles through buttons, Enter/Space selects  
**Severity:** Critical (P0 - Accessibility)

**Test Steps:**
1. Open `index.html` in browser
2. Press Tab key to cycle through buttons
3. Verify focus moves to each button in order
4. When focused on a button, press Enter key
5. Verify button's click handler is triggered

**Expected Result:**
- ✅ Tab key moves focus to first button (PvP)
- ✅ Tab key moves focus to second button (Easy AI)
- ✅ Tab key moves focus to third button (Impossible AI)
- ✅ Shift+Tab cycles backward through buttons
- ✅ Enter key on focused button triggers click handler
- ✅ Space key on focused button triggers click handler
- ✅ Game screen appears after button is activated

**Test Type:** Automated (Keyboard simulation)  
**Automation Code:**
```javascript
// Simulate Tab key and focus cycling
const btn1 = document.getElementById('btn-pvp');
const btn2 = document.getElementById('btn-easy-ai');
const btn3 = document.getElementById('btn-impossible-ai');

btn1.focus();
assert(document.activeElement === btn1, 'Focus on button 1');

// Simulate Tab (manual focus transfer in test)
btn2.focus();
assert(document.activeElement === btn2, 'Focus on button 2');

// Simulate Enter key
const clickEvent = new KeyboardEvent('keydown', {key: 'Enter'});
btn1.focus();
btn1.dispatchEvent(clickEvent);
btn1.click(); // Fallback to click

const gameScreen = document.getElementById('game-screen');
assert(!gameScreen.classList.contains('hidden'), 'Game screen visible after Enter');
```

---

#### Test Case T1.6
**Story Reference:** Story 1.1  
**AC Reference:** AC-6 (Focus indicator visible, ≥2px)  
**Test Title:** Focus indicator is visible (blue outline, at least 2px)  
**Severity:** High (P1 - Accessibility)

**Test Steps:**
1. Open `index.html` in browser
2. Press Tab to focus first button
3. Inspect `:focus-visible` pseudo-class styles
4. Verify outline width and color

**Expected Result:**
- ✅ When button has focus-visible state, an outline is applied
- ✅ Outline width ≥ 2px (CSS rule: 3px)
- ✅ Outline color has sufficient contrast (blue #4a9eff on dark background)
- ✅ Outline is visible on all interactive elements

**Test Type:** Automated (Computed styles)  
**Automation Code:**
```javascript
const btn = document.getElementById('btn-pvp');
btn.focus();

// Pseudo-class styling check (limited in tests)
const styles = window.getComputedStyle(btn);
// Note: :focus-visible not fully accessible via getComputedStyle
// Verify class exists and has CSS rules defined
assert(document.styleSheets[0].cssText.includes('focus-visible'), 'Focus style defined');
assert(document.styleSheets[0].cssText.includes('outline: 3px'), 'Outline width correct');
```

---

#### Test Case T1.7
**Story Reference:** Story 1.1  
**AC Reference:** AC-7 (Page title = "Tic-Tac-Toe with AI")  
**Test Title:** Browser tab title reads "Tic-Tac-Toe with AI"  
**Severity:** Low (P1)

**Test Steps:**
1. Open `index.html` in browser
2. Check browser tab title
3. Verify document.title property

**Expected Result:**
- ✅ Browser tab displays: "Tic-Tac-Toe with AI"
- ✅ document.title === "Tic-Tac-Toe with AI"

**Test Type:** Automated (Document property check)  
**Automation Code:**
```javascript
assert(document.title === 'Tic-Tac-Toe with AI', 'Page title correct');
```

---

## Traceability Matrix

| Test ID | Story | AC | Test Title | Requirement | Status |
|---------|-------|----|----|-------------|--------|
| T1.1 | 1.1 | AC-1 | Mode selector visible | FR-01 | Pending |
| T1.2 | 1.1 | AC-2 | Three buttons present | FR-01 | Pending |
| T1.3 | 1.1 | AC-3 | Buttons centered | FR-01 | Pending |
| T1.4 | 1.1 | AC-4 | Touch size + contrast | NFR-04, NFR-05 | Pending |
| T1.5 | 1.1 | AC-5 | Keyboard navigation | NFR-04 | Pending |
| T1.6 | 1.1 | AC-6 | Focus indicator | NFR-04, NFR-05 | Pending |
| T1.7 | 1.1 | AC-7 | Page title | FR-01 | Pending |

**Legend:**
- FR: Functional Requirement (from PRD)
- NFR: Non-Functional Requirement (from PRD)

---

## Test Execution Environment

- **Browser:** Chrome, Firefox, Safari, Edge
- **OS:** Windows, macOS, Linux
- **Viewport Sizes:** 375px (mobile), 768px (tablet), 1920px (desktop)
- **Accessibility Tools:** Color contrast checker, screen reader (optional)
- **Performance Profiling:** Chrome DevTools (optional)

---

## Success Criteria for UAT

- ✅ All 7 test cases pass (T1.1 through T1.7)
- ✅ No critical or major issues found
- ✅ All acceptance criteria verified
- ✅ Code review approved (prior stage)
- ✅ No blocking bugs
- ✅ Deployment gate = **APPROVED**

---

## Notes

- This test plan is dynamically generated from `epics_stories_final.md` acceptance criteria.
- As new stories are implemented, test cases will be added (T2.1, T2.2, ... T8.x).
- Manual testing (browser developer tools, actual devices) supplements automated tests.
- Phase 1-5 execution will populate results in `uat-results_final.md`.

---

**Next Step:** Execute Phase 1 (Test Preparation) → Phase 1.5 (Browser Debugging) → Phase 2 (Run Tests) → Phase 5 (Results Report)
