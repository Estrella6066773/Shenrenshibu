#!/usr/bin/env python3
"""
设定设计文档库链接检查 PowerShell 启动脚本
用于在 Windows 环境下启动监视脚本
"""

import os
import sys
import subprocess
import time
import re
from pathlib import Path
from typing import Set

SCRIPT_DIR = Path(__file__).parent
DOCS_ROOT = SCRIPT_DIR.parent.parent
CHECKER_SCRIPT = SCRIPT_DIR / "check-links.py"
WATCHER_SCRIPT = SCRIPT_DIR / "watch-links-idle.py"

IDLE_TIMEOUT = 30 * 60


def get_markdown_files() -> Set[str]:
    """获取当前所有 Markdown 文件"""
    md_files = set()
    for root, _, files in os.walk(DOCS_ROOT):
        for file in files:
            if file.endswith(".md"):
                md_files.add(str(Path(root) / file))
    return md_files


def check_for_changes(last_files: Set[str]) -> bool:
    """检查是否有文件变化"""
    current_files = get_markdown_files()
    if current_files != last_files:
        return True

    for file_path in current_files:
        try:
            mtime = os.path.getmtime(file_path)
            if time.time() - mtime < 60:
                return True
        except OSError:
            pass

    return False


def run_checker():
    """运行链接检查器"""
    try:
        result = subprocess.run(
            [sys.executable, str(CHECKER_SCRIPT)],
            cwd=DOCS_ROOT,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running checker: {e}", file=sys.stderr)
        return False


def main():
    print(f"Watching for markdown file changes in: {DOCS_ROOT}")
    print(f"Idle timeout: {IDLE_TIMEOUT // 60} minutes")
    print(f"Checker script: {CHECKER_SCRIPT}")
    print("-" * 60)

    last_files = get_markdown_files()
    last_activity = time.time()

    while True:
        time.sleep(60)

        if check_for_changes(last_files):
            last_activity = time.time()
            last_files = get_markdown_files()
            print(f"[{time.strftime('%H:%M:%S')}] File change detected, running checker...")
            success = run_checker()
            if success:
                print(f"[{time.strftime('%H:%M:%S')}] Check passed.")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Check failed.")
        else:
            idle_time = (time.time() - last_activity) / 60
            if idle_time >= IDLE_TIMEOUT / 60:
                print(f"[{time.strftime('%H:%M:%S')}] Idle timeout reached. Exiting.")
                break
            elif int(idle_time) % 5 == 0:
                print(f"[{time.strftime('%H:%M:%S')}] Still watching... (idle {int(idle_time)}/{IDLE_TIMEOUT // 60} min)")


if __name__ == "__main__":
    main()
