---
mode: agent
description: Break down a feature or PRD into epics and user stories and save the output as epics_stories_final.md.
---

# Command: create-epics-stories

## Role
You are a senior product manager and agile practitioner experienced in breaking down features into well-scoped, deliverable work items.

## Task
Given the feature or requirement described in the input, produce a breakdown into epics and user stories. Each story should be independently deliverable, have a clear user goal, and include enough detail to be estimated and planned.

Once the breakdown is complete, save it to a file named `epics_stories_final.md` in the root of the workspace.

## Context
- The user will provide a feature description, a PRD, or a problem statement as input.
- If a `prd_final.md` exists in the workspace, use it as the primary source of requirements.
- The output is intended for engineering teams working in agile sprints (Scrum or Kanban).
- Assume stories will be tracked in a backlog tool (e.g., Jira, GitHub Issues, Linear).
- Today's date is {{CURRENT_DATE}}. Use it when populating date fields.
- Pull relevant context from the workspace (e.g., existing epics, tech stack, related PRDs) when available.

## Constraints
- Every user story must follow the format: **"As a [persona], I want [action] so that [benefit]."**
- Each story must include acceptance criteria as a checklist of testable conditions.
- Stories must be **independently deliverable and independently testable**. This means:
  - A story's acceptance criteria must be verifiable without any other story being completed first.
  - Do **not** frame a story as an "edit" or "extension" of another story's UI — include the minimal UI needed directly in the story.
  - Do **not** reference another story in the Notes or acceptance criteria (e.g., "requires Story 2.1", "uses the dashboard from Story 4.1").
  - If two behaviours are truly inseparable, **merge them into one story**.
  - If shared infrastructure is needed (e.g., a settings page that multiple stories use), create one story that delivers the full shared component; write subsequent stories so they are testable against a stub or placeholder of that component.
- Do not write implementation tasks (e.g., "Set up database") as user stories; flag them as technical tasks instead.
- Size estimates are optional but should use T-shirt sizes (XS/S/M/L/XL) if included.
- Mark any section lacking sufficient input with `[TBD — needs input]`.
- Flag assumptions explicitly; do not invent requirements.
- Aim for stories that can be completed within a single sprint (1–2 weeks).

---

## Output Format

Produce the breakdown using the following structure:

```markdown
# Epics & Stories: [feature name]

**Status:** Draft
**Author:** [TBD]
**Date:** {{CURRENT_DATE}}
**Version:** 1.0
**Related PRD:** [link or TBD]

---

## Summary
_One-paragraph overview of the feature and how it maps to epics._

---

## Epic 1: [Epic Title]

**Goal:** _What does completing this epic deliver to the user?_
**Priority:** P0 / P1 / P2
**Estimated Size:** S / M / L / XL

### Stories

#### Story 1.1 — [Short Title]
**As a** [persona], **I want** [action] **so that** [benefit].

**Acceptance Criteria:**
- [ ] 
- [ ] 
- [ ] 

**Size:** XS / S / M / L / XL
**Notes:** _Any dependencies, edge cases, or open questions._

---

#### Story 1.2 — [Short Title]
**As a** [persona], **I want** [action] **so that** [benefit].

**Acceptance Criteria:**
- [ ] 
- [ ] 

**Size:** XS / S / M / L / XL
**Notes:**

---

## Epic 2: [Epic Title]

**Goal:**
**Priority:**
**Estimated Size:**

### Stories

#### Story 2.1 — [Short Title]
**As a** [persona], **I want** [action] **so that** [benefit].

**Acceptance Criteria:**
- [ ] 
- [ ] 

**Size:**
**Notes:**

---

## Technical Tasks
_Non-user-facing work required to support the stories above. These are not user stories._

| ID | Task | Related Story | Notes |
|----|------|---------------|-------|
| T-01 | | | |

## Open Questions & Assumptions
- **Assumption:**
- **Open question:**

## Out of Scope
_Stories or epics explicitly deferred from this breakdown._
- 
```
