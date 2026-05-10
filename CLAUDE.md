# SDLC Pipeline Project

This repo runs a 9-stage SDLC pipeline (PRD → Architecture → UX → Epics → Plan → Implement → Review → UAT → Deploy). Each stage is a skill under `.agents/skills/` with a SKILL.md (instructions) and `verify/` (deterministic Python gate).

## Running the pipeline

Use the slash commands in `.claude/commands/`:

- `/create-product <description>` — run all stages, auto-resuming from the first incomplete one
- `/stage-1` through `/stage-9` — run a single stage independently

Each command points to the corresponding `.agents/skills/<stage>/SKILL.md`. Read that file and follow its instructions exactly when invoked.

## Conventions

Before working on any stage, consult `.agents/skills/STAGE-CONVENTIONS.md` for:

- Size classification (`trivial` / `medium` / `large`) — read `size` from `.agents/artifacts/stage-1/problem.json`, never re-derive
- Anti-hallucination rule — every justification must trace to an upstream ID (`FR-N`, `NFR-N`, `GOAL-N`, story ID, etc.); generic virtue claims are prohibited
- Upstream traceability chain — Stage N+1 must cite IDs produced by Stage N
- Pipeline leakage rule — artifacts describe the product, never reference other pipeline stages
- Proportionality — documentation effort must match feature complexity; trivial changes get trivial artifacts
- Section omission — sections with no signal must be omitted (silence implies compliance)

## Artifact locations

- Stage outputs: `.agents/artifacts/stage-N/`
- Generated source code (Stage 6): `src/`
- Build output (Stage 6): `dist/`

## Diagnostics

- **Smoke test:** `python .agents/tests/run_verifiers.py` — runs every stage verifier against the current artifacts. Run after touching anything under `.agents/skills/_shared/`, `.agents/schemas/`, or any verify script.
- **Drift check:** `python .agents/tests/check_drift.py` — compares each artifact's recorded `meta.source_hashes` against the current files. Reports stale downstream artifacts after upstream edits.
- **Stage 6 recovery:** `python .agents/skills/stage-6-implement/recovery.py --status` — diagnose a wedged Stage 6 run; `--reset --yes` to archive `progress.json` and start fresh; `--unstage T-N --yes` to retry one task.

## Scope guardrails

Each stage has hard scope limits documented in section 9 of STAGE-CONVENTIONS.md. Do not let a stage take on work that belongs to another stage (e.g., Stage 1 PRD must not name files; Stage 7 review must not modify code).

## Out-of-scope for this pipeline

- **Server-side deployment.** Stage 9 covers GitHub Pages only. Apps that depend on Postgres, Redis, server-rendered frameworks, or any `*.csproj` / `pom.xml` runtime trigger a halt at Stage 9 with a recommendation to use Vercel / Render / Azure / etc. Those deploy paths are intentionally outside the orchestrator — they belong in your project's own CI/CD config (e.g. `.github/workflows/`), not in the SDLC pipeline.
- **Code review for security.** Stage 7 catches structural / contract violations and missing test coverage. It is not a substitute for a focused security review (use `/security-review` separately for that).

## Cross-tool note

`.agents/skills/` is also consumed by GitHub Copilot. Do not move or rename anything under `.agents/`. The `.claude/commands/` files are thin pointers — keep them that way.
