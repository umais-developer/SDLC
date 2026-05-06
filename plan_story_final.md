# Implementation Plan: Display Mode Selection Screen

**Status:** Final  
**Author:** Engineering Team  
**Date:** 2026-05-06  
**Story:** Story 1.1 — Display Mode Selection Screen  
**Related Epic:** Epic 1: Mode Selection & Game Initialization  
**Estimate:** S (Small — ~2 story points)

---

## Story
**As a** casual player, **I want** to see three clearly labeled mode options when the app loads **so that** I can choose how to play.

---

## Acceptance Criteria
- [ ] Application displays a main screen on load with no game board initially visible.
- [ ] Three mode buttons are displayed: "Player vs. Player", "Play Easy AI", "Play Impossible AI".
- [ ] Buttons are equally prominent, centered, and clearly labeled with text (no icons alone).
- [ ] Each button is at least 44×44 px and has high contrast (4.5:1 minimum) for accessibility.
- [ ] Keyboard navigation works: Tab key cycles through buttons; Enter key selects the focused button.
- [ ] Focus indicator is visible (at least 2px border/outline) on all buttons.
- [ ] Page title reads "Tic-Tac-Toe with AI" or similar in browser tab.

---

## Implementation Tasks

### Frontend

| ID | Task | Definition of Done | Depends On |
|----|------|--------------------|------------|
| FE-01 | Create index.html with semantic structure | HTML file exists with `<button>` elements (not `<div>`); contains proper `<head>` with title, `<body>` with mode selector container; no inline styles (use external stylesheet). | — |
| FE-02 | Implement three mode selector buttons in HTML | Three `<button>` elements with IDs: `btn-pvp`, `btn-easy-ai`, `btn-impossible-ai`; labels: "Player vs. Player", "Play Easy AI", "Play Impossible AI"; data attributes or event listeners attached. | FE-01 |
| FE-03 | Create responsive layout using CSS Grid or Flexbox | Mode selector div is centered on screen; three buttons arranged horizontally (desktop) or vertically (mobile); equal width buttons; responsive to viewport changes (media query at 768px breakpoint). | FE-01, FE-02 |
| FE-04 | Apply button styling for minimum 44×44 px touch targets | Each button is at least 44×44 px; padding applied to reach minimum size; no button is squeezed or too small on any screen size. | FE-03 |
| FE-05 | Implement focus styles with visible focus indicator | CSS `:focus-visible` pseudo-class applied; focus indicator is at least 2px border or outline; color contrast ≥ 4.5:1 against background (e.g., white outline on dark background). | FE-04 |
| FE-06 | Implement hover styles for desktop affordance | CSS `:hover` pseudo-class applied to buttons; background color changes slightly or shadow appears; `cursor: pointer` applied; mouse users see clear affordance. | FE-04 |
| FE-07 | Set page title and favicon | `<title>` element reads "Tic-Tac-Toe with AI" or similar; browser tab displays this title; favicon added (optional for MVP). | FE-01 |
| FE-08 | Hide game board and other UI initially | Game board (if present in HTML) is hidden via CSS `display: none` or similar; only mode selector is visible on page load; use JavaScript or CSS to manage visibility. | FE-01 |

### Testing

| ID | Task | Type | Definition of Done |
|----|------|------|--------------------|
| TEST-01 | Manual accessibility test: Keyboard navigation | Manual | Tab through all three buttons; focus indicator visible on each; Enter key selects button (tested in Chrome, Firefox). Result: Pass. |
| TEST-02 | Manual color contrast test | Manual | Use WebAIM Contrast Checker or Lighthouse to verify button text vs. background ≥ 4.5:1. Result: Pass. |
| TEST-03 | Cross-browser rendering test | Manual | Open index.html in Chrome, Firefox, Safari, Edge; verify buttons are visible, properly sized, and correctly labeled on each. Result: Pass on all. |
| TEST-04 | Responsive layout test | Manual | Resize browser window or use DevTools mobile emulation (375px, 768px, 1920px widths); buttons remain visible and at least 44×44 px at all sizes. Result: Pass. |
| TEST-05 | Touch target size validation | Automated/Manual | Use browser DevTools to measure button dimensions; confirm ≥ 44×44 px. Result: Pass. |
| TEST-06 | Page title verification | Manual | Open page in browser; confirm tab title reads "Tic-Tac-Toe with AI". Result: Pass. |
| TEST-07 | Button click response (integration stub) | Manual | Click each button; confirm click is detected and event listener is triggered (log to console if not yet connected to game logic). Result: Events fire. |

---

## Task Dependency Order

1. **FE-01** — Create index.html with basic semantic structure.
2. **FE-02** — Add three `<button>` elements with proper IDs and labels.
3. **FE-03** — Style layout using Flexbox/Grid and responsive breakpoints.
4. **FE-04** — Ensure touch targets are ≥ 44×44 px.
5. **FE-05** — Add focus indicator styling (`:focus-visible`).
6. **FE-06** — Add hover styles for desktop affordance.
7. **FE-07** — Set page title in `<head>`.
8. **FE-08** — Hide game board initially (CSS or JS visibility).
9. **TEST-01** → **TEST-07** — Run all manual and automated tests; document results.

---

## Risks & Unknowns

| Item | Type | Impact | Mitigation / Next Step |
|------|------|--------|------------------------|
| CSS Grid/Flexbox compatibility on older browsers (IE11) | Risk | Layout may break on IE11; buttons may not display correctly. | **Decision:** Target modern browsers only (Chrome, Firefox, Safari, Edge); IE11 support deferred to future release. Use CSS Grid or Flexbox without polyfills. |
| Focus indicator visibility on different OS/browser combinations | Unknown | Focus ring style may not be consistently visible across platforms. | **Mitigation:** Use `outline` property with high contrast color; test on Mac/Windows/Linux in Chrome/Firefox/Safari. If inconsistency found, switch to custom focus ring (border + box-shadow). |
| Button label clarity or user confusion about mode differences | Risk | Users may not understand the difference between Easy AI and Impossible AI from button text alone. | **Mitigation:** Label text is clear; defer detailed explanations (e.g., tooltips, help page) to v2. For MVP, button text is self-explanatory ("Easy AI" vs. "Impossible AI"). |
| Touch target size on very small screens (e.g., 320px width) | Risk | Three buttons may not fit horizontally; buttons may be squeezed below 44×44 px. | **Mitigation:** Stack buttons vertically on mobile (< 480px width) using responsive CSS. Buttons remain 44×44 px minimum on all screen sizes. |
| No styling framework (CSS or Tailwind) | Unknown | Manual CSS may be verbose or inconsistent. | **Decision:** Use vanilla CSS for MVP; if complexity grows, integrate Tailwind or CSS-in-JS in v2. For now, keep styles minimal and readable. |

---

## Out of Scope / Follow-up Items

- **Button tooltips or help text** — Explaining the difference between modes (deferred to v2).
- **Dark mode or theme switching** — Implement single light theme for MVP.
- **Localization or i18n** — English only for MVP.
- **Animation on button hover/click** — Keep transitions minimal; deferred to v2 if needed for UX polish.
- **Game board initialization logic** — Handled in Story 1.2; not part of this story.

---

## Open Questions

- **Q: Should the mode selector be a separate page/screen, or a persistent UI overlay that can be returned to?**  
  **A:** For MVP, mode selector is a separate screen (shown on load, hidden during gameplay). Returning to it is handled in Story 7.2 (rematch flow).

- **Q: Should there be a "Help" or "Rules" button on the mode selector?**  
  **A:** No, not for MVP. Button labels are self-explanatory. Help page deferred to v2.

- **Q: What if a button label is too long for the button width?**  
  **A:** Use responsive font sizes and padding; stack buttons vertically on small screens if needed. Test and adjust as necessary during TEST-04 (responsive layout test).

- **Q: Should buttons have any icons (e.g., "👥" for PvP, "🤖" for AI)?**  
  **A:** No icons alone; text labels are mandatory for clarity. Icons optional but not required for MVP.

---

## Definition of Done (Story-Level)

The story is complete when:

1. ✅ index.html file exists with valid semantic HTML.
2. ✅ Three mode buttons are visible and clearly labeled on page load.
3. ✅ All acceptance criteria are met and verified via manual tests (TEST-01 through TEST-07 pass).
4. ✅ Page renders correctly on desktop, tablet, and mobile screens.
5. ✅ Keyboard navigation works: Tab and Enter keys function as expected.
6. ✅ Focus indicators are visible and meet contrast requirements.
7. ✅ Page title is set and visible in browser tab.
8. ✅ Code is committed to the `main` or `develop` branch with clear commit message: "feat: Display mode selection screen (Story 1.1)".
9. ✅ No blocking bugs or accessibility issues (zero critical findings from manual tests).

---

## Notes for the Engineer

- **Start with HTML structure:** Use semantic HTML5 with `<button>` elements (not `<div>` with click handlers). This ensures keyboard accessibility by default.
- **CSS organization:** Keep styles in a single `styles.css` file for simplicity. Consider organizing by component (e.g., `.mode-selector`, `.btn-mode`) for future scalability.
- **Testing priority:** Focus on accessibility tests (keyboard, focus indicator, contrast) first; they're mandatory for this story and foundational for the entire app.
- **Browser testing:** If possible, test on actual devices or use browser emulation (Chrome DevTools, Firefox Responsive Design Mode). Real device testing catches rendering issues not visible in emulation.
- **Commit strategy:** Make atomic commits: one for HTML structure, one for CSS layout, one for accessibility styles. This makes code review easier.

---

## Related Stories & Follow-up

- **Story 1.2 — Initialize Game Board and Game State:** Builds on this story; handles game logic initialization after mode selection.
- **All other user stories:** Depend on a functioning mode selector; this is the entry point.

---

## Success Criteria for Code Review

- [ ] HTML is semantic and accessible (no `<div>` pretending to be buttons).
- [ ] CSS is responsive and tested on multiple screen sizes.
- [ ] All acceptance criteria are met and documented in test results.
- [ ] No accessibility violations (WCAG 2.1 AA minimum).
- [ ] Code is clean, readable, and well-commented where necessary.
- [ ] Commit message is clear and references the story (e.g., "feat(Story 1.1): Display mode selection screen").
