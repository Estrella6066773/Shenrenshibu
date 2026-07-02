#!/usr/bin/env python3
"""Static UAT preflight: code/scene/build checks without Unity Play."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "Assets"
SCENES = (
    ROOT / "Assets/05_Scenes/主场景.unity",
    ROOT / "Assets/05_Scenes/主场景_委托改进.unity",
)
TEMPLATE_DIR = ROOT / "Assets/04_Data/委托系统"
BUILD_SETTINGS = ROOT / "ProjectSettings/EditorBuildSettings.asset"
EDITMODE_TEST = ROOT / "Assets/01_Scripts/Tests/Editor/AssignmentDailyRefreshUat036EditModeTests.cs"
PLAYMODE_TEST = ROOT / "Assets/01_Scripts/Tests/PlayMode/AssignmentDailyRefreshUat036PlayModeTests.cs"
CORE_BUS_TEST = ROOT / "Assets/01_Scripts/Tests/PlayMode/CoreBusGateUat001PlayModeTests.cs"
CORE_LOOP_TEST = ROOT / "Assets/01_Scripts/Tests/PlayMode/CoreLoopUat010050112PlayModeTests.cs"
UAT011_EDITMODE = ROOT / "Assets/01_Scripts/Tests/Editor/CoreLoopUat011EditModeTests.cs"

PUBLISHER_GUID = "7a4e2f1b9c3d5e6f8091a2b3c4d5e6f7"
VERIFIER_GUID = "b8c9d0e1f2a3546576879abcdef01234"
ECONOMY_GUID = "0c85c88ca0834f340b476568180ae249"
EVENT_BUS_GUID = "a4146549165edc54dac65fc22f7742ed"
MAIN_SCENE_GUID = "fad4afe1aeae41f4b8bff47c7886e5c1"
MAIN_MENU_GUID = "57649e30a457d2f44a9035bf193ba6cc"
MAIN_MENU_CONTROLLER_GUID = "dd961827319a2d34faedf4e55a0058d9"
MAIN_MENU_SCENE = ROOT / "Assets/05_Scenes/主菜单.unity"
SAVE_COLLECTION_TEST = ROOT / "Assets/01_Scripts/Tests/PlayMode/SaveCollectionPlayModeTests.cs"
SCENE_FLOW_SETUP = ROOT / "Assets/01_Scripts/Editor/SceneFlowSetupMenu.cs"
DAILY_IDS = ("daily01", "daily02", "daily03")


def check_daily_scene(failures: list[str]) -> None:
    for scene in SCENES:
        rel = scene.relative_to(ROOT).as_posix()
        if not scene.is_file():
            failures.append(f"missing scene: {rel}")
            continue
        text = scene.read_text(encoding="utf-8")
        if PUBLISHER_GUID not in text:
            failures.append(f"{rel}: missing AssignmentDailyRefreshPublisher")
        if VERIFIER_GUID not in text:
            failures.append(f"{rel}: missing AssignmentDailyRefreshPlaymodeVerifier")
        if ECONOMY_GUID not in text:
            failures.append(f"{rel}: missing PlayerEconomySystem")
        if EVENT_BUS_GUID not in text:
            failures.append(f"{rel}: missing EventBusBootstrap")
        for daily_id in DAILY_IDS:
            if f"assignmentTemplateId: {daily_id}" not in text:
                failures.append(f"{rel}: registry missing {daily_id}")

    if not TEMPLATE_DIR.is_dir():
        failures.append("missing folder: Assets/04_Data/委托系统")
        return

    for daily_id in DAILY_IDS:
        needle = f"idPrefix: {daily_id}"
        if not any(needle in p.read_text(encoding="utf-8") for p in TEMPLATE_DIR.glob("*.asset")):
            failures.append(f"template asset missing idPrefix={daily_id}")


def check_build_settings(failures: list[str]) -> None:
    if not BUILD_SETTINGS.is_file():
        failures.append("missing ProjectSettings/EditorBuildSettings.asset")
        return
    text = BUILD_SETTINGS.read_text(encoding="utf-8")
    if MAIN_SCENE_GUID not in text:
        failures.append("Editor Build Settings missing 主场景 guid")

    if MAIN_MENU_GUID not in text:
        failures.append("Editor Build Settings missing 主菜单 guid")

    if MAIN_MENU_SCENE.is_file():
        if MAIN_MENU_GUID not in text.split("m_Scenes:")[1][:200] if "m_Scenes:" in text else "":
            failures.append("Build Settings index 0 不是主菜单场景")
    else:
        failures.append("missing scene: Assets/05_Scenes/主菜单.unity（请运行 神人事部/场景/安装主菜单场景）")


def check_main_menu_code(failures: list[str]) -> None:
    if not SCENE_FLOW_SETUP.is_file():
        failures.append("missing SceneFlowSetupMenu.cs")
    if not SAVE_COLLECTION_TEST.is_file():
        failures.append("missing SaveCollectionPlayModeTests.cs")

    main_menu_controller = ASSETS / "01_Scripts/Presentation/MainMenu/MainMenuController.cs"
    if not main_menu_controller.is_file():
        failures.append("missing MainMenuController.cs")

    game_scene_ids = ASSETS / "01_Scripts/Runtime/SceneFlow/GameSceneIds.cs"
    if not game_scene_ids.is_file():
        failures.append("missing GameSceneIds.cs")

    if MAIN_MENU_SCENE.is_file():
        text = MAIN_MENU_SCENE.read_text(encoding="utf-8")
        if MAIN_MENU_CONTROLLER_GUID not in text:
            failures.append("主菜单.unity: missing MainMenuController script")
        if "Canvas" not in text:
            failures.append("主菜单.unity: missing Canvas")
        if "EventSystem" not in text:
            failures.append("主菜单.unity: missing EventSystem")


def check_code_uat(failures: list[str]) -> None:
    if not ASSETS.is_dir():
        failures.append("missing Assets/")
        return

    cs_files = list(ASSETS.rglob("*.cs"))
    joined = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in cs_files)

    if "DisplayDialog" in joined:
        failures.append("Assets contains DisplayDialog (UAT Editor 链检)")

    if "SortSessionList" not in joined:
        failures.append("ChatUIManager.SortSessionList missing (REQ-MSG-005)")

    if "AssignmentDailyRefreshPublisher" not in joined:
        failures.append("AssignmentDailyRefreshPublisher missing")

    if "CollectTemplateIdsByBelongingKind" not in joined:
        failures.append("CollectTemplateIdsByBelongingKind missing")

    menu_ok = (
        'MenuItem("神人事部/' in joined
        and "AssignmentDailyRuntimeSetupMenu" in joined
        and "AssignmentUat036TestRunnerMenu" in joined
        and "Uat036BatchTestRunner" in joined
        and "Uat036TestCallbacks" in joined
    )
    if not menu_ok:
        failures.append("Editor 菜单 神人事部/ 或 UAT 入口不完整 (UAT-110~111)")

    if not PLAYMODE_TEST.is_file():
        failures.append("missing PlayMode test: AssignmentDailyRefreshUat036PlayModeTests.cs")
    else:
        play_text = PLAYMODE_TEST.read_text(encoding="utf-8")
        if "LoadSceneInPlayMode" not in play_text:
            failures.append("PlayMode test should use Editor LoadSceneInPlayMode fallback")

    if not CORE_BUS_TEST.is_file():
        failures.append("missing PlayMode test: CoreBusGateUat001PlayModeTests.cs")
    else:
        core_text = CORE_BUS_TEST.read_text(encoding="utf-8")
        for needle in ("UAT001_EventBusBootstrap", "UAT002_CreateBeforeGate", "UAT003_CreateAfterGate"):
            if needle not in core_text:
                failures.append(f"CoreBusGateUat001PlayModeTests missing {needle}")

    if not EDITMODE_TEST.is_file():
        failures.append("missing EditMode test: AssignmentDailyRefreshUat036EditModeTests.cs")

    if not UAT011_EDITMODE.is_file():
        failures.append("missing EditMode test: CoreLoopUat011EditModeTests.cs")
    else:
        uat011_text = UAT011_EDITMODE.read_text(encoding="utf-8")
        if "UAT011_PlayerEconomy_HasTaskSettlementIdempotencyGuard" not in uat011_text:
            failures.append("CoreLoopUat011EditModeTests missing UAT-011 guard check")

    if not CORE_LOOP_TEST.is_file():
        failures.append("missing PlayMode test: CoreLoopUat010050112PlayModeTests.cs")
    else:
        loop_text = CORE_LOOP_TEST.read_text(encoding="utf-8")
        for needle in ("UAT010_DayAdvance", "UAT050_ApplyStressDelta", "UAT112_AssignmentTestBootstrap"):
            if needle not in loop_text:
                failures.append(f"CoreLoopUat010050112PlayModeTests missing {needle}")


def check_docs_uat_record(failures: list[str]) -> None:
    record = ROOT / "Docs/03-程序设计/05-交付/交付-UAT执行记录.md"
    if not record.is_file():
        failures.append("missing 交付-UAT执行记录.md")


def main() -> int:
    failures: list[str] = []
    check_daily_scene(failures)
    check_build_settings(failures)
    check_main_menu_code(failures)
    check_code_uat(failures)
    check_docs_uat_record(failures)

    if failures:
        print("UAT PREFLIGHT FAILED")
        for item in failures:
            print(f"  - {item}")
        return 1

    print("UAT preflight: PASS")
    print("  - UAT-036a daily scene/registry/templates")
    print("  - UAT-110/111 Editor menu presence")
    print("  - REQ-MSG-005 SortSessionList")
    print("  - DisplayDialog zero")
    print("  - Build Settings 主场景")
    print("  - PlayMode/EditMode UAT-036 tests present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
