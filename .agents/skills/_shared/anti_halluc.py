"""
Anti-hallucination scanner for stage artifacts.

Why this exists
---------------
STAGE-CONVENTIONS.md section 2 prohibits a specific set of fabricated-authority
phrases ("chosen per industry best practices", "based on user research", etc.)
The rule lives in every prompt as instruction to the LLM, but until now no
verifier scanned the produced artifacts for it. A sloppy LLM that ignored the
prompt could pass every other gate.

This module provides a regex-based scan that any markdown-final verifier can
call after producing its document.

Scope
-----
The scanner targets phrases that *assert authority without evidence*. It does
NOT try to be a general fact-checker — it only flags patterns that the
conventions document explicitly prohibits, plus a few high-confidence
fabricated-precision patterns ("studies show", "research indicates", "users
expect").

API
---
    from anti_halluc import scan
    violations = scan(text, stage="Stage 1")
    if violations:
        for line_no, snippet, pattern_label in violations:
            ...

Each violation is a (line_no, matched_snippet, pattern_label) tuple so the
caller can produce file:line citations.
"""

import re
from typing import Iterable

# Each pattern: (compiled regex, human-readable label).
# Patterns are case-insensitive. Order matters only for reporting consistency.
_PROHIBITED_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bindustry best practice", re.IGNORECASE),
     "fabricated authority: 'industry best practice'"),
    (re.compile(r"\bindustry standard", re.IGNORECASE),
     "fabricated authority: 'industry standard' (acceptable only for named protocols, e.g. 'OAuth 2.0')"),
    (re.compile(r"\bbased on (user research|industry research|market research)", re.IGNORECASE),
     "fabricated authority: invokes unspecified research"),
    (re.compile(r"\bderived from (testing|playability|user) (norms|research|studies)", re.IGNORECASE),
     "fabricated authority: invokes unspecified studies"),
    (re.compile(r"\bstudies (show|indicate|suggest)\b", re.IGNORECASE),
     "fabricated authority: 'studies show'"),
    (re.compile(r"\busers expect\b", re.IGNORECASE),
     "fabricated user-research claim: 'users expect'"),
    (re.compile(r"\busers abandon\b", re.IGNORECASE),
     "fabricated user-research claim: 'users abandon'"),
    (re.compile(r"\b(typical|standard) (usage|user) patterns?\b", re.IGNORECASE),
     "fabricated baseline: 'typical/standard usage patterns'"),
    (re.compile(r"\bproven (scalability|reliability|track record)\b", re.IGNORECASE),
     "generic virtue claim: 'proven X' without citation"),
    (re.compile(r"\bfor\s+its\s+(component\s+model|simplicity|flexibility|popularity|elegance)\b", re.IGNORECASE),
     "generic virtue claim — cite an FR/NFR/CON ID instead of 'for its X'"),
    (re.compile(r"\bcomponent\s+model\b.*\b(chosen|selected|preferred)\b", re.IGNORECASE),
     "generic virtue claim: tech 'chosen for its component model'"),
]

# Patterns that are normally fine but become violations when used as a
# justification (i.e. preceded by "for" or "because" with no upstream-ID cite).
# We approximate by flagging only when the line has no FR/NFR/CON/GOAL token.
_JUSTIFICATION_REQUIRES_ID = re.compile(
    r"\b(chosen|selected|preferred)\s+for\s+(its\s+)?(simplicity|flexibility|performance|maintainability|popularity)",
    re.IGNORECASE,
)
_HAS_UPSTREAM_ID = re.compile(r"\b(FR|NFR|CON|GOAL|S|T|FLOW)-\d+", re.IGNORECASE)


def scan(text: str, stage: str = "") -> list[tuple[int, str, str]]:
    """Scan `text` (markdown or plain) for fabricated-authority patterns.

    Returns a list of (line_no, snippet, pattern_label) tuples — empty if clean.

    Lines inside fenced code blocks are skipped, since example code or sample
    JSON may legitimately contain prohibited phrases (e.g. a "Bad" example in a
    prompt).
    """
    violations: list[tuple[int, str, str]] = []
    in_code_block = False

    for idx, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip()
        if line.lstrip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        for pattern, label in _PROHIBITED_PATTERNS:
            match = pattern.search(line)
            if match:
                snippet = line.strip()[:200]
                violations.append((idx, snippet, label))

        if _JUSTIFICATION_REQUIRES_ID.search(line) and not _HAS_UPSTREAM_ID.search(line):
            snippet = line.strip()[:200]
            violations.append(
                (idx, snippet, "justification missing upstream ID (FR/NFR/CON/GOAL)")
            )

    return violations


def format_violations(
    violations: Iterable[tuple[int, str, str]],
    file_label: str = "",
) -> str:
    """Render violations as a human-readable bullet list."""
    out = []
    for line_no, snippet, label in violations:
        prefix = f"{file_label}:" if file_label else ""
        out.append(f"  - {prefix}L{line_no}  [{label}]\n      {snippet}")
    return "\n".join(out)
