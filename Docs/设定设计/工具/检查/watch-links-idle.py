#!/usr/bin/env python3
"""可选：编辑期后台监视「设定设计/」Markdown；无活动一段时间后自动退出。

默认不随仓库启动，不占用空闲资源。提交前仍以 git pre-commit 为准。

用法（仓库根目录）：
    python 设定设计/管线/检查/watch-links-idle.py
    python 设定设计/管线/检查/watch-links-idle.py --idle-minutes 30

检测逻辑（任一满足即视为「有活动」，重置空闲计时）：
  - 设定设计/ 下任意 .md 被保存（mtime 变化）
  - 本仓库发生新的 git 提交（HEAD 日志更新）

仅在有 .md 变更时运行 check-links（--quiet）；空闲超时后进程退出。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CANON_ROOT = SCRIPT_DIR.parents[1]
REPO_ROOT = CANON_ROOT.parent
CHECK_SCRIPT = SCRIPT_DIR / "check-links.py"
DEFAULT_IDLE_MIN = 30
DEFAULT_POLL_SEC = 30


def head_log_mtime() -> float:
    log = REPO_ROOT / ".git" / "logs" / "HEAD"
    if log.is_file():
        return log.stat().st_mtime
    return 0.0


def latest_md_mtime(root: Path) -> float:
    latest = 0.0
    for md in root.rglob("*.md"):
        try:
            latest = max(latest, md.stat().st_mtime)
        except OSError:
            pass
    return latest


def run_check(quiet: bool) -> int:
    cmd = [sys.executable, str(CHECK_SCRIPT)]
    if quiet:
        cmd.append("--quiet")
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="空闲自动退出的正文链接监视（可选）")
    parser.add_argument(
        "--idle-minutes",
        type=int,
        default=DEFAULT_IDLE_MIN,
        help=f"无活动多少分钟后退出（默认 {DEFAULT_IDLE_MIN}）",
    )
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=DEFAULT_POLL_SEC,
        help=f"轮询间隔秒数（默认 {DEFAULT_POLL_SEC}）",
    )
    parser.add_argument(
        "--no-quiet",
        action="store_true",
        help="检查时输出完整报告",
    )
    args = parser.parse_args()

    if not CANON_ROOT.is_dir():
        print(f"找不到正文目录：{CANON_ROOT}", file=sys.stderr)
        return 1

    idle_sec = max(1, args.idle_minutes) * 60
    poll = max(5, args.poll_seconds)
    quiet = not args.no_quiet

    last_md = latest_md_mtime(CANON_ROOT)
    last_head = head_log_mtime()
    last_activity = time.time()

    print(
        f"正文链接监视已启动：{args.idle_minutes} 分钟无保存/提交后自动退出；"
        f"每 {poll} 秒检查一次。Ctrl+C 可随时结束。",
        flush=True,
    )

    try:
        while True:
            time.sleep(poll)
            now = time.time()
            md = latest_md_mtime(CANON_ROOT)
            head = head_log_mtime()

            if md > last_md:
                last_md = md
                last_activity = now
                code = run_check(quiet)
                if code != 0 and quiet:
                    print("链接检查未通过，详见上方输出。", flush=True)
            elif head > last_head:
                last_head = head
                last_activity = now
                # 新提交：hook 已检查过，这里只重置空闲计时，不重复跑
            elif now - last_activity >= idle_sec:
                print(
                    f"已超过 {args.idle_minutes} 分钟无 Markdown 保存或提交，监视退出。",
                    flush=True,
                )
                return 0
    except KeyboardInterrupt:
        print("\n监视已手动结束。", flush=True)
        return 0


if __name__ == "__main__":
    sys.exit(main())
