#!/usr/bin/env python3
"""
prd_final_check.py — Two-layer, size-aware confidence scorer for prd_final.md

Layer 1 (70% weight): Deterministic structural checks (size-aware)
Layer 2 (30% weight): LLM qualitative checks via Anthropic Claude

Graceful degradation: if LLM is unavailable, falls back to deterministic-only
scoring with threshold recalibrated to 80%.

Usage:
    python prd_final_check.py <prd_final.md> <goals.json> [problem.json]

If problem.json is provided and contains a "size" field ("trivial" | "medium" | "large"),
required-section and required-ID checks are tailored to that size. Without it, the
checker defaults to Medium-sized expectations.

Exit code: 0 = confidence >= threshold
Exit code: 1 = below threshold or error
"""

import json
import os
import re
import sys
from pathlib import Path

# Shared helpers: console encoding setup + anti-hallucination scanner.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "_shared"))
from console import setup as setup_console  # noqa: E402
setup_console()
from anti_halluc import scan as scan_anti_halluc, format_violations  # noqa: E402

# Load .env from the project root (two levels up from this script's verify/ dir)
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
    load_dotenv(dotenv_path=_env_path)
except ImportError:
    pass  # python-dotenv not installed; fall back to environment variables only

THRESHOLD = 0.85
DET_WEIGHT  = 0.70   # deterministic layer share of final score
LLM_WEIGHT  = 0.30   # LLM qualitative layer share of final score
LLM_FALLBACK_THRESHOLD = 0.80  # lower bar when LLM is unavailable
LLM_MODEL = "claude-haiku-4-5-20251001"
LLM_PRD_CHAR_LIMIT = 16000  # max PRD chars sent to LLM auditor

# ---------------------------------------------------------------------------
# Size-aware configuration
# ---------------------------------------------------------------------------
# Each size selects a profile of required sections, required ID checks,
# and which LLM dimensions are evaluated. Trivial PRDs are intentionally
# graded against a minimal rubric so the SKILL.md sizing tiers are honoured.

SECTION_PATTERNS = {
    "problem":       (r"##\s+\d+\.\s+Problem",                 "Problem Statement section"),
    "assumptions":   (r"##\s+\d+\.\s+Assumptions",             "Assumptions & Open Questions section"),
    "scope":         (r"(##\s+\d+\.\s+Scope|In Scope|Out of Scope)", "Scope section"),
    "acceptance":    (r"##\s+\d+\.\s+Acceptance",              "Acceptance Summary section"),
    "goals":         (r"##\s+\d+\.\s+Goals",                   "Goals section"),
    "fr":            (r"##\s+\d+\.\s+Functional Requirements", "Functional Requirements section"),
    "nfr":           (r"##\s+\d+\.\s+Non.Functional",          "Non-Functional Requirements section"),
    "traceability":  (r"##\s+\d+\.\s+Traceability Matrix",     "Traceability Matrix section"),
    "testing":       (r"##\s+\d+\.\s+Testing Strategy",        "Testing Strategy section"),
}

# Per-size profile: which section keys are required and which ID checks apply
SIZE_PROFILES = {
    "trivial": {
        "sections":     ["problem", "assumptions", "scope", "acceptance"],
        "id_checks":    ["fr_ids_present"],   # FRs only; no goals/NFRs/matrix
        "needs_matrix": False,
        "llm_dims":     ["proportionality", "baseline_creep",
                         "decision_consolidation", "implementation_free"],
        # business_value dropped for trivial — single-line problem is acceptable
    },
    "medium": {
        "sections":     ["problem", "assumptions", "goals", "fr",
                         "testing", "acceptance"],
        "id_checks":    ["goal_ids_present", "fr_ids_present"],
        "needs_matrix": False,  # only required if GOAL count > 2 (checked dynamically)
        "llm_dims":     ["proportionality", "baseline_creep",
                         "decision_consolidation", "business_value",
                         "implementation_free"],
    },
    "large": {
        "sections":     ["problem", "assumptions", "goals", "fr", "nfr",
                         "traceability", "testing", "acceptance"],
        "id_checks":    ["goal_ids_present", "fr_ids_present", "nfr_ids_present"],
        "needs_matrix": True,
        "llm_dims":     ["proportionality", "baseline_creep",
                         "decision_consolidation", "business_value",
                         "implementation_free"],
    },
}

VAGUE_PHRASES = [
    r"\bas described above\b",
    r"\bsee requirements\b",
    r"\blorem ipsum\b",
    # NOTE: "TBD" is intentionally NOT here — the skill explicitly permits
    # [TBD — stakeholder input needed] as an honest signal of genuine uncertainty.
    # The LLM auditor is responsible for catching lazy TBDs.
]

# Deterministic checks. Weights are renormalised at runtime based on which
# checks apply to the current size profile.
ALL_CHECKS = [
    ("required_sections",  "All required sections present (size-aware)",                 0.20),
    ("no_placeholders",    "No {{placeholder}} tokens remaining",                        0.15),
    ("goal_ids_present",   "All GOAL-* IDs from goals.json appear in PRD",               0.15),
    ("fr_ids_present",     "All FR-* IDs from goals.json appear in PRD",                 0.15),
    ("nfr_ids_present",    "All NFR-* IDs from goals.json appear in PRD",                0.10),
    ("traceability_links", "Traceability matrix links each GOAL to at least one FR",     0.15),
    ("no_stub_sections",   "No required section is empty/stub-only",                     0.05),
    ("no_vague_phrases",   "No stub/vague filler phrases detected",                      0.05),
    ("no_fabricated_authority", "No fabricated-authority phrases (anti-hallucination)",   0.05),
]

# LLM qualitative dimensions — feature-agnostic rubric (no search-bar specifics).
# Each gets equal share (0.20) of the LLM_WEIGHT when all five run.
# Weights are renormalised at runtime based on which dimensions apply.
LLM_DIMENSIONS = {
    "proportionality": {
        "description": "Documentation effort is proportionate to feature complexity",
        "weight": 0.20,
        "rubric": (
            "10 = section count, requirement count, and detail level are appropriate "
            "for the feature's actual scope; a small UI tweak gets a compact PRD, a "
            "cross-cutting subsystem gets a thorough one. "
            "0 = a trivial change is wrapped in 9 sections, traceability matrices, "
            "and 7+ requirements; ceremony exceeds the work."
        ),
    },
    "baseline_creep": {
        "description": "Every requirement describes genuinely new behavior, not universal defaults",
        "weight": 0.20,
        "rubric": (
            "10 = every FR and NFR describes behavior the system would not exhibit "
            "by default — each is a real product decision. "
            "0 = requirements include things that are baseline expectations for any "
            "modern application (e.g. 'is keyboard accessible', 'has a label', "
            "'shows an empty state when nothing matches', 'persists nothing between "
            "sessions when no persistence was requested'). Such items inflate scope "
            "without adding signal."
        ),
    },
    "decision_consolidation": {
        "description": "Key scope decisions are consolidated, not scattered across sections",
        "weight": 0.20,
        "rubric": (
            "10 = the specific behavioral parameters this feature requires "
            "(its actual product decisions, whatever they are for this feature) "
            "appear in one dedicated place and are referenced from elsewhere. "
            "0 = the same decision is restated in Scope, Ambiguities, FR acceptance "
            "criteria, and Constraints simultaneously, forcing the reader to "
            "reconcile multiple copies."
        ),
    },
    "business_value": {
        "description": "Clear statement of who benefits and what outcome results",
        "weight": 0.20,
        "rubric": (
            "10 = clearly states who the user is, what problem they have, and what "
            "observable outcome the change produces. "
            "0 = no business or user context — pure feature description with no "
            "explanation of why it should exist. "
            "Note: invented metrics with fabricated precision (e.g. '≥80% of "
            "sessions', 'average duration ≥ 3 minutes' with no measurement plan) "
            "are a form of failure here — score them down, not up."
        ),
    },
    "implementation_free": {
        "description": "Free of prescribed implementation details",
        "weight": 0.20,
        "rubric": (
            "10 = describes WHAT and WHY in user/business language; does not dictate "
            "HOW. Naming standards or APIs that ARE the requirement is acceptable "
            "(e.g. 'must meet WCAG 2.1 AA' is the requirement itself; "
            "'announce updates via ARIA live regions' names a standard accessibility "
            "primitive). "
            "0 = prescribes specific technology choices that should be architecture "
            "decisions (e.g. 'use React with Redux', 'build with Vite', 'store in "
            "IndexedDB'), or includes code, file structures, or build configurations."
        ),
    },
}


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        print(f"❌ File not found: {path}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    try:
        return json.loads(load_file(path))
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def determine_size(problem_path: str | None, goals: dict) -> tuple[str, str]:
    """
    Return (size, source) where source explains how size was determined.
    Priority: problem.json size field > goals.json size field > Medium default.
    """
    if problem_path and Path(problem_path).exists():
        problem = load_json(problem_path)
        size = problem.get("size", "").lower().strip()
        if size in SIZE_PROFILES:
            return size, f"from {problem_path}"

    size = goals.get("size", "").lower().strip()
    if size in SIZE_PROFILES:
        return size, "from goals.json"

    return "medium", "default (no size field found)"


# ---------------------------------------------------------------------------
# LLM layer
# ---------------------------------------------------------------------------

def run_llm_checks(prd_text: str, active_dim_keys: list[str]) -> tuple[list, bool]:
    """
    Call Anthropic Claude to score the PRD on qualitative dimensions.
    Only the dimensions in active_dim_keys are evaluated.
    Returns (results_list, llm_available).
    Falls back gracefully if API key missing or call fails.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not set — skipping LLM qualitative checks")
        return [], False

    try:
        import anthropic
    except ImportError:
        print("⚠️  anthropic package not installed — skipping LLM qualitative checks")
        return [], False

    # Build size-aware schema and rubric text
    schema_lines = []
    rubric_lines = []
    for key in active_dim_keys:
        dim = LLM_DIMENSIONS[key]
        schema_lines.append(
            f'  "{key}": {{\n'
            f'    "score": <0-10>,\n'
            f'    "justification": "<one sentence>",\n'
            f'    "failures": ["<specific issue if score < 7, else empty list>"]\n'
            f'  }}'
        )
        rubric_lines.append(f"- {key}: {dim['rubric']}")

    schema_block = "{\n" + ",\n".join(schema_lines) + "\n}"
    rubric_block = "\n".join(rubric_lines)

    # Truncate with explicit warning
    truncated = len(prd_text) > LLM_PRD_CHAR_LIMIT
    prd_excerpt = prd_text[:LLM_PRD_CHAR_LIMIT]
    if truncated:
        print(f"⚠️  PRD exceeds {LLM_PRD_CHAR_LIMIT} chars — LLM will see only the first portion")

    rubric_prompt = f"""You are a PRD quality auditor. Score the following Product Requirements Document on the dimensions below.

Return ONLY valid JSON matching this exact schema — no explanation, no markdown:
{schema_block}

Scoring criteria:
{rubric_block}

PRD to evaluate{' (TRUNCATED)' if truncated else ''}:
---
{prd_excerpt}
---"""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=LLM_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": rubric_prompt}],
        )
        raw = message.content[0].text.strip()
        # Strip markdown code fences if model wrapped response
        raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\n?```$", "", raw)
        llm_scores = json.loads(raw)
    except Exception as e:
        print(f"⚠️  LLM check failed ({e}) — skipping qualitative layer")
        return [], False

    results = []
    # Equal share among active dimensions
    share = 1.0 / len(active_dim_keys) if active_dim_keys else 0
    for key in active_dim_keys:
        dim_meta = LLM_DIMENSIONS[key]
        dim = llm_scores.get(key, {})
        raw_score = dim.get("score", 0)
        normalized = raw_score / 10.0
        passed = raw_score >= 7
        results.append({
            "id": f"llm_{key}",
            "description": dim_meta["description"],
            "weight": share,
            "passed": passed,
            "score": raw_score,
            "justification": dim.get("justification", ""),
            "failures": dim.get("failures", []),
            "normalized": normalized,
        })

    return results, True


# ---------------------------------------------------------------------------
# Deterministic layer
# ---------------------------------------------------------------------------

def section_match(prd_text: str, key: str):
    """Return regex match for a section by key, including its body up to next ## section."""
    pattern, _ = SECTION_PATTERNS[key]
    return re.search(
        pattern + r"(.+?)(?=\n##\s|\Z)",
        prd_text,
        re.IGNORECASE | re.DOTALL,
    )


def run_checks(prd_text: str, goals: dict, profile: dict) -> list:
    results = []
    required_section_keys = profile["sections"]
    active_id_checks = set(profile["id_checks"])
    needs_matrix = profile["needs_matrix"]

    # Dynamic matrix requirement: Medium PRDs need matrix only if > 2 goals
    goal_count = len(goals.get("goals", []))
    if not needs_matrix and "goals" in required_section_keys and goal_count > 2:
        needs_matrix = True

    if needs_matrix and "traceability" not in required_section_keys:
        required_section_keys = required_section_keys + ["traceability"]

    # Filter ALL_CHECKS down to those active for this size
    active_check_ids = {"required_sections", "no_placeholders",
                        "no_stub_sections", "no_vague_phrases",
                        "no_fabricated_authority"}
    active_check_ids.update(active_id_checks)
    if needs_matrix:
        active_check_ids.add("traceability_links")

    active_checks = [c for c in ALL_CHECKS if c[0] in active_check_ids]

    for check_id, description, weight in active_checks:
        passed = False
        failures = []

        if check_id == "required_sections":
            missing = []
            for key in required_section_keys:
                pattern, label = SECTION_PATTERNS[key]
                if not re.search(pattern, prd_text, re.IGNORECASE):
                    missing.append(label)
            passed = len(missing) == 0
            failures = [f"Missing section: {s}" for s in missing]

        elif check_id == "no_placeholders":
            found = list(set(re.findall(r"\{\{[^}]+\}\}", prd_text)))
            passed = len(found) == 0
            failures = [f"Unreplaced placeholder: {p}" for p in found]

        elif check_id == "goal_ids_present":
            goal_ids = [g["id"] for g in goals.get("goals", [])]
            missing = [gid for gid in goal_ids if gid not in prd_text]
            passed = len(missing) == 0
            failures = [f"Missing goal ID: {gid}" for gid in missing]

        elif check_id == "fr_ids_present":
            fr_ids = [fr["id"] for fr in goals.get("functional_requirements", [])]
            missing = [frid for frid in fr_ids if frid not in prd_text]
            passed = len(missing) == 0
            failures = [f"Missing FR ID: {frid}" for frid in missing]

        elif check_id == "nfr_ids_present":
            nfr_ids = [nfr["id"] for nfr in goals.get("non_functional_requirements", [])]
            missing = [nid for nid in nfr_ids if nid not in prd_text]
            passed = len(missing) == 0
            failures = [f"Missing NFR ID: {nid}" for nid in missing]

        elif check_id == "traceability_links":
            goal_ids = [g["id"] for g in goals.get("goals", [])]
            fr_ids = [fr["id"] for fr in goals.get("functional_requirements", [])]
            matrix_match = re.search(
                r"##\s+\d+\.\s+Traceability Matrix(.+?)(?=\n##\s|\Z)",
                prd_text,
                re.IGNORECASE | re.DOTALL,
            )
            if not matrix_match:
                passed = False
                failures = ["Traceability Matrix section not found or empty"]
            else:
                matrix_text = matrix_match.group(1)
                unlinked = []
                for gid in goal_ids:
                    if gid not in matrix_text:
                        unlinked.append(f"{gid} (not in matrix)")
                    else:
                        lines = [l for l in matrix_text.splitlines() if gid in l]
                        has_fr = any(
                            any(frid in line for frid in fr_ids)
                            for line in lines
                        )
                        if not has_fr:
                            unlinked.append(f"{gid} (no FR linked in matrix row)")
                passed = len(unlinked) == 0
                failures = [f"Goal not linked to FR in traceability matrix: {u}" for u in unlinked]

        elif check_id == "no_stub_sections":
            # Catch genuinely empty/stub sections — NOT short ones.
            # A stub is a heading with essentially no body content.
            STUB_THRESHOLD = 5  # words; anything below this is almost certainly a stub
            stubs = []
            for key in required_section_keys:
                _, label = SECTION_PATTERNS[key]
                m = section_match(prd_text, key)
                if m:
                    body = m.group(1).strip()
                    # Strip out empty markdown table skeletons and similar visual-only chrome
                    cleaned = re.sub(r'[\|\-:\s]+', ' ', body).strip()
                    words = len(cleaned.split())
                    if words < STUB_THRESHOLD:
                        stubs.append(f"{label} (only {words} content words)")
            passed = len(stubs) == 0
            failures = [f"Stub section: {s}" for s in stubs]

        elif check_id == "no_vague_phrases":
            found = []
            for phrase in VAGUE_PHRASES:
                matches = re.findall(phrase, prd_text, re.IGNORECASE)
                found.extend(matches)
            found = list(set(found))
            passed = len(found) == 0
            failures = [f"Vague filler phrase detected: '{p}'" for p in found]

        elif check_id == "no_fabricated_authority":
            violations = scan_anti_halluc(prd_text, stage="Stage 1")
            passed = len(violations) == 0
            failures = [
                f"L{line_no} [{label}]: {snippet}"
                for line_no, snippet, label in violations
            ]

        results.append({
            "id": check_id,
            "description": description,
            "weight": weight,
            "passed": passed,
            "failures": failures,
        })

    return results


# ---------------------------------------------------------------------------
# Score blending
# ---------------------------------------------------------------------------

def compute_score(det_results: list, llm_results: list, llm_available: bool) -> tuple[float, float]:
    """
    Blend deterministic (70%) and LLM (30%) scores.
    If LLM unavailable, use deterministic only with recalibrated threshold.
    Weights are renormalised based on which checks were active.
    Returns (final_score, effective_threshold).
    """
    if not det_results:
        det_score = 0.0
    else:
        det_total = sum(r["weight"] for r in det_results)
        det_earned = sum(r["weight"] for r in det_results if r["passed"])
        det_score = det_earned / det_total if det_total > 0 else 0.0

    if not llm_available or not llm_results:
        return round(det_score, 4), LLM_FALLBACK_THRESHOLD

    # LLM score: weighted average of normalized dimension scores
    llm_total_weight = sum(r["weight"] for r in llm_results)
    if llm_total_weight > 0:
        llm_score = sum(r["normalized"] * r["weight"] for r in llm_results) / llm_total_weight
    else:
        llm_score = 0.0

    final = round(DET_WEIGHT * det_score + LLM_WEIGHT * llm_score, 4)
    return final, THRESHOLD


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(prd_path: str, goals_path: str, problem_path: str | None = None) -> None:
    prd_text = load_file(prd_path)
    goals = load_json(goals_path)

    # Determine size and select profile
    size, size_source = determine_size(problem_path, goals)
    profile = SIZE_PROFILES[size]

    print(f"\n📋 PRD Final Check")
    print(f"   Size profile     : {size.upper()} ({size_source})")

    # Layer 1: deterministic (size-aware)
    det_results = run_checks(prd_text, goals, profile)

    # Layer 2: LLM qualitative (size-aware)
    llm_results, llm_available = run_llm_checks(prd_text, profile["llm_dims"])

    score, effective_threshold = compute_score(det_results, llm_results, llm_available)
    passed_overall = score >= effective_threshold

    mode_label = "Deterministic + LLM" if llm_available else "Deterministic only (LLM unavailable)"
    print(f"   Mode             : {mode_label}")
    print(f"   Confidence Score : {score:.0%}")
    print(f"   Threshold        : {effective_threshold:.0%}")
    print(f"   Result           : {'✅ PASS' if passed_overall else '❌ FAIL — recompile required'}")

    # --- Deterministic results ---
    det_passed = [r for r in det_results if r["passed"]]
    det_failed = [r for r in det_results if not r["passed"]]

    print(f"\n── Layer 1: Structural Checks ({len(det_results)} active for {size}) ──")
    for r in det_passed:
        print(f"  ✅ [{r['weight']:.0%}] {r['description']}")
    for r in det_failed:
        print(f"  ❌ [{r['weight']:.0%}] {r['description']}")
        for f in r["failures"]:
            print(f"       • {f}")

    # --- LLM results ---
    if llm_available and llm_results:
        print(f"\n── Layer 2: Qualitative Checks ({len(llm_results)} active for {size}) ──")
        for r in llm_results:
            icon = "✅" if r["passed"] else "❌"
            print(f"  {icon} [{r['score']}/10] {r['description']}")
            print(f"       → {r['justification']}")
            for f in r["failures"]:
                print(f"       • {f}")

    # Write structured report for recompile loop
    report_path = Path(prd_path).parent / "prd_check_report.json"
    all_failures = (
        [f for r in det_failed for f in r["failures"]] +
        [f for r in (llm_results or []) if not r["passed"] for f in r["failures"]]
    )
    report = {
        "size": size,
        "size_source": size_source,
        "score": score,
        "threshold": effective_threshold,
        "passed": passed_overall,
        "llm_available": llm_available,
        "deterministic_checks": det_results,
        "llm_checks": llm_results,
        "failure_summary": all_failures,
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n📄 Report written to: {report_path}")

    sys.exit(0 if passed_overall else 1)


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print("Usage: python verify/prd_final_check.py <prd_final.md> <goals.json> [problem.json]")
        sys.exit(1)
    prd = sys.argv[1]
    goals = sys.argv[2]
    problem = sys.argv[3] if len(sys.argv) == 4 else None
    main(prd, goals, problem)