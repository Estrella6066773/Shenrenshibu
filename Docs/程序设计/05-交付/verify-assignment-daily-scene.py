#!/usr/bin/env python3
"""Static check: daily assignment publisher, verifier, and template pool in main scenes."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCENES = (
    ROOT / "Assets/05_Scenes/主场景.unity",
    ROOT / "Assets/05_Scenes/主场景_委托改进.unity",
)
TEMPLATE_DIR = ROOT / "Assets/04_Data/委托系统"
PUBLISHER_GUID = "7a4e2f1b9c3d5e6f8091a2b3c4d5e6f7"
VERIFIER_GUID = "b8c9d0e1f2a3546576879abcdef01234"
ECONOMY_GUID = "0c85c88ca0834f340b476568180ae249"
DAILY_IDS = ("daily01", "daily02", "daily03")


def main() -> int:
    failures: list[str] = []

    for scene in SCENES:
        rel = scene.relative_to(ROOT).as_posix()
        if not scene.is_file():
            failures.append(f"missing scene: {rel}")
            continue

        text = scene.read_text(encoding="utf-8")
        if PUBLISHER_GUID not in text:
            failures.append(f"{rel}: missing AssignmentDailyRefreshPublisher guid")
        if VERIFIER_GUID not in text:
            failures.append(f"{rel}: missing AssignmentDailyRefreshPlaymodeVerifier guid")
        if ECONOMY_GUID not in text:
            failures.append(f"{rel}: missing PlayerEconomySystem guid")
        for daily_id in DAILY_IDS:
            if f"assignmentTemplateId: {daily_id}" not in text:
                failures.append(f"{rel}: registry missing {daily_id}")

    if not TEMPLATE_DIR.is_dir():
        failures.append(f"missing folder: {TEMPLATE_DIR.relative_to(ROOT).as_posix()}")
    else:
        for daily_id in DAILY_IDS:
            needle = f"idPrefix: {daily_id}"
            found = any(
                needle in asset.read_text(encoding="utf-8")
                for asset in TEMPLATE_DIR.glob("*.asset")
            )
            if not found:
                failures.append(f"template asset missing idPrefix={daily_id}")

    if failures:
        print("ASSIGNMENT DAILY SCENE CHECK FAILED")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("Assignment daily scene check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
