# SDLC Pipeline

A reusable, **agent-driven** Software Development Life Cycle pipeline.

**`/create-product`** runs the full **9-stage** flow: PRD → Architecture → UX → Epics & Stories → Implementation Plan → Implementation → Code Review → UAT → Deploy. It enforces upstream-ID traceability, gated handoffs at every stage, and real browser-driven UAT evidence (Playwright screenshots/video/trace) before the deployment gate flips to APPROVED.

The pipeline is **tool-neutral**: it's documented as Markdown skill files under `.agents/skills/`. Claude Code, GitHub Copilot, and any other agent that can read a file and follow instructions can run it. The slash commands in `.claude/commands/` are thin pointers to the corresponding skill.

---

## Repo layout (main)

```
.
├── .agents/
│   ├── skills/                  # 9-stage pipeline (per-stage SKILL.md + prompts + verifiers)
│   │   ├── stage-1-prd/         #   …
│   │   ├── stage-2-architecture/
│   │   ├── …
│   │   ├── stage-9-deploy/
│   │   ├── _shared/             # shared Python helpers (meta, hashes, anti-halluc)
│   │   └── STAGE-CONVENTIONS.md # shared rules (size classification, anti-halluc, traceability, etc.)
│   ├── schemas/                 # JSON schemas for the structured artifacts
│   ├── scripts/                 # helpers (e.g. detect_capabilities.py)
│   └── tests/                   # smoke + drift verifiers across all stages
├── .claude/
│   └── commands/                # slash commands: /create-product, /stage-N, …
├── .github/                     # CI: runs the smoke tests on every push
├── CLAUDE.md                    # project-level instructions for Claude Code
├── pyrightconfig.json           # editor type-checking config (Pyright/Pylance)
└── README.md                    # this file
```

Per-product implementation code (`src/`, `tests/`, `package.json`, etc.) is **not** committed to `main` — it lives on feature branches. `.gitignore` enforces this with leading-slash root patterns (`/src/`, `/tests/`, `/index.html`, etc.).

---

## Running the full pipeline

### In Claude Code

```
/create-product <one-line product or feature description>
```

Examples:

```
/create-product Build a focus-timer web app with daily streaks
/create-product Add a CSV export to the existing reports dashboard
```

The orchestrator auto-detects where to resume from (it walks `.agents/artifacts/stage-N/*_final.md`). It runs each stage in sequence, halts on any verifier failure, and stops after Stage 8. Stage 9 (deploy to GitHub Pages) is opt-in — invoke it manually with `/stage-9` once you've reviewed Stage 8 results.

### In GitHub Copilot or other agents

Pass the same description to:

```
Follow instructions in #file:.agents/skills/create-product/SKILL.md with: <description>
```

### Running a single stage

Each stage skill is independently invocable:

```
/stage-1 <feature description>      # PRD only
/stage-2                            # Architecture (after Stage 1)
…
/stage-8                            # UAT (after Stage 7 approves)
```

This is useful for re-running a specific stage after editing upstream artifacts.

### Stage outputs

| Stage | Skill | Final artifact |
|---|---|---|
| 1 — PRD | `stage-1-prd` | `stage-1/prd_final.md` |
| 2 — Architecture | `stage-2-architecture` | `stage-2/architecture_final.md` |
| 3 — UX | `stage-3-ux` | `stage-3/ux_final.md` |
| 4 — Epics & Stories | `stage-4-epics` | `stage-4/epics_stories_final.md` |
| 5 — Plan | `stage-5-plan` | `stage-5/plan_story_final.md` |
| 6 — Implementation | `stage-6-implement` | `src/`, build/test logs, `progress.json` |
| 7 — Code Review | `stage-7-review` | `stage-7/CODE_REVIEW.md` |
| 8 — UAT | `stage-8-uat` | `stage-8/uat-results_final.md` |
| 9 — Deploy | `stage-9-deploy` | `stage-9/deployment_config.json` (opt-in) |

All structured artifacts also carry a `meta` block with prompt versions and source hashes for **drift detection** — see "Drift, smoke, recovery" below.

---

## Verifying any artifact set

Every stage has a deterministic verifier you can run directly. There's also a smoke runner that runs them all:

```bash
python .agents/tests/run_verifiers.py        # run every stage's verifier against current artifacts
python .agents/tests/check_drift.py          # detect upstream/downstream drift via meta hashes
```

---

## Conventions you should know about

These are codified in [.agents/skills/STAGE-CONVENTIONS.md](./.agents/skills/STAGE-CONVENTIONS.md). The short version:

1. **Size classification** is set once in Stage 1 (`trivial` / `medium` / `large`) on `problem.json`, and every downstream stage inherits it. Never re-derive size from your own criteria.
2. **Anti-hallucination rule.** Every justification must trace to a specific upstream ID (`FR-N`, `NFR-N`, `GOAL-N`, `CON-N`, `S-N`, `T-N`). Generic virtue claims (`"chosen for simplicity"`, `"per industry best practices"`) are forbidden. Invented numbers must be tagged `[assumed: <value> — <one-line rationale>]`.
3. **Traceability chain.** Each stage's outputs cite the IDs produced by the previous stage. Stage 2 cites Stage 1's FRs/NFRs; Stage 4 cites Stage 3's flow IDs; Stage 5 cites Stage 4's story IDs; Stage 6 source files cite Stage 5's task IDs.
4. **Pipeline leakage rule.** Artifacts describe **the product**, never reference other pipeline stages. The PRD doesn't say "Stage 2 will refine this" — that's pipeline plumbing, not product information.
5. **Proportionality.** Trivial changes get trivial artifacts. A one-line bug fix doesn't need a traceability matrix.
6. **Section omission.** When a section has no signal (e.g. no genuine risks), omit it. Silence implies compliance.
7. **Scope limits.** Each stage is forbidden from doing the next stage's job — Stage 1 doesn't pick file names; Stage 7 doesn't modify code.

---

## Setting up a new project

1. **Create or branch a repo** that contains this `.agents/` tree (clone this repo, then strip `.agents/artifacts/` from your feature branch start).
2. **Add a one-line `CLAUDE.md`** at the repo root pointing the agent at the pipeline (`README.md` already does most of the work).
3. **Decide on a feature** and run the pipeline: `/create-product <description>`.
4. **Review each gate output** before letting the agent proceed. Verifiers do the structural work; you do the judgment.
5. **For Stage 9 (deploy)**, ensure your project actually builds to a static bundle. The current Stage 9 verifier supports GitHub Pages targets; server-side deploys (Postgres/Redis/server-rendered frameworks) are intentionally out of scope and trigger a halt with a recommendation.

---

## Branching convention

- **`main`** is **pipeline-only**. It carries `.agents/`, `.claude/`, `.github/`, `CLAUDE.md`, `pyrightconfig.json`, `README.md`. It does **not** carry `src/`, `tests/`, `index.html`, `package.json`, or any product-specific code.
- **Feature branches** carry the implementation. To track files that root `.gitignore` excludes (`/src/`, `/tests/`, `/index.html`), use `git add -f`.
- **`node_modules/`** and **`/dist/`** are ignored on every branch.

When you start a new project off this repo, branch from `main`, force-add the implementation files into your feature branch, and merge back into `main` only via the pipeline artifacts (not the product code).

---

## Drift, smoke, recovery

- **Smoke test** (`python .agents/tests/run_verifiers.py`) runs every stage's verifier against the current artifacts. Run it after touching anything under `.agents/skills/_shared/`, `.agents/schemas/`, or any `verify/` script.
- **Drift detection** (`python .agents/tests/check_drift.py`) compares each artifact's recorded `meta.source_hashes` against the current files. If you edit `goals.json` after `stories.json` has been generated, this will tell you `stories.json` is now stale.
- **Stage 6 recovery** (`python .agents/skills/stage-6-implement/recovery.py`) inspects a wedged Stage 6 run, lets you unstage a single task with `--unstage T-N --yes`, or archive `progress.json` with `--reset --yes` and start clean. The recovery tool never modifies `src/` — that's a deliberate split so a partial commit can be salvaged before reset.

---

## Out of scope

- **Server-side deployment.** Stage 9 covers GitHub Pages only. Apps that depend on Postgres/Redis/server-rendered frameworks halt at Stage 9 with a recommendation to use Vercel/Render/Azure/etc. Those deploy paths belong in your project's own CI/CD config (e.g. `.github/workflows/`), not in the SDLC pipeline.
- **Security review.** Stage 7 catches structural and contract violations and missing test coverage. It is **not** a substitute for a focused security review — use `/security-review` separately.

---

## Cross-tool note

`.agents/skills/` is consumed by Claude Code and GitHub Copilot today. Do not move or rename anything under `.agents/`. The `.claude/commands/` files are thin pointers — keep them that way. If you add a new agent, write a thin pointer in its conventions and re-use the SKILL.md files unchanged.

---

## License

See `LICENSE` if present. Otherwise, treat this repo as proprietary unless your organisation says otherwise.
