#!/usr/bin/env python3
"""
Inject the `meta` block into a structured stage artifact.

Why this exists
---------------
`meta.prompt_versions` and `meta.source_hashes` (defined in
STAGE-CONVENTIONS.md section 8) let downstream verifiers detect when an
artifact is stale relative to either the prompt that produced it or the
upstream artifacts it depends on. The LLM cannot compute file hashes, so
this post-process step injects them after the artifact is written.

Usage
-----
    python .agents/skills/_shared/inject_meta.py <path-to-artifact>

The artifact path is matched against ARTIFACT_MAPPING below; if a mapping
exists, the script reads the relevant prompts' `prompt_version` from their
frontmatter, hashes the listed source artifacts, and writes a `meta` field
into the artifact's top-level JSON (replacing any existing meta block).

If the artifact has no mapping (e.g. log files, snapshots, free-form
records), the script exits silently with code 0.

Each stage's SKILL.md should call this immediately after writing its
JSON artifact.
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SKILLS = REPO_ROOT / ".agents" / "skills"
ARTIFACTS = REPO_ROOT / ".agents" / "artifacts"

sys.path.insert(0, str(SKILLS / "_shared"))
from console import setup as setup_console  # noqa: E402
setup_console()
from meta import build_meta  # noqa: E402


# Maps artifact (relative to .agents/artifacts/) to:
#   prompts: list of (prompt_name, stage_dir_name)
#   sources: list of artifact paths (relative to .agents/artifacts/)
ARTIFACT_MAPPING: dict[str, dict] = {
    "stage-1/problem.json": {
        "prompts": [("problem_interpretation", "stage-1-prd")],
        "sources": [],
    },
    "stage-1/goals.json": {
        "prompts": [("goals_extraction", "stage-1-prd")],
        "sources": ["stage-1/problem.json"],
    },
    "stage-2/tech_stack.json": {
        "prompts": [("tech_stack_review", "stage-2-architecture")],
        "sources": ["stage-1/problem.json", "stage-1/goals.json"],
    },
    "stage-2/components.json": {
        "prompts": [("component_design", "stage-2-architecture")],
        "sources": ["stage-1/goals.json", "stage-2/tech_stack.json"],
    },
    "stage-3/flows.json": {
        "prompts": [("user_flows", "stage-3-ux")],
        "sources": ["stage-1/goals.json", "stage-2/components.json"],
    },
    "stage-4/stories.json": {
        "prompts": [("epics_stories", "stage-4-epics")],
        "sources": [
            "stage-1/goals.json",
            "stage-3/flows.json",
            "stage-2/components.json",
        ],
    },
    "stage-5/tasks.json": {
        "prompts": [("implementation_plan", "stage-5-plan")],
        "sources": [
            "stage-4/stories.json",
            "stage-2/components.json",
            "stage-1/goals.json",
        ],
    },
    "stage-7/review.json": {
        "prompts": [("code_audit", "stage-7-review")],
        "sources": [
            "stage-2/components.json",
            "stage-4/stories.json",
            "stage-5/tasks.json",
        ],
    },
    "stage-8/test_plan.json": {
        "prompts": [("test_plan_generation", "stage-8-uat")],
        "sources": ["stage-4/stories.json"],
    },
    "stage-8/uat_results.json": {
        "prompts": [("test_execution", "stage-8-uat")],
        "sources": ["stage-8/test_plan.json"],
    },
}


def get_prompt_version(prompt_name: str, stage_dir: str) -> str:
    """Read `prompt_version` from a prompt's YAML frontmatter."""
    prompt_path = SKILLS / stage_dir / "prompts" / f"{prompt_name}.md"
    if not prompt_path.exists():
        return "unknown"
    text = prompt_path.read_text(encoding="utf-8")
    match = re.search(r'^prompt_version:\s*"([^"]+)"\s*$', text, re.MULTILINE)
    return match.group(1) if match else "unknown"


def resolve_artifact_path(arg: str) -> tuple[Path, str]:
    """Accept an absolute path, a path relative to repo root (e.g.
    `.agents/artifacts/stage-1/problem.json`), or one relative to
    `.agents/artifacts/` (e.g. `stage-1/problem.json`).

    Returns (absolute_path, key_for_mapping)."""
    p = Path(arg)
    if p.is_absolute():
        absolute = p
    elif arg.replace("\\", "/").startswith(".agents/"):
        absolute = (REPO_ROOT / arg).resolve()
    else:
        absolute = (ARTIFACTS / arg).resolve()
    try:
        key = str(absolute.relative_to(ARTIFACTS)).replace("\\", "/")
    except ValueError:
        key = arg
    return absolute, key


def main(arg: str) -> int:
    artifact_path, key = resolve_artifact_path(arg)
    if not artifact_path.exists():
        print(f"❌ Artifact not found: {artifact_path}", file=sys.stderr)
        return 1

    config = ARTIFACT_MAPPING.get(key)
    if config is None:
        print(f"ℹ️  No meta mapping for {key} — skipping (this is fine for "
              f"logs, snapshots, and other free-form artifacts)")
        return 0

    prompt_versions = {
        name: get_prompt_version(name, stage_dir)
        for name, stage_dir in config["prompts"]
    }
    source_artifacts = {src: ARTIFACTS / src for src in config["sources"]}
    missing = [src for src, p in source_artifacts.items() if not p.exists()]
    if missing:
        print(f"❌ Source artifacts missing for {key}: {missing}", file=sys.stderr)
        return 1

    new_meta = build_meta(prompt_versions, source_artifacts)

    with open(artifact_path) as f:
        data = json.load(f)
    data["meta"] = new_meta
    with open(artifact_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"✅ Injected meta into {key}")
    print(f"   prompts: {prompt_versions}")
    print(f"   {len(source_artifacts)} source(s) hashed")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python inject_meta.py <path-to-artifact>", file=sys.stderr)
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
