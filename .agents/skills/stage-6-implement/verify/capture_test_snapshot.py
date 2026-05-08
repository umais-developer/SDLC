#!/usr/bin/env python3
"""
Capture a snapshot of pre-existing test files for Stage 6.

Usage:
  python capture_test_snapshot.py <output_path> [root...]

If no roots are provided, defaults to: src tests
"""

import json
import sys
from pathlib import Path

TEST_PATTERNS = ["**/*.test.*", "**/*.spec.*", "**/__tests__/**/*.*"]


def collect_tests(roots: list[Path]) -> list[str]:
    files: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for pattern in TEST_PATTERNS:
            for path in root.glob(pattern):
                if path.is_file():
                    files.append(path.as_posix())
    return sorted(set(files))


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python capture_test_snapshot.py <output_path> [root...]")
        return 1

    output_path = Path(sys.argv[1])
    roots = [Path(p) for p in sys.argv[2:]] if len(sys.argv) > 2 else [Path("src"), Path("tests")]

    test_files = collect_tests(roots)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({"test_files": test_files}, indent=2) + "\n", encoding="utf-8")

    print(f"Captured {len(test_files)} test files to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
