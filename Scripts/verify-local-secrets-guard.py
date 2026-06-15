#!/usr/bin/env python3
"""Fail if local-secret path patterns appear in Git index or under Docs/."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Keep in sync with Docs/00-规范/禁写层-本地说明.md §第四条
BLOCKED_PATH_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(^|/)Docs-local(/|$)", re.IGNORECASE),
    re.compile(r"/SET-EMB-[0-9]", re.IGNORECASE),
    re.compile(r"^SET-EMB-[0-9]", re.IGNORECASE),
)


def matches_blocked(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(p.search(normalized) for p in BLOCKED_PATH_PATTERNS)


def git_tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print("WARN: git ls-files failed; skipping index check", file=sys.stderr)
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def scan_docs_tree() -> list[str]:
    docs = ROOT / "Docs"
    if not docs.is_dir():
        return []
    hits: list[str] = []
    for path in docs.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if matches_blocked(rel):
            hits.append(rel)
    return hits


def main() -> int:
    errors: list[str] = []

    for rel in git_tracked_files():
        if matches_blocked(rel):
            errors.append(f"tracked by Git (must be ignored): {rel}")

    for rel in scan_docs_tree():
        errors.append(f"blocked path under Docs/: {rel}")

    if errors:
        print("Local secrets guard FAILED:", file=sys.stderr)
        for item in errors:
            print(f"  - {item}", file=sys.stderr)
        print(
            "See Docs/00-规范/禁写层-本地说明.md §第四条",
            file=sys.stderr,
        )
        return 1

    print("OK: no blocked local-secret paths in Git index or Docs/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
