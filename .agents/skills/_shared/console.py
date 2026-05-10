"""
Stdio configuration helper for verify scripts.

Why this exists
---------------
Every verify script prints status with unicode characters (e.g. ✅ / ❌ / ⚠️).
On Windows, Python's default stdout encoding is cp1252, which cannot encode
those characters — the script crashes with `UnicodeEncodeError` partway
through its output, sometimes during the very `except` block that's trying to
print the original error. Subprocess captures (CI, the smoke test, anything
running verify scripts via `subprocess.run`) hit this hardest because the
captured pipe forces the cp1252 codec.

Setting `PYTHONIOENCODING=utf-8` in the environment fixes the symptom but
relies on every caller to remember. This helper fixes it in-process so the
verify scripts work the same on any platform regardless of how they're
invoked.

Usage
-----
At the very top of a verify script, after `sys.path.insert(...)` adds
`_shared/`:

    from console import setup as setup_console
    setup_console()

Idempotent — safe to call multiple times.
"""

import sys


def setup() -> None:
    """Force stdout/stderr to UTF-8 if the runtime gave us a narrower codec."""
    for stream in (sys.stdout, sys.stderr):
        try:
            encoding = getattr(stream, "encoding", None)
            if encoding and encoding.lower().replace("-", "") != "utf8":
                if hasattr(stream, "reconfigure"):
                    stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            # Reconfiguring is best-effort; if it fails (closed stream,
            # detached buffer, exotic runtime), the script continues with
            # whatever encoding the runtime gave us.
            pass
