#!/usr/bin/env python3
"""Deterministic intent expansion helper.

Transforms raw request text into a structured intent model without using LLM calls.

Usage:
  python3 .agents/scripts/intent_expansion.py --input Requirements.md --output .agents/tmp/intent_expanded.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "must", "should", "would",
    "have", "has", "had", "are", "was", "were", "will", "can", "could", "our", "your", "their",
    "user", "users", "feature", "system", "application", "app", "page", "screen", "component",
}

GOAL_CUES = ("need", "want", "must", "should", "goal", "objective")
CONSTRAINT_CUES = (
    "must", "must not", "cannot", "should not", "out of scope", "non-functional",
    "performance", "security", "privacy", "accessibility", "compliance",
)


def sentence_split(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def extract_goals(sentences: List[str]) -> List[str]:
    goals = []
    for s in sentences:
        lower = s.lower()
        if any(cue in lower for cue in GOAL_CUES):
            goals.append(s)
    return goals[:12]


def extract_constraints(sentences: List[str]) -> List[str]:
    constraints = []
    for s in sentences:
        lower = s.lower()
        if any(cue in lower for cue in CONSTRAINT_CUES):
            constraints.append(s)
    return constraints[:20]


def extract_entities(text: str, limit: int = 20) -> List[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text)
    words = [w.lower() for w in words if w.lower() not in STOPWORDS]
    counts = Counter(words)
    return [w for w, _ in counts.most_common(limit)]


def extract_candidate_actions(sentences: List[str], limit: int = 25) -> List[str]:
    actions: List[str] = []
    for s in sentences:
        m = re.search(r"\b(to|should|must)\b\s+([a-zA-Z][^.,;:]*)", s, flags=re.IGNORECASE)
        if m:
            actions.append(m.group(2).strip())
    # deterministic de-dup
    seen = set()
    unique = []
    for a in actions:
        key = a.lower()
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique[:limit]


def build_intent_model(text: str) -> Dict[str, object]:
    sentences = sentence_split(text)
    goals = extract_goals(sentences)
    constraints = extract_constraints(sentences)
    entities = extract_entities(text)
    actions = extract_candidate_actions(sentences)

    return {
        "summary": sentences[0] if sentences else "",
        "goals": goals,
        "constraints": constraints,
        "entities": entities,
        "candidate_actions": actions,
        "open_questions": [
            "Which requirement is highest priority (P0)?",
            "What is explicitly out of scope for this release?",
            "Which acceptance criteria are mandatory for launch?",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic intent expansion for SDLC input.")
    parser.add_argument("--input", required=True, help="Path to input markdown or text")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)

    text = in_path.read_text(encoding="utf-8", errors="replace")
    model = build_intent_model(text)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(model, indent=2), encoding="utf-8")

    print(f"Intent expansion written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
