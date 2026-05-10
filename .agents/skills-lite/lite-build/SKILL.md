---
name: lite-build
description: |
  Three-stage SDLC: Spec -> Build -> Verify. No JSON ceremony, one markdown per stage,
  one combined verifier. Use this when the 9-stage pipeline would be overkill — small
  features, prototypes, focused enhancements, or anything where you want the result
  in 20 minutes instead of two hours.
---

# Lite Build — 3-Stage Orchestrator

You are an SDLC orchestrator running a deliberately compact pipeline. Three stages,
three artifacts, one verifier. No traceability matrix, no flow JSON, no drift checks.

## Invocation

- Claude Code: `/lite-build <feature or product description>`
- Other agents: read this file, pass the request as input.

## Output Layout

```
.agents/artifacts-lite/
├── spec.md       (Stage A)
├── build.log     (Stage B)
└── REVIEW.md     (Stage C)
```

Code goes under `src/` exactly like the 9-stage pipeline.

## Auto-Resume

Resume from the first missing artifact:

| Missing | Start at |
|---|---|
| `spec.md` | Stage A |
| any `src/**/*.test.*` | Stage B |
| `REVIEW.md` | Stage C |
| all present | done |

## Run Each Stage

For each stage from the resume point, follow that stage's SKILL.md exactly. The
stages are tool-neutral; each one names the prompts/files it needs.

- **Stage A — Spec:** `.agents/skills-lite/spec/SKILL.md`
- **Stage B — Build:** `.agents/skills-lite/build/SKILL.md`
- **Stage C — Verify:** `.agents/skills-lite/verify/SKILL.md`

After each stage, run the combined gate:

```bash
python .agents/skills-lite/_verify.py <stage>
```

`<stage>` is `spec`, `build`, or `verify`. Non-zero exit → halt with the verifier's
message; do not paper over a failure.

## Anti-Hallucination

Same rule as the full pipeline, in shorter form:
- Mark every default value with `[assumed: <value> — <one-line reason>]` in `spec.md`.
- Every test must reference at least one FR-ID from `spec.md` in its describe / it
  string or a comment header. The verifier enforces this.
- Don't claim build/test success without log evidence.

## Stage Contracts (summary)

- **Stage A** writes `.agents/artifacts-lite/spec.md` with: Problem (1 para), FRs
  (FR-1..FR-N, ≤10), Assumptions, Acceptance Criteria. No more sections.
- **Stage B** writes code under `src/` and a build log to
  `.agents/artifacts-lite/build.log`. Every FR has at least one test that mentions
  its ID. Build + test commands exit 0.
- **Stage C** writes `.agents/artifacts-lite/REVIEW.md` with: verdict (APPROVE or
  CHANGES_REQUIRED), one-line summary per FR (pass/fail), ≤3 findings, smoke-test
  evidence (HTTP 200 from `vite preview` or equivalent).

## What This Pipeline Does NOT Do

- No story decomposition, no UX flow JSON, no architecture doc, no per-component
  traceability table, no separate UAT stage, no Playwright by default.
- No JSON schemas, no meta blocks, no drift hash check.
- One review pass; no amendment loop.

If you find yourself wanting any of those, the work is too big for `lite-build` —
stop and use `/create-product` instead.
