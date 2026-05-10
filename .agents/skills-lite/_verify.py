"""
Combined verifier for the 3-stage lite pipeline.

Usage:
    python .agents/skills-lite/_verify.py spec
    python .agents/skills-lite/_verify.py build
    python .agents/skills-lite/_verify.py verify

Exit 0 = pass, exit 1 = fail. Failure messages go to stderr.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / ".agents" / "artifacts-lite"
SPEC = ART / "spec.md"
BUILD_LOG = ART / "build.log"
REVIEW = ART / "REVIEW.md"

REQUIRED_SECTIONS = [
    "## Problem",
    "## Functional Requirements",
    "## Assumptions",
    "## Acceptance Criteria",
]

FR_PATTERN = re.compile(r"\bFR-(\d+)\b")
ASSUMED_PATTERN = re.compile(r"\[assumed:\s*[^\]]+?\s*[-—]\s*[^\]]+\]")


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def passed(msg: str) -> None:
    print(f"OK: {msg}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def fr_ids_in(text: str) -> set[str]:
    return {f"FR-{n}" for n in FR_PATTERN.findall(text)}


def parse_section(text: str, header: str) -> str:
    """Return body text under a `## Header` line, up to the next `## ` or EOF."""
    pattern = re.compile(
        rf"^{re.escape(header)}\s*\n(.*?)(?=\n## |\Z)", re.DOTALL | re.MULTILINE
    )
    m = pattern.search(text)
    return m.group(1).strip() if m else ""


def verify_spec() -> None:
    text = read(SPEC)
    for sec in REQUIRED_SECTIONS:
        if sec not in text:
            fail(f"spec.md missing section: {sec}")
    fr_ids = fr_ids_in(parse_section(text, "## Functional Requirements"))
    if not fr_ids:
        fail("spec.md has no FR-N entries under Functional Requirements")
    if len(fr_ids) > 10:
        fail(f"spec.md has {len(fr_ids)} FRs (cap is 10 — use /create-product)")
    ac_text = parse_section(text, "## Acceptance Criteria")
    ac_fr_ids = fr_ids_in(ac_text)
    missing = sorted(fr_ids - ac_fr_ids, key=lambda s: int(s.split("-")[1]))
    if missing:
        fail(f"FRs without acceptance criteria: {missing}")
    assumptions = parse_section(text, "## Assumptions")
    # Allow "None." as a valid assumptions section.
    if assumptions and assumptions.lower() not in {"none.", "none", "_none_"}:
        # Each non-empty bullet should be tagged
        bullets = [
            b.strip("-* ").strip()
            for b in assumptions.splitlines()
            if b.strip().startswith(("-", "*"))
        ]
        for b in bullets:
            if not ASSUMED_PATTERN.search(b):
                fail(
                    f"assumption is not tagged with [assumed: ... — ...]: {b[:80]}"
                )
    passed(f"spec.md OK — {len(fr_ids)} FR(s), {len(ac_fr_ids)} covered by AC")


def verify_build() -> None:
    if not SPEC.exists():
        fail("spec.md must exist before verifying build")
    log = read(BUILD_LOG)
    if not re.search(r"EXIT=(\d+)\s*$", log.strip()):
        fail("build.log must end with EXIT=<n>")
    m = re.search(r"EXIT=(\d+)\s*$", log.strip())
    code = int(m.group(1)) if m else -1
    if code != 0:
        fail(f"build.log reports EXIT={code} — fix tests/build before continuing")

    spec_frs = fr_ids_in(SPEC.read_text(encoding="utf-8"))
    test_files: list[Path] = []
    for pattern in ("**/*.test.*", "**/*.spec.*", "tests/**/*"):
        for p in ROOT.glob(f"src/{pattern}"):
            if p.is_file():
                test_files.append(p)
        for p in ROOT.glob(pattern):
            if p.is_file() and p.is_relative_to(ROOT / "tests"):
                test_files.append(p)
    test_files = list(dict.fromkeys(test_files))  # dedupe
    if not test_files:
        fail("no test files found under src/ or tests/")

    fr_seen: dict[str, list[Path]] = {fr: [] for fr in spec_frs}
    for tf in test_files:
        try:
            content = tf.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for fr in spec_frs:
            if fr in content:
                fr_seen[fr].append(tf)

    uncovered = [fr for fr, files in fr_seen.items() if not files]
    if uncovered:
        fail(
            "FRs with no test that names the ID: "
            f"{sorted(uncovered, key=lambda s: int(s.split('-')[1]))}"
        )

    # Placeholder check on source files only (not tests)
    src_files = [p for p in (ROOT / "src").glob("**/*") if p.is_file() and not p.name.endswith(("test.ts", "test.tsx", "spec.ts", "test.js", "spec.js"))]
    bad = []
    for p in src_files:
        if p.suffix not in {".ts", ".tsx", ".js", ".jsx", ".py", ".css"}:
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if re.search(r"\bTODO\b|\bFIXME\b|not\s+implemented", txt, re.IGNORECASE):
            # CSS / comments allowed; only flag if it's the bulk of the file.
            non_blank = [l for l in txt.splitlines() if l.strip()]
            if len(non_blank) < 8:
                bad.append(str(p.relative_to(ROOT)))
    if bad:
        fail(f"placeholder/stub-only source files: {bad}")

    passed(
        f"build.log EXIT=0 — {len(spec_frs)} FR(s) covered by {sum(1 for v in fr_seen.values() if v)} groups of tests"
    )


def verify_verify() -> None:
    if not SPEC.exists() or not BUILD_LOG.exists():
        fail("spec.md and build.log must exist before verifying review")
    text = read(REVIEW)
    m = re.search(r"^\*\*Verdict:\*\*\s*(APPROVE|CHANGES_REQUIRED)", text, re.MULTILINE)
    if not m:
        fail("REVIEW.md must contain a `**Verdict:** APPROVE|CHANGES_REQUIRED` line")
    verdict = m.group(1)
    spec_frs = fr_ids_in(SPEC.read_text(encoding="utf-8"))
    review_frs = fr_ids_in(text)
    missing = sorted(spec_frs - review_frs, key=lambda s: int(s.split("-")[1]))
    if missing:
        fail(f"REVIEW.md does not mention these FRs: {missing}")
    # Each FR should have PASS or FAIL near it on the same line.
    failures = []
    for line in text.splitlines():
        m_fr = FR_PATTERN.search(line)
        if not m_fr:
            continue
        if "PASS" not in line and "FAIL" not in line:
            continue
        if "FAIL" in line and "PASS" not in line:
            failures.append(line.strip())

    # Also check the build log still says EXIT=0
    log = BUILD_LOG.read_text(encoding="utf-8")
    if not re.search(r"EXIT=0\s*$", log.strip()):
        fail("build.log no longer ends with EXIT=0 — re-run Stage B")

    # Critical/High findings rule
    if re.search(r"\b(Critical|High)\b", text):
        # Must not be in a finding bullet that's still active
        # Allow them only if explicitly resolved
        for line in text.splitlines():
            if re.search(r"\b(Critical|High)\b", line) and "RESOLVED" not in line.upper():
                if "Findings" in text and line.strip().startswith("-"):
                    fail(f"unresolved Critical/High finding in REVIEW.md: {line.strip()[:120]}")

    if verdict != "APPROVE":
        fail(f"verdict is {verdict} (must be APPROVE to pass the gate)")
    if failures:
        fail(f"REVIEW.md has FR rows marked FAIL: {failures}")
    passed(f"REVIEW.md APPROVE — {len(spec_frs)} FR(s) all PASS")


def main(argv: list[str]) -> None:
    if len(argv) != 2 or argv[1] not in {"spec", "build", "verify"}:
        print("usage: python _verify.py {spec|build|verify}", file=sys.stderr)
        sys.exit(2)
    {"spec": verify_spec, "build": verify_build, "verify": verify_verify}[argv[1]]()


if __name__ == "__main__":
    main(sys.argv)
