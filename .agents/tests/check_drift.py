#!/usr/bin/env python3
"""
Walk every structured artifact under `.agents/artifacts/` and report any whose
recorded `meta.source_hashes` no longer match the current files on disk.

Usage:

    python .agents/tests/check_drift.py

Exit code: 0 if no drift detected (or no artifact carries a meta block yet);
1 if at least one artifact has drifted source_hashes.

This is a soft gate — it does not modify any files. Run it after editing
upstream artifacts to see what downstream stages need re-running.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ARTIFACTS_ROOT = REPO_ROOT / ".agents" / "artifacts"
SHARED = REPO_ROOT / ".agents" / "skills" / "_shared"

sys.path.insert(0, str(SHARED))
from console import setup as setup_console  # noqa: E402
setup_console()
from meta import check_drift  # noqa: E402


def main() -> int:
    if not ARTIFACTS_ROOT.exists():
        print(f"No artifacts directory at {ARTIFACTS_ROOT} — nothing to check.")
        return 0

    artifacts = sorted(ARTIFACTS_ROOT.rglob("*.json"))
    if not artifacts:
        print("No JSON artifacts found.")
        return 0

    any_drift = False
    checked = 0

    for artifact in artifacts:
        rel = artifact.relative_to(REPO_ROOT)
        try:
            drifted = check_drift(artifact, ARTIFACTS_ROOT)
        except Exception as e:
            print(f"⚠️  Could not check {rel}: {e}", file=sys.stderr)
            continue

        if drifted:
            any_drift = True
            print(f"❌ {rel}")
            for key, recorded, current in drifted:
                print(f"   {key}: recorded={recorded}  current={current}")
        checked += 1

    print()
    if any_drift:
        print(f"Drift detected. Re-run the affected downstream stages.")
        return 1
    print(f"Checked {checked} artifact(s). No drift detected (or no meta blocks yet).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
