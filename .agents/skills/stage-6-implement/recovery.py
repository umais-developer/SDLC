#!/usr/bin/env python3
"""
Stage 6 recovery tool.

Why this exists
---------------
A Stage 6 run can leave the pipeline wedged: some tasks completed but none
verified, some files written but not all, and Stage 7's structural check then
fails because tasks.json references test files that don't exist on disk yet.

This script reports the wedged state and (with explicit confirmation) resets
progress so the next /stage-6 invocation starts cleanly.

Usage
-----
    python .agents/skills/stage-6-implement/recovery.py --status
    python .agents/skills/stage-6-implement/recovery.py --reset --yes
    python .agents/skills/stage-6-implement/recovery.py --unstage T-12 --yes

`--status` is read-only and is the default. `--reset` archives `progress.json`
to `progress.json.bak.<timestamp>` so a fresh `/stage-6` run sees no prior
progress. `--unstage <task-id>` removes a specific task from
`completed_tasks` and `tasks_verified` so it gets re-attempted.

Source files written by previous attempts are NOT touched. If you want to
also discard the code those tasks produced, use `git restore <path>` on the
specific files yourself — this script will not modify the working tree.
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
STAGE_6_DIR = REPO_ROOT / ".agents" / "artifacts" / "stage-6"
TASKS_PATH = REPO_ROOT / ".agents" / "artifacts" / "stage-5" / "tasks.json"


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def fmt_status(progress: dict, tasks: dict) -> str:
    completed = set(progress.get("completed_tasks", []) or [])
    verified = set(progress.get("tasks_verified", []) or [])
    failed = [f.get("id") for f in progress.get("failed_tasks", []) or [] if f.get("id")]
    modified = progress.get("modified_files", []) or []
    task_ids = [t.get("id") for t in tasks.get("tasks", []) if t.get("id")]
    total = len(task_ids)

    pending = [tid for tid in task_ids if tid not in completed]
    completed_unverified = sorted(completed - verified)

    lines = [
        f"Stage 6 progress (total tasks: {total})",
        f"  completed:        {len(completed)}",
        f"  verified:         {len(verified)}",
        f"  failed:           {len(failed)}",
        f"  modified files:   {len(modified)}",
        "",
    ]
    if pending:
        lines.append(f"Pending tasks ({len(pending)}): {', '.join(pending[:10])}"
                     + (" ..." if len(pending) > 10 else ""))
    if completed_unverified:
        lines.append(
            f"Completed but UNVERIFIED ({len(completed_unverified)}): "
            f"{', '.join(completed_unverified[:10])}"
            + (" ..." if len(completed_unverified) > 10 else "")
        )
    if failed:
        lines.append(f"Failed tasks ({len(failed)}): {', '.join(str(f) for f in failed)}")
    if not (pending or completed_unverified or failed):
        lines.append("State is clean — Stage 6 is complete.")

    return "\n".join(lines)


def fmt_recommendation(progress: dict, tasks: dict) -> str:
    completed = set(progress.get("completed_tasks", []) or [])
    verified = set(progress.get("tasks_verified", []) or [])
    failed = bool(progress.get("failed_tasks") or [])
    task_ids = {t.get("id") for t in tasks.get("tasks", []) if t.get("id")}

    if not task_ids:
        return "No tasks defined in tasks.json. Re-run Stage 5."
    if verified.issuperset(task_ids):
        return "Stage 6 is fully verified. No recovery needed."
    if failed:
        return (
            "Recommendation: investigate failed_tasks in progress.json, "
            "then either re-run /stage-6 (which will retry failures) or "
            "use --unstage <task-id> --yes to drop a specific task before retry."
        )
    if completed and not verified:
        return (
            "Recommendation: tasks were written but never verified. "
            "Re-run /stage-6 to verify them, or use --reset --yes to start "
            "fresh (source files in src/ are NOT removed)."
        )
    return "Recommendation: re-run /stage-6 to continue."


def archive_progress(stage_dir: Path) -> Path:
    progress = stage_dir / "progress.json"
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = stage_dir / f"progress.json.bak.{ts}"
    shutil.copy2(progress, backup)
    progress.unlink()
    return backup


def unstage_task(progress_path: Path, task_id: str) -> bool:
    data = load_json(progress_path)
    changed = False
    for key in ("completed_tasks", "tasks_verified"):
        items = data.get(key, []) or []
        if task_id in items:
            data[key] = [t for t in items if t != task_id]
            changed = True
    failed = data.get("failed_tasks", []) or []
    new_failed = [f for f in failed if not (isinstance(f, dict) and f.get("id") == task_id)]
    if len(new_failed) != len(failed):
        data["failed_tasks"] = new_failed
        changed = True
    if changed:
        with open(progress_path, "w") as f:
            json.dump(data, f, indent=2)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 6 recovery tool")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--status", action="store_true", help="report current state (default)")
    group.add_argument("--reset", action="store_true", help="archive progress.json so /stage-6 starts fresh")
    group.add_argument("--unstage", metavar="TASK_ID", help="remove a task from completed_tasks/tasks_verified/failed_tasks")
    parser.add_argument("--yes", action="store_true", help="confirm a destructive action (--reset / --unstage)")
    args = parser.parse_args()

    progress_path = STAGE_6_DIR / "progress.json"
    if not progress_path.exists():
        print(f"No progress.json at {progress_path}. Stage 6 has not been run yet.")
        return 0
    if not TASKS_PATH.exists():
        print(f"No tasks.json at {TASKS_PATH}. Run Stage 5 first.", file=sys.stderr)
        return 1

    progress = load_json(progress_path)
    tasks = load_json(TASKS_PATH)

    if args.reset:
        if not args.yes:
            print("Refusing to reset without --yes. Run --status first to see what would be lost.", file=sys.stderr)
            return 1
        backup = archive_progress(STAGE_6_DIR)
        print(f"Archived progress.json to {backup.relative_to(REPO_ROOT)}")
        print("Source files in src/ were NOT modified. Re-run /stage-6 to start clean.")
        return 0

    if args.unstage:
        if not args.yes:
            print("Refusing to unstage without --yes.", file=sys.stderr)
            return 1
        if unstage_task(progress_path, args.unstage):
            print(f"Removed {args.unstage} from progress.json. Re-run /stage-6 to retry it.")
            return 0
        print(f"{args.unstage} was not present in progress.json — nothing to do.", file=sys.stderr)
        return 1

    print(fmt_status(progress, tasks))
    print()
    print(fmt_recommendation(progress, tasks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
