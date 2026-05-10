"""
Drift-detection helpers for SDLC artifacts.

Why this exists
---------------
`prompt_version` (in each prompt's frontmatter) lets us tell that an artifact
was produced under a known prompt revision. But that doesn't catch the more
common drift: the upstream artifact itself changed after the downstream one
was produced. Example: someone edits `goals.json` to add FR-16, but
`stories.json` was generated before that change — the downstream is silently
stale.

This module provides:
  - `hash_artifact(path)`            sha256 of a file's bytes (first 12 hex)
  - `build_meta(...)`                assemble a meta block for a new artifact
  - `check_drift(artifact_path, ...)`compare recorded source_hashes against
                                     current files; return drifted paths

Convention
----------
Every structured stage artifact (problem.json, goals.json, components.json,
flows.json, stories.json, tasks.json, review.json, test_plan.json,
uat_results.json) should carry a top-level `meta` field:

    {
      "meta": {
        "generated_at": "2026-05-09T14:32:00Z",
        "prompt_versions": {"<prompt_name>": "<date>"},
        "source_hashes": {
          "stage-1/problem.json": "sha256:abc123...",
          "stage-1/goals.json":   "sha256:def456..."
        }
      },
      ...
    }

`generated_at` and `prompt_versions` are informational. `source_hashes` is
load-bearing: a verifier can compare recorded hashes against current files
and refuse the gate (or warn) if any upstream input has shifted.

Hashes are recorded as `sha256:<first 12 hex chars>` so the meta block stays
human-readable without losing collision resistance for drift purposes.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def hash_artifact(path: Path) -> str:
    """Return `sha256:<first 12 hex>` of the file's bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()[:12]}"


def now_iso() -> str:
    """Current UTC time in ISO 8601 with second precision."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_meta(
    prompt_versions: dict[str, str],
    source_artifacts: dict[str, Path],
) -> dict:
    """Assemble a meta block.

    Args:
        prompt_versions: map of prompt_name → version string, e.g.
            {"problem_interpretation": "2026-05-09"}.
        source_artifacts: map of relative-path key → absolute path on disk,
            e.g. {"stage-1/problem.json": Path("...")}.
    """
    return {
        "generated_at": now_iso(),
        "prompt_versions": dict(prompt_versions),
        "source_hashes": {key: hash_artifact(p) for key, p in source_artifacts.items()},
    }


def check_drift(
    artifact_path: Path,
    artifacts_root: Path,
) -> list[tuple[str, str, str]]:
    """Compare the artifact's recorded source_hashes against current files.

    Returns a list of `(source_key, recorded_hash, current_hash)` tuples for
    each source whose hash no longer matches. Empty list = no drift.

    Returns an empty list if the artifact has no `meta.source_hashes` block —
    drift is opt-in, not enforced.
    """
    with open(artifact_path) as f:
        data = json.load(f)
    recorded = (data.get("meta") or {}).get("source_hashes") or {}
    if not recorded:
        return []

    drifted: list[tuple[str, str, str]] = []
    for key, recorded_hash in recorded.items():
        source_path = artifacts_root / key
        if not source_path.exists():
            drifted.append((key, recorded_hash, "MISSING"))
            continue
        current_hash = hash_artifact(source_path)
        if current_hash != recorded_hash:
            drifted.append((key, recorded_hash, current_hash))
    return drifted
