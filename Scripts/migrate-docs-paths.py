#!/usr/bin/env python3
"""Update document paths after the numbered Docs directory migration."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = (
    ROOT / "Docs",
    ROOT / ".github",
    ROOT / "Scripts",
    ROOT / ".cursor" / "rules" / "local",
)
TEXT_SUFFIXES = {
    ".md",
    ".mdc",
    ".py",
    ".ps1",
    ".yml",
    ".yaml",
    ".json",
    ".txt",
}
REPLACEMENTS = (
    ("Docs/02-系统设计", "Docs/02-系统设计"),
    ("Docs/03-程序设计", "Docs/03-程序设计"),
    ("Docs/04-设定", "Docs/04-设定"),
    ("Docs\\系统设计", "Docs\\02-系统设计"),
    ("Docs\\程序设计", "Docs\\03-程序设计"),
    ("Docs\\设定设计", "Docs\\04-设定"),
    ("../02-系统设计/", "../02-系统设计/"),
    ("../03-程序设计/", "../03-程序设计/"),
    ("../04-设定/", "../04-设定/"),
    ("../../02-系统设计/", "../../02-系统设计/"),
    ("../../03-程序设计/", "../../03-程序设计/"),
    ("../../04-设定/", "../../04-设定/"),
    ("../../../02-系统设计/", "../../../02-系统设计/"),
    ("../../../03-程序设计/", "../../../03-程序设计/"),
    ("../../../04-设定/", "../../../04-设定/"),
    ("(02-系统设计/", "(02-系统设计/"),
    ("(03-程序设计/", "(03-程序设计/"),
    ("(04-设定/", "(04-设定/"),
    ("[02-系统设计/", "[02-系统设计/"),
    ("[03-程序设计/", "[03-程序设计/"),
    ("[04-设定/", "[04-设定/"),
    ("`02-系统设计/", "`02-系统设计/"),
    ("`03-程序设计/", "`03-程序设计/"),
    ("`04-设定/", "`04-设定/"),
    ("'02-系统设计/", "'02-系统设计/"),
    ("'03-程序设计/", "'03-程序设计/"),
    ("'04-设定/", "'04-设定/"),
    ('"02-系统设计/', '"02-系统设计/'),
    ('"03-程序设计/', '"03-程序设计/'),
    ('"04-设定/', '"04-设定/'),
)
REGEX_REPLACEMENTS = (
    (re.compile(r"(?<!02-)02-系统设计/"), "02-系统设计/"),
    (re.compile(r"(?<!03-)03-程序设计/"), "03-程序设计/"),
    (re.compile(r"(?<!04-)04-设定/"), "04-设定/"),
    (re.compile(r"(?<!02-)02-系统设计\\"), r"02-系统设计\\"),
    (re.compile(r"(?<!03-)03-程序设计\\"), r"03-程序设计\\"),
    (re.compile(r"(?<!04-)04-设定\\"), r"04-设定\\"),
)


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        if root.is_file():
            candidates = [root]
        else:
            candidates = [path for path in root.rglob("*") if path.is_file()]
        for path in candidates:
            if path.suffix.lower() in TEXT_SUFFIXES:
                files.append(path)
    return sorted(set(files))


def migrate_text(text: str) -> str:
    updated = text
    for old, new in REPLACEMENTS:
        updated = updated.replace(old, new)
    for pattern, new in REGEX_REPLACEMENTS:
        updated = pattern.sub(new, updated)
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report files that still need migration.")
    args = parser.parse_args()

    changed: list[Path] = []
    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        updated = migrate_text(text)
        if updated == text:
            continue

        changed.append(path)
        if not args.check:
            path.write_text(updated, encoding="utf-8", newline="")

    for path in changed:
        print(path.relative_to(ROOT).as_posix())

    if args.check and changed:
        print(f"{len(changed)} file(s) need path migration.")
        return 1

    print(f"{len(changed)} file(s) {'need' if args.check else 'updated by'} path migration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
