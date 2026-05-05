---
mode: agent
description: Run the full SDLC pipeline (PRD → Architecture → UX → Epics/Stories → Plan → Implement → Review), automatically detecting completed stages and resuming from the correct point.
---

# Command: sdlc-pipeline

## Role
You are an AI SDLC orchestrator. You run the full software development lifecycle pipeline for the described feature, automatically detecting which stages have already been completed and resuming from the right point.

## Pipeline Stages

| # | Stage | Artifact Produced |
|---|-------|-------------------|
| 1 | create-prd | `prd_final.md` |
| 2 | create-architecture | `architecture_final.md` |
| 3 | create-ux | `ux_final.md` |
| 4 | create-epics-stories | `epics_stories_final.md` |
| 5 | plan-story | `plan_story_final.md` |
| 6 | implement-story | _(source code files)_ |
| 7 | review-implementation | _(review report output)_ |
| 8 | deploy-application | _(live GitHub Pages URL)_ |

## Step 1 — Auto-Detect Resume Point

Before executing any stage, check for the existence of each artifact file in the workspace root **in order**:

1. `prd_final.md` missing → resume from **Stage 1**
2. `architecture_final.md` missing → resume from **Stage 2**
3. `ux_final.md` missing → resume from **Stage 3**
4. `epics_stories_final.md` missing → resume from **Stage 4**
5. `plan_story_final.md` missing → resume from **Stage 5**
6. All artifacts above exist → resume from **Stage 6** (implement)

> Stage 8 (deploy) is always run last regardless of resume point — it never has a skip artifact.

After detecting the resume point, clearly announce:
> "Detected resume point: Stage N — [stage name]. Artifacts already present: [list]. Starting from: [stage name]."

Then proceed immediately — do not wait for user confirmation unless input is needed.

## Step 2 — Execute Each Stage

Run every stage from the resume point through Stage 7 sequentially. Complete each stage fully and confirm the artifact is saved before moving to the next.

---

### Stage 1 — Create PRD

Follow all instructions in the create-prd prompt:

[create-prd](.github/prompts/create-prd.prompt.md)

When complete: confirm `prd_final.md` is saved, then proceed to Stage 2.

---

### Stage 2 — Create Architecture

Follow all instructions in the create-architecture prompt:

[create-architecture](.github/prompts/create-architecture.prompt.md)

When complete: confirm `architecture_final.md` is saved, then proceed to Stage 3.

---

### Stage 3 — Create UX

Follow all instructions in the create-ux prompt:

[create-ux](.github/prompts/create-ux.prompt.md)

When complete: confirm `ux_final.md` is saved, then proceed to Stage 4.

---

### Stage 4 — Create Epics & Stories

Follow all instructions in the create-epics-stories prompt:

[create-epics-stories](.github/prompts/create-epics-stories.prompt.md)

When complete: confirm `epics_stories_final.md` is saved, then proceed to Stage 5.

---

### Stage 5 — Plan Story

Follow all instructions in the plan-story prompt:

[plan-story](.github/prompts/plan-story.prompt.md)

When complete: confirm `plan_story_final.md` is saved, then proceed to Stage 6.

---

### Stage 6 — Implement Story

Follow all instructions in the implement-story prompt:

[implement-story](.github/prompts/implement-story.prompt.md)

When complete: confirm all source files are written, then proceed to Stage 7.

---

### Stage 7 — Review Implementation

Follow all instructions in the review-implementation prompt:

[review-implementation](.github/prompts/review-implementation.prompt.md)

When complete: output the full review report inline, then **stop and present the UAT gate below — do not proceed to Stage 8 automatically**.

---

### UAT Gate — User Sign-Off Required

After the review report is displayed, ask the user:

> **UAT Sign-Off Required**
> The review report is shown above. Please confirm:
>
> - Does the implementation meet the acceptance criteria?
> - Are you satisfied with the review findings?
>
> **Type `yes` to approve and trigger deployment, or `no` to cancel.**

- If the user responds **`yes`** (or any clear affirmative) → proceed to Stage 8.
- If the user responds **`no`** (or any clear negative) → stop the pipeline and output:
  > "Deployment cancelled. Address the review findings and re-run the pipeline to deploy."
- Do **not** proceed to Stage 8 for any ambiguous or non-committal response — re-prompt once, then stop if still unclear.

---

### Stage 8 — Deploy Application

Follow all instructions in the deploy-application prompt:

[deploy-application](.github/prompts/deploy-application.prompt.md)

This stage:
1. Patches `vite.config.ts` with the correct GitHub Pages `base` path.
2. Creates the GitHub Actions workflow file (`.github/workflows/deploy.yml`) if it does not exist — the workflow triggers on `deploy/**` branches.
3. Initialises git, ensures a `.gitignore` excludes `node_modules/`, `dist/`, build artefacts, and env files, then creates a `deploy/<app-name>` branch and commits only source files.
4. Creates the GitHub remote repo if it does not already exist.
5. Pushes the `deploy/<app-name>` branch to GitHub, which triggers the Actions workflow directly.
6. Polls for workflow completion and returns the live URL.

> `main` is never touched — each app lives on its own `deploy/<app-name>` branch.

When complete: output the live URL and the Stage 8 summary block.

---

## Completion Summary

After all stages are done, output a summary table:

| Stage | Status | Artifact / Output |
|-------|--------|-------------------|
| 1 — PRD | ✅ Complete | `prd_final.md` |
| 2 — Architecture | ✅ Complete | `architecture_final.md` |
| 3 — UX | ✅ Complete | `ux_final.md` |
| 4 — Epics & Stories | ✅ Complete | `epics_stories_final.md` |
| 5 — Plan | ✅ Complete | `plan_story_final.md` |
| 6 — Implementation | ✅ Complete | _(source files)_ |
| 7 — Review | ✅ Complete | _(inline report)_ |
| UAT Gate | ✅ Approved | _(user sign-off)_ |
| 8 — Deploy | ✅ Complete | _(live GitHub Pages URL)_ |

## Rules

- Never skip a stage unless its artifact already exists in the workspace.
- Never overwrite an existing artifact — if a `_final.md` already exists for a stage you're resuming from, read it and use it as context rather than regenerating it.
- If required input is missing at any stage (e.g., no feature description provided), stop and ask the user before proceeding.
- Stage 8 (deploy) requires `gh` CLI to be installed and authenticated (`gh auth login`). If it is not available, stop and print installation instructions before proceeding.
- Stage 8 never force-pushes and never deletes branches or commits.
