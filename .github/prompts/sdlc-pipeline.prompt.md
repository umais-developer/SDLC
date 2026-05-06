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
| 7.5 | uat-automated-testing | `uat-test-plan_final.md`, `uat-results_final.md` |
| 8 | deploy-application | _(live GitHub Pages URL)_ |

## Step 1 — Auto-Detect Resume Point

Before executing any stage, check for the existence of each artifact file in the workspace root **in order**:

1. `prd_final.md` missing → resume from **Stage 1**
2. `architecture_final.md` missing → resume from **Stage 2**
3. `ux_final.md` missing → resume from **Stage 3**
4. `epics_stories_final.md` missing → resume from **Stage 4**
5. `plan_story_final.md` missing → resume from **Stage 5**
6. Source code missing or incomplete → resume from **Stage 6** (implement)
7. `uat-results_final.md` missing → resume from **Stage 7.5** (UAT)
8. All above exist → proceed to **Stage 8** (deploy)

> Stage 8 (deploy) is always run last regardless of resume point — it never has a skip artifact.

After detecting the resume point, clearly announce:
> "Detected resume point: Stage N — [stage name]. Artifacts already present: [list]. Starting from: [stage name]."

Then proceed immediately — do not wait for user confirmation unless input is needed.

### Optional Deterministic Intent Expansion (Pre-Stage)

Before Stage 1 (or when requirements are ambiguous), you may run deterministic intent expansion to normalize input:

```bash
python3 .agents/scripts/intent_expansion.py --input Requirements.md --output .agents/tmp/intent_expanded.json
```

Use the generated JSON as supporting context for PRD/architecture/UX decisions. This is advisory and does not replace required artifacts.

## Step 2 — Execute Each Stage

Run every stage from the resume point through Stage 7 sequentially. Complete each stage fully and confirm the artifact is saved before moving to the next.

## Stage Verification Rules

After each stage, perform a verification check before proceeding:

1. **Artifact existence:** required output file exists in workspace root.
2. **Artifact integrity:** file is non-empty and contains expected top-level headings for that stage.
3. **Dependency coverage:** output reflects required upstream artifacts for that stage (when applicable).
4. **Decision logging:** if assumptions were required, they are explicitly documented.

Minimum verification targets by stage:
- Stage 1 (`prd_final.md`): includes Problem Statement, Goals & Success Metrics, Scope, Functional Requirements.
- Stage 2 (`architecture_final.md`): includes Component Design, Data Flow, Security & Privacy, Scalability.
- Stage 3 (`ux_final.md`): includes User Flows, States & Variations, Accessibility Considerations.
- Stage 4 (`epics_stories_final.md`): includes at least one epic, user stories with acceptance criteria, and Traceability Matrix mapping stories to PRD/Architecture/UX.
- Stage 5 (`plan_story_final.md`): includes acceptance criteria, actionable tasks, dependency order, testing tasks.
- Stage 6 (implementation): code compiles/runs where applicable and tests are present for implemented behavior.
- Stage 7 (review): includes severity-classified findings and explicit verdict.
- Stage 7.5 (UAT): generates `uat-test-plan_final.md` from acceptance criteria, executes all tests, and produces `uat-results_final.md` with pass/fail counts, fixed issues, deployment gate decision.
- Stage 8 (deploy): produces live application URL and deployment confirmation.

### Deterministic Verification Commands

Use these non-LLM checks before advancing stages:

```bash
# Stage 1
python3 .agents/scripts/deterministic_checks.py --stage stage1 --artifact prd_final.md

# Stage 2
python3 .agents/scripts/deterministic_checks.py --stage stage2 --artifact architecture_final.md

# Stage 3
python3 .agents/scripts/deterministic_checks.py --stage stage3 --artifact ux_final.md

# Stage 4
python3 .agents/scripts/deterministic_checks.py --stage stage4 --artifact epics_stories_final.md

# Stage 5
python3 .agents/scripts/deterministic_checks.py --stage stage5 --artifact plan_story_final.md
```

If deterministic checks fail, stop advancement and fix the artifact before continuing.

## Parallelization Policy

Use parallel execution only for **independent checks** inside a stage. Do not parallelize stages that produce required downstream artifacts.

- Keep stages **1 → 5** strictly sequential (each stage depends on prior artifacts).
- In implementation/review phases, parallelize only where outputs do not overwrite each other.
- Safe examples:
  - Run `lint` and `unit tests` in parallel after dependencies are installed.
  - Run static analysis and UI/manual test preparation in parallel, then merge findings into one report.
  - In deploy stage, run read-only preflight checks (static-host compatibility, `gh auth status`, workflow-file existence) in parallel.
- Never run write-heavy steps in parallel (file generation, code modification, branch/commit operations).

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

Before generating stories, ensure Stage 4 reads and synthesizes all available upstream artifacts:
- `prd_final.md` (product requirements and scope)
- `architecture_final.md` (technical constraints and non-functional requirements)
- `ux_final.md` (user flows, interactions, states, and accessibility expectations)

If any required upstream artifact is missing for Stage 4, stop and ask the user before proceeding.

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

When complete: output the full review report inline, then proceed to Stage 7.5 (Automated UAT).

---

### Stage 7.5 — Automated UAT Testing

After the review is complete, invoke the automated UAT agent to run comprehensive testing against all user story acceptance criteria:

Follow all instructions in the uat-automated-testing prompt:

[uat-automated-testing](.github/prompts/uat-automated-testing.prompt.md)

This stage generates **two persistent artifacts**:

**1. `uat-test-plan_final.md` (Phase 0)**
- Dynamically generated from `epics_stories_final.md`
- Contains all test cases derived from acceptance criteria
- Organized by epic and story
- Includes test ID, steps, and expected results
- Provides traceability matrix back to requirements

**2. `uat-results_final.md` (Phase 5)**
- Execution timestamp and summary stats
- Test results table for each epic
- Issues found and fixes applied
- Unresolved issues documented
- Deployment gate decision (APPROVED or BLOCKED)

**Execution Flow:**
1. Phase 0: Generate test plan from acceptance criteria → `uat-test-plan_final.md`
2. Phase 1-2: Execute all tests from generated plan (100% coverage)
3. Phase 3: Auto-fix any failures found
4. Phase 5: Generate results artifact → `uat-results_final.md`
5. Phase 6: Determine deployment gate status

**Deployment Criteria:**
- ✅ **Approved if:** All mandatory tests pass OR all issues auto-fixed and re-tested successfully
- ❌ **Blocked if:** Any critical tests fail and cannot be auto-fixed

If UAT **passes** (gate = APPROVED): proceed to Stage 8 (Deploy).

If UAT **fails** (gate = BLOCKED): 
1. Output the blocking issues from `uat-results_final.md`
2. Stop and ask developer to review
3. Developer fixes issues manually
4. Invoke UAT agent again to verify fixes

---

### UAT Gate — Verification Complete

After `uat-results_final.md` is generated and reviewed:
- If deployment gate = **APPROVED**: output "✅ UAT APPROVED — Deployment Cleared"
- If deployment gate = **BLOCKED**: output "❌ UAT BLOCKED — Manual fixes required" + list blocking issues, then stop
- Do **not** proceed to Stage 8 unless gate = APPROVED

---

### Stage 8 — Deploy Application

**Before doing anything else, determine whether the app is static-deployable to GitHub Pages.**

Check `architecture_final.md` (and the implemented source code) for any of the following signals:
- A Node.js / Express / Fastify / NestJS / any HTTP server process
- A database (PostgreSQL, MySQL, MongoDB, Redis, SQLite, etc.)
- Server-side rendering at request time (Next.js SSR, Remix, SvelteKit SSR, etc.)
- API routes or backend endpoints that run server-side code
- WebSockets or any persistent server connection
- Docker / container definitions
- Environment variables that reference server secrets (DB passwords, API keys used server-side)

**If any of the above are present** → GitHub Pages cannot host this app. Output:
> "⚠️ Stage 8 skipped — this app requires a server and cannot be deployed to GitHub Pages. To deploy, use a platform that supports server-side workloads (e.g. Vercel, Render, Railway, Fly.io). No deployment has been made."

Then skip to the Completion Summary, marking Stage 8 as ⏭️ Skipped.

**If the app is purely static** (React/Vue/Svelte/Astro/vanilla JS that builds to `dist/` with no server process) → proceed with deployment:

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
| 7 — Review | ✅ Complete | _(review report)_ |
| 7.5 — Automated UAT | ✅ Approved _or_ ❌ Blocked | `uat-test-plan_final.md`, `uat-results_final.md` |
| 8 — Deploy | ✅ Complete _or_ ⏭️ Skipped (server-side app) | _(live GitHub Pages URL, or skip reason)_ |

## Rules

- Never skip a stage unless its artifact already exists in the workspace.
- Never overwrite an existing artifact — if a `_final.md` already exists for a stage you're resuming from, read it and use it as context rather than regenerating it.
- For Stage 7.5: If `uat-test-plan_final.md` exists but `uat-results_final.md` does not, resume from Phase 1 (skip Phase 0 regeneration). If both exist, output final decision and proceed to Stage 8.
- If required input is missing at any stage (e.g., no feature description provided), stop and ask the user before proceeding.
- Stage 8 (deploy) requires `gh` CLI to be installed and authenticated (`gh auth login`). If it is not available, stop and print installation instructions before proceeding.
- Stage 8 never force-pushes and never deletes branches or commits.
