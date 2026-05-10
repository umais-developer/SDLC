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

## Scope guardrails

Each stage has hard scope limits documented in section 8 of STAGE-CONVENTIONS.md. Do not let a stage take on work that belongs to another stage (e.g., Stage 1 PRD must not name files; Stage 7 review must not modify code).

## Cross-tool note

`.agents/skills/` is also consumed by GitHub Copilot. Do not move or rename anything under `.agents/`. The `.claude/commands/` files are thin pointers — keep them that way.
