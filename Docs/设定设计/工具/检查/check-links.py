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

# 不以 .md 解析的资源扩展名
NON_MD_EXTENSIONS = {
    ".yaml", ".yml", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg",
    ".py", ".ps1", ".sh", ".mdc", ".json", ".pdf",
}

# 已知待入库资源（相对 设定设计/）；缺失时不阻塞钩子
PENDING_ASSET_SUFFIXES: set[str] = set()

# 模板占位：URL 或显示名命中则跳过（非真实互引）
PLACEHOLDER_URL_MARKERS = (
    "链接", "链接1", "链接2", "链接3",
    "文档路径", "文档路径.md",
    "显示文本", "显示文字",
    "CHR-示例角色1.md", "CHR-示例角色2.md",
    "CHR-关联角色1.md", "CHR-关联角色2.md",
)

PLACEHOLDER_URL_RE = re.compile(
    r"(\[角色编号\]|\[英文名\]|\[链接\d*\]|相对路径/)"
)


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
            link_url = match.group(2)
            if not link_url.startswith(("http://", "https://", "mailto:", "#")):
                links.append((link_url, line_num))
    return links


def is_placeholder_link(link_url: str) -> bool:
    """模板占位链接，不参与有效性校验"""
    if link_url in PLACEHOLDER_URL_MARKERS:
        return True
    if "[" in link_url or "]" in link_url:
        return True
    if PLACEHOLDER_URL_RE.search(link_url):
        return True
    return False


def path_exists(link_path: Path) -> bool:
    """目标路径是否存在（文件、目录或目录内 README）"""
    if link_path.exists():
        return True
    if link_path.is_dir():
        return (link_path / "README.md").exists() or True
    parent = link_path.parent
    if parent.exists() and parent.is_dir() and link_path.name == "README.md":
        return (parent / "README.md").exists()
    return False


def resolve_link(base_file: Path, link_url: str) -> Tuple[Optional[Path], str]:
    """
    解析相对链接。返回 (解析路径, 模式说明)；None 表示跳过校验。
    """
    link_path = link_url
    if "#" in link_path:
        link_path = link_path.split("#")[0]
    link_path = link_path.strip()

    if not link_path:
        return None, "anchor-only"

    if link_path.startswith("/"):
        return None, "absolute-skip"

    if link_path.startswith("../") and ".cursor/" in link_path:
        return None, "local-cursor-rule"

    if is_placeholder_link(link_path):
        return None, "placeholder"

    suffix = Path(link_path).suffix.lower()

    if suffix in NON_MD_EXTENSIONS:
        resolved = (base_file.parent / link_path).resolve()
        return resolved, "asset"

    if link_path.endswith("/"):
        resolved = (base_file.parent / link_path).resolve()
        if resolved.is_dir():
            return resolved, "directory"
        if (resolved / "README.md").exists():
            return resolved / "README.md", "directory-readme"
        return resolved, "directory-missing"

    # 显式 .md 或需补 .md
    if not link_path.endswith(".md"):
        md_candidate = (base_file.parent / (link_path + ".md")).resolve()
        if md_candidate.exists():
            return md_candidate, "markdown"
        dir_candidate = (base_file.parent / link_path).resolve()
        if dir_candidate.is_dir():
            readme = dir_candidate / "README.md"
            if readme.exists():
                return readme, "directory-readme"
            return dir_candidate, "directory"
        return md_candidate, "markdown"

    resolved = (base_file.parent / link_path).resolve()
    return resolved, "markdown"


def check_links_in_file(file_path: Path, fix: bool = False) -> List[Tuple[str, int, str]]:
    """检查单个文件中的所有链接"""
    errors = []

    if not file_path.exists():
        return [(str(file_path), 0, "FILE_NOT_FOUND")]

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    links = extract_links(content)

    for link_url, line_num in links:
        resolved, mode = resolve_link(file_path, link_url)

        if resolved is None:
            continue

        if mode == "asset":
            if not resolved.exists():
                try:
                    rel = resolved.relative_to(DOCS_ROOT.resolve())
                    if rel.as_posix() in PENDING_ASSET_SUFFIXES:
                        continue
                except ValueError:
                    pass
                errors.append((str(file_path), line_num, f"Broken link: {link_url} -> {resolved}"))
            continue

        if mode.startswith("directory"):
            if resolved.exists():
                continue
            errors.append((str(file_path), line_num, f"Broken link: {link_url} -> {resolved}"))
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

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
