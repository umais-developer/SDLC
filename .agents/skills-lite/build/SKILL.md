---
name: lite-build-stage
description: |
  Stage B of the lite pipeline. Write code + tests directly from spec.md.
  Build and tests must pass. Every FR has a test that names its ID.
---

# Lite Stage B — Build

You are a senior dev. Read `spec.md`, write the code and tests, run build + test,
capture the log. No story decomposition, no per-task tracking.

## Inputs
- `.agents/artifacts-lite/spec.md` from Stage A.
- The current `src/` tree (modify in place; do not start from scratch unless `src/` is empty).

## Outputs
- Source files under `src/`.
- Tests next to the code they cover (`*.test.ts`, `*.spec.ts`, etc.).
- `.agents/artifacts-lite/build.log` — captured stdout/stderr of build + tests.

## Rules

1. **One commit-shaped unit of work.** Modify only what the spec needs. Don't
   refactor unrelated code.
2. **Every FR has a test that mentions its ID.** Either in the `describe`/`it`
   string or in a `/* FR-N */` header comment. The verifier greps for this.
3. **Use the project's existing build/test commands** if present
   (`package.json#scripts`, `pyproject.toml`, `Cargo.toml`, etc.). If the project
   is greenfield, scaffold the minimum needed.
4. **Anti-hallucination:** don't claim a test passes without seeing it in the log.

## Procedure

1. Read `spec.md`. List FR-IDs.
2. Decide on the smallest set of files that satisfies all FRs.
3. Write the code; write the tests alongside (each test mentions its FR-ID).
4. Run build + tests. If anything fails, fix the code (not the test) and re-run.
   Cap at 3 retry rounds.
5. Capture stdout+stderr to `.agents/artifacts-lite/build.log`. Append `EXIT=N` at
   the end with the actual exit code of the test run.

## Gate

```bash
python .agents/skills-lite/_verify.py build
```

Pass criteria:
- `build.log` exists and ends with `EXIT=0`.
- Every FR-ID from `spec.md` appears in at least one test file under `src/` or `tests/`.
- No empty or placeholder source files (TODO / FIXME / `throw new Error("not implemented")`).
