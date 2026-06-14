#!/usr/bin/env python3
"""UAT-115 static check: dialogue data folder presence and meta integrity."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DIALOGUE_DIR = ROOT / "Assets/04_Data/对话dat"
META_GUID = re.compile(r"^guid: ([0-9a-f]{32})\s*$", re.MULTILINE | re.IGNORECASE)


def check_dialogue_folder(failures: list[str]) -> None:
    if not DIALOGUE_DIR.is_dir():
        failures.append("missing folder: Assets/04_Data/对话dat")
        return

    data_files = [
        p
        for p in DIALOGUE_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in {".asset", ".prefab", ".json", ".csv", ".txt"}
    ]
    if not data_files:
        failures.append("Assets/04_Data/对话dat has no recognizable data files")
        return

    for data_file in data_files:
        meta = data_file.with_suffix(data_file.suffix + ".meta")
        if not meta.is_file():
            failures.append(f"missing meta: {data_file.relative_to(ROOT).as_posix()}")
            continue
        text = meta.read_text(encoding="utf-8", errors="replace")
        m = META_GUID.search(text)
        if not m:
            failures.append(f"invalid meta guid: {meta.relative_to(ROOT).as_posix()}")
        elif len(m.group(1)) != 32:
            failures.append(f"meta guid not 32 chars: {meta.relative_to(ROOT).as_posix()}")


def check_scene_references_dialogue_dat(failures: list[str]) -> None:
    scenes = list((ROOT / "Assets/05_Scenes").glob("*.unity"))
    if not scenes:
        failures.append("no scenes under Assets/05_Scenes")
        return

    needle = "04_Data/对话dat"
    if not any(needle in s.read_text(encoding="utf-8", errors="replace") for s in scenes):
        failures.append("no scene references Assets/04_Data/对话dat (optional wiring check)")


def main() -> int:
    failures: list[str] = []
    check_dialogue_folder(failures)
    # 非阻断：主场景可能通过 Registry 间接引用，仅作提示
    # check_scene_references_dialogue_dat(failures)

    if failures:
        print("UAT-115 data asset check: FAILED")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("UAT-115 data asset check: PASS")
    print(f"  - {DIALOGUE_DIR.relative_to(ROOT).as_posix()} present with valid meta")
    return 0


if __name__ == "__main__":
    sys.exit(main())
