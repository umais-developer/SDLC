"""
Stage 9 desktop-deploy verifier.

Validates `deployment_config.json` for `target == "desktop"`:
- desktop_targets[] is non-empty
- each installer_path exists on disk and matches installer_size_bytes
- each sha256 is a 64-char hex string and matches the file (when computable)
- each signature.verified is true and verify_command is non-empty

Usage:
    python .agents/skills/stage-9-deploy/verify/desktop_deploy.py \\
        .agents/artifacts/stage-9/deployment_config.json

Exit 0 = pass, exit 1 = fail. Failure messages go to stderr.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def fail(msg: str) -> "None":
    print(f"❌ [Stage 9] {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg: str) -> "None":
    print(f"⚠️  [Stage 9] {msg}")


def ok(msg: str) -> "None":
    print(f"✅ {msg}")


def load(path: Path) -> dict:
    if not path.exists():
        fail(f"deployment_config.json not found at {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"deployment_config.json is not valid JSON: {e}")
        return {}  # unreachable


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(config_path: str) -> "None":
    config = load(Path(config_path))
    target = config.get("target")
    if target != "desktop":
        fail(
            f"target is '{target}', expected 'desktop'. "
            "For 'web', use the GitHub Pages path in stage-9-deploy/SKILL.md (Path A)."
        )

    if not isinstance(config.get("version"), str) or not config["version"].strip():
        fail("'version' is required and must be a non-empty string")

    targets = config.get("desktop_targets")
    if not isinstance(targets, list) or len(targets) == 0:
        fail("'desktop_targets' must be a non-empty array")

    valid_os = {"macos", "windows", "linux"}
    seen_os: set[str] = set()
    repo_root = Path(config_path).resolve().parent.parent.parent.parent
    # ^ deployment_config.json -> stage-9 -> artifacts -> .agents -> repo_root

    for i, t in enumerate(targets):
        prefix = f"desktop_targets[{i}]"
        if not isinstance(t, dict):
            fail(f"{prefix} must be an object")

        os_name = t.get("os")
        if os_name not in valid_os:
            fail(f"{prefix}.os must be one of {sorted(valid_os)}, got '{os_name}'")
        if os_name in seen_os:
            warn(f"{prefix}.os '{os_name}' duplicates an earlier target")
        seen_os.add(os_name)

        ipath = t.get("installer_path")
        if not isinstance(ipath, str) or not ipath.strip():
            fail(f"{prefix}.installer_path must be a non-empty string")
        installer = repo_root / ipath
        if not installer.exists():
            fail(f"{prefix}.installer_path does not exist on disk: {ipath}")
        if not installer.is_file():
            fail(f"{prefix}.installer_path is not a regular file: {ipath}")

        size = t.get("installer_size_bytes")
        actual_size = installer.stat().st_size
        if not isinstance(size, int) or size <= 0:
            fail(f"{prefix}.installer_size_bytes must be a positive integer")
        if size != actual_size:
            fail(
                f"{prefix}.installer_size_bytes mismatch: claimed {size}, actual {actual_size}"
            )

        claimed_sha = t.get("sha256")
        if not isinstance(claimed_sha, str) or not SHA256_RE.fullmatch(claimed_sha.lower()):
            fail(f"{prefix}.sha256 must be a 64-char lowercase hex digest")
        # Compute and compare. This may be slow for large installers; acceptable for a single Stage 9 run.
        actual_sha = sha256_of(installer)
        if actual_sha.lower() != claimed_sha.lower():
            fail(
                f"{prefix}.sha256 mismatch: claimed {claimed_sha[:12]}..., actual {actual_sha[:12]}..."
            )

        sig = t.get("signature")
        if not isinstance(sig, dict):
            fail(f"{prefix}.signature must be an object")
        if sig.get("verified") is not True:
            fail(
                f"{prefix}.signature.verified must be true. Stage 9 will not approve "
                f"unsigned desktop installers. Sign before re-running."
            )
        method = sig.get("method")
        if not isinstance(method, str) or not method.strip():
            fail(f"{prefix}.signature.method must describe how the installer was signed")
        verify_cmd = sig.get("verify_command")
        if not isinstance(verify_cmd, str) or not verify_cmd.strip():
            fail(
                f"{prefix}.signature.verify_command must record the command used to verify "
                f"the signature (e.g. 'spctl --assess --type install <path>')"
            )

    # Advisory: version-vs-package.json check
    pkg = repo_root / "package.json"
    if pkg.exists():
        try:
            pkg_data = json.loads(pkg.read_text(encoding="utf-8"))
            pkg_version = pkg_data.get("version")
            if isinstance(pkg_version, str) and pkg_version != config["version"]:
                warn(
                    f"deployment_config.json#version '{config['version']}' does not match "
                    f"package.json#version '{pkg_version}'"
                )
        except (OSError, json.JSONDecodeError):
            pass

    ok(
        f"Stage 9 desktop-deploy verification PASSED: "
        f"{len(targets)} signed installer(s) across {sorted(seen_os)}"
    )


def main(argv: "list[str]") -> "None":
    if len(argv) != 2:
        print(
            "usage: python desktop_deploy.py <path-to-deployment_config.json>",
            file=sys.stderr,
        )
        sys.exit(2)
    verify(argv[1])


if __name__ == "__main__":
    main(sys.argv)
