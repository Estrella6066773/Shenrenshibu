#!/usr/bin/env python3
"""
设定设计文档库内部链接检查工具
检查所有 Markdown 文件中的内部链接是否有效
"""

import os
import re
import sys
import yaml
import argparse
from pathlib import Path
from typing import Set, List, Tuple, Optional

SCRIPT_DIR = Path(__file__).parent
DOCS_ROOT = SCRIPT_DIR.parent.parent
REGISTRY_PATH = DOCS_ROOT / "管理规则" / "id-registry.yaml"
MANIFEST_PATTERNS = [
    DOCS_ROOT / "玩家投放" / "v0.1" / "manifest.yaml",
    DOCS_ROOT / "玩家投放" / "v0.2" / "manifest.yaml",
    DOCS_ROOT / "玩家投放" / "v0.3" / "manifest.yaml",
]


def load_registry() -> dict:
    """加载 id 注册表"""
    if not REGISTRY_PATH.exists():
        return {"entries": []}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_registered_paths() -> Set[str]:
    """获取注册表中所有已登记的路径"""
    registry = load_registry()
    paths = set()
    for entry in registry.get("entries", []):
        path = entry.get("path", "")
        if path:
            paths.add(path)
    return paths


def get_all_markdown_files() -> List[Path]:
    """获取所有 Markdown 文件"""
    md_files = []
    for root, _, files in os.walk(DOCS_ROOT):
        for file in files:
            if file.endswith(".md"):
                md_files.append(Path(root) / file)
    return md_files


def extract_links(content: str) -> List[Tuple[str, int]]:
    """从内容中提取所有 Markdown 链接"""
    links = []
    for line_num, line in enumerate(content.split("\n"), 1):
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.finditer(pattern, line)
        for match in matches:
            link_text = match.group(1)
            link_url = match.group(2)
            if not link_url.startswith(("http://", "https://", "mailto:", "#")):
                links.append((link_url, line_num))
    return links


def resolve_link(base_file: Path, link_path: str) -> Optional[Path]:
    """解析相对链接为绝对路径"""
    if "#" in link_path:
        link_path = link_path.split("#")[0]

    if link_path.startswith("/"):
        return None

    if not link_path.endswith(".md"):
        link_path += ".md"

    resolved = (base_file.parent / link_path).resolve()
    return resolved


def check_links_in_file(file_path: Path, fix: bool = False) -> List[Tuple[str, int, str]]:
    """检查单个文件中的所有链接"""
    errors = []

    if not file_path.exists():
        return [(str(file_path), 0, "FILE_NOT_FOUND")]

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    links = extract_links(content)

    for link_url, line_num in links:
        resolved = resolve_link(file_path, link_url)

        if resolved is None:
            errors.append((str(file_path), line_num, f"Absolute path link: {link_url}"))
            continue

        if not resolved.exists():
            errors.append((str(file_path), line_num, f"Broken link: {link_url} -> {resolved}"))

    return errors


def check_all_links(fix: bool = False, quiet: bool = False) -> bool:
    """检查所有链接"""
    md_files = get_all_markdown_files()
    all_errors = []

    for md_file in md_files:
        errors = check_links_in_file(md_file, fix)
        all_errors.extend(errors)

    if all_errors:
        if not quiet:
            print("=" * 60)
            print("LINK CHECK FAILED")
            print("=" * 60)
            for file_path, line_num, error_msg in all_errors:
                rel_path = os.path.relpath(file_path, DOCS_ROOT)
                print(f"{rel_path}:{line_num}: {error_msg}")
            print("=" * 60)
            print(f"Total errors: {len(all_errors)}")
        return False
    else:
        if not quiet:
            print("All links are valid.")
        return True


def stage_fixed_files(errors: List[Tuple[str, int, str]]):
    """暂存已修复的文件（用于 git 钩子）"""
    import subprocess

    files_to_stage = set()
    for file_path, _, _ in errors:
        files_to_stage.add(file_path)

    for file_path in files_to_stage:
        try:
            subprocess.run(
                ["git", "add", file_path],
                cwd=DOCS_ROOT,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            pass


def main():
    parser = argparse.ArgumentParser(description="检查设定设计文档库中的内部链接")
    parser.add_argument("--fix", action="store_true", help="自动修复链接（目前仅报告错误）")
    parser.add_argument("--stage-fixed", action="store_true", help="修复后暂存文件")
    parser.add_argument("--quiet", action="store_true", help="静默模式，仅返回退出码")
    args = parser.parse_args()

    if not REGISTRY_PATH.exists():
        print(f"Warning: Registry not found at {REGISTRY_PATH}", file=sys.stderr)

    success = check_all_links(fix=args.fix, quiet=args.quiet)

    if not success and not args.quiet:
        sys.exit(1)
    elif not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
