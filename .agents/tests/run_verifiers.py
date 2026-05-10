#!/usr/bin/env python3
"""
Smoke test: run every SDLC stage verifier against the artifacts in
`.agents/artifacts/`.

Purpose
-------
After changing any verify script, the shared `_shared/` modules, or any schema
under `.agents/schemas/`, run this from the repo root:

    python .agents/tests/run_verifiers.py

The script invokes Stages 1–5 + 7 verifiers using the current real artifacts as
fixtures. Stages 6 and 8 require runtime artifacts (build logs, Playwright
captures) and are skipped here — provide those separately if you want full
coverage.

Exit code
---------
0 if every invoked verifier exits 0; 1 otherwise. Failures are printed with the
verifier's stderr so you can fix or amend.

Adding new fixtures
-------------------
Drop a JSON or Markdown file under `.agents/artifacts/stage-N/` matching the
path the SKILL.md prescribes for that stage. The runner picks them up
automatically.
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS = REPO_ROOT / ".agents" / "artifacts"
SKILLS = REPO_ROOT / ".agents" / "skills"


def run(label: str, args: list[str]) -> tuple[bool, str]:
    """Run a verifier; return (passed, output).

    Forces UTF-8 stdio in the child so the verifier's emoji-laced print
    statements survive Windows cp1252 stdout.
    """
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        result = subprocess.run(
            [sys.executable, *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            env=env,
        )
        passed = result.returncode == 0
        output = (result.stdout + result.stderr).strip()
        return passed, output
    except subprocess.TimeoutExpired:
        return False, f"{label}: timed out after 60s"
    except Exception as e:
        return False, f"{label}: runner error: {e}"


def header(text: str) -> None:
    print(f"\n=== {text} ===")


def detect_size() -> str:
    """Read size from stage-1 problem.json, default to medium."""
    problem = ARTIFACTS / "stage-1" / "problem.json"
    if not problem.exists():
        return "medium"
    import json
    try:
        with open(problem) as f:
            data = json.load(f)
        size = data.get("size")
        if isinstance(size, str) and size.strip():
            return size.strip().lower()
    except Exception:
        pass
    return "medium"


def main() -> int:
    if not ARTIFACTS.exists():
        print(f"No artifacts directory at {ARTIFACTS} — nothing to verify.", file=sys.stderr)
        return 1

    size = detect_size()
    is_large = size == "large"
    is_trivial = size == "trivial"

    print(f"Running verifiers against artifacts (size={size})")

    failures: list[tuple[str, str]] = []

    # --- Stage 1 ---
    header("Stage 1 — PRD")
    goals = ARTIFACTS / "stage-1" / "goals.json"
    if goals.exists():
        passed, out = run(
            "stage-1",
            [str(SKILLS / "stage-1-prd" / "verify" / "prd_structure.py"), str(goals)],
        )
        print(out or "(no output)")
        if not passed:
            failures.append(("Stage 1", out))
    else:
        print("skipped — goals.json missing")

    # --- Stage 2 ---
    header("Stage 2 — Architecture")
    components = ARTIFACTS / "stage-2" / "components.json"
    if is_trivial:
        passed, out = run(
            "stage-2-trivial",
            [str(SKILLS / "stage-2-architecture" / "verify" / "architecture_completeness.py"), "--trivial"],
        )
    elif components.exists() and goals.exists():
        passed, out = run(
            "stage-2",
            [
                str(SKILLS / "stage-2-architecture" / "verify" / "architecture_completeness.py"),
                str(components),
                str(goals),
            ],
        )
    else:
        passed, out = True, "skipped — components.json or goals.json missing"
    print(out or "(no output)")
    if not passed:
        failures.append(("Stage 2", out))

    # --- Stage 3 ---
    header("Stage 3 — UX")
    flows = ARTIFACTS / "stage-3" / "flows.json"
    ux_final = ARTIFACTS / "stage-3" / "ux_final.md"
    if is_trivial and ux_final.exists():
        passed, out = run(
            "stage-3-trivial",
            [str(SKILLS / "stage-3-ux" / "verify" / "flows_structure.py"), "--trivial", str(ux_final)],
        )
    elif flows.exists() and goals.exists():
        passed, out = run(
            "stage-3",
            [str(SKILLS / "stage-3-ux" / "verify" / "flows_structure.py"), str(flows), str(goals)],
        )
    else:
        passed, out = True, "skipped — flows.json or goals.json missing"
    print(out or "(no output)")
    if not passed:
        failures.append(("Stage 3", out))

    # --- Stage 4 ---
    header("Stage 4 — Epics & Stories")
    stories = ARTIFACTS / "stage-4" / "stories.json"
    epics_final = ARTIFACTS / "stage-4" / "epics_stories_final.md"
    s4_args = [str(SKILLS / "stage-4-epics" / "verify" / "story_traceability.py")]
    if is_trivial and epics_final.exists():
        s4_args += ["--trivial", str(epics_final)]
    elif stories.exists() and goals.exists():
        s4_args += [str(stories), str(goals)]
        if flows.exists():
            s4_args.append(str(flows))
        if components.exists():
            s4_args.append(str(components))
        if is_large:
            s4_args += ["--require-deps", "--require-matrix"]
    else:
        s4_args = []
    if s4_args:
        passed, out = run("stage-4", s4_args)
    else:
        passed, out = True, "skipped — stories.json or goals.json missing"
    print(out or "(no output)")
    if not passed:
        failures.append(("Stage 4", out))

    # --- Stage 5 ---
    header("Stage 5 — Plan")
    tasks = ARTIFACTS / "stage-5" / "tasks.json"
    plan_final = ARTIFACTS / "stage-5" / "plan_story_final.md"
    s5_args = [str(SKILLS / "stage-5-plan" / "verify" / "tasks_structure.py")]
    if is_trivial and tasks.exists() and plan_final.exists():
        s5_args += ["--trivial", str(tasks), str(plan_final), str(goals), str(components)]
    elif tasks.exists() and stories.exists() and goals.exists() and components.exists():
        s5_args += [str(tasks), str(stories), str(goals), str(components)]
        if is_large:
            s5_args += ["--require-deps", "--require-order"]
    else:
        s5_args = []
    if s5_args:
        passed, out = run("stage-5", s5_args)
    else:
        passed, out = True, "skipped — required Stage 5 inputs missing"
    print(out or "(no output)")
    if not passed:
        failures.append(("Stage 5", out))

    # --- Stage 7 (requires Stage 6 fully verified) ---
    header("Stage 7 — Code Review")
    review = ARTIFACTS / "stage-7" / "review.json"
    progress = ARTIFACTS / "stage-6" / "progress.json"
    stage_6_complete = False
    if progress.exists() and tasks.exists():
        import json
        try:
            with open(progress) as f:
                pdata = json.load(f)
            with open(tasks) as f:
                tdata = json.load(f)
            verified = set(pdata.get("tasks_verified", []) or [])
            task_ids = {t.get("id") for t in tdata.get("tasks", []) if t.get("id")}
            stage_6_complete = bool(task_ids) and verified.issuperset(task_ids)
        except Exception:
            stage_6_complete = False

    if not review.exists():
        print("skipped — review.json missing")
    elif not stage_6_complete:
        print("skipped — Stage 6 not fully verified (run /stage-6 to completion before /stage-7)")
    else:
        passed, out = run(
            "stage-7",
            [
                str(SKILLS / "stage-7-review" / "verify" / "code_review_verdict.py"),
                str(ARTIFACTS / "stage-7"),
            ],
        )
        print(out or "(no output)")
        if not passed:
            failures.append(("Stage 7", out))

    # --- Stage 8 (skipped — needs running app + Playwright artifacts) ---
    header("Stage 8 — UAT")
    print("skipped — UAT verifier requires app_health.json and Playwright artifacts; run via /stage-8")

    # --- Summary ---
    header("Summary")
    if failures:
        print(f"FAILED: {len(failures)} verifier(s)")
        for stage, out in failures:
            print(f"\n[{stage}]")
            print(out)
        return 1

    print("All invoked verifiers PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
