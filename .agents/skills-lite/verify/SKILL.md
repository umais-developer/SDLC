---
name: lite-verify
description: |
  Stage C of the lite pipeline. Compare build output to spec.md, smoke-run the app,
  write REVIEW.md with verdict + per-FR pass/fail + at most 3 findings.
---

# Lite Stage C — Verify

You are a reviewer + QA. Compare the implementation to the spec, smoke-run the
app, and write a single REVIEW.md.

## Inputs
- `.agents/artifacts-lite/spec.md` and `.agents/artifacts-lite/build.log`.
- The current `src/` tree.

## Outputs
- `.agents/artifacts-lite/REVIEW.md`.
- Optional: `.agents/artifacts-lite/smoke.log` (curl/playwright/whatever you used).

## Procedure

1. **Re-run the test command** for fresh evidence (don't trust a stale log).
   Append to `build.log` if helpful.
2. **Smoke-run the app.** Start `dev` or `preview`. Hit the root URL with
   `curl -sI` (or open headless Playwright). Capture HTTP status to `smoke.log`.
   Skip this step only if the deliverable is a CLI / library with no app.
3. **For each FR**, write one line: `FR-N — PASS|FAIL — one-sentence why`. Cite
   the test file and the code file you checked.
4. **List up to 3 findings** if you spot real problems. No findings is the right
   answer when the spec is met. Generic praise is forbidden.
5. **Verdict**: `APPROVE` if every FR is PASS and no Critical/High findings.
   Otherwise `CHANGES_REQUIRED`.

## REVIEW.md template

```markdown
# Lite Review: <feature name>

**Verdict:** APPROVE | CHANGES_REQUIRED
**Build:** EXIT=0 (build.log)
**Smoke:** HTTP 200 at <url> (smoke.log)

## Per-FR Status
- **FR-1** — PASS — covered by `src/x.test.ts`, implemented in `src/x.ts:42`
- **FR-2** — PASS — ...

## Findings (max 3)
None. (or: Low/Medium/High/Critical findings with file:line and a one-line fix.)
```

## Gate

```bash
python .agents/skills-lite/_verify.py verify
```

Pass criteria:
- `REVIEW.md` exists, has a `Verdict:` line that says `APPROVE`.
- Every FR-ID from `spec.md` appears in `REVIEW.md` with PASS or FAIL.
- 0 Critical / High findings.
- `build.log` still ends with `EXIT=0`.

If verdict is `CHANGES_REQUIRED`: stop. The user fixes the code (or re-runs Stage B
with corrections) and re-invokes Stage C.
