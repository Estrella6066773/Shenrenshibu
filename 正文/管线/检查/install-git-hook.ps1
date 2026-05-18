# 在仓库任意子目录运行：启用唯一 pre-commit，并停用 .git/hooks 下的旧副本
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    $root = (git -C "../../.." rev-parse --show-toplevel 2>$null)
    if (-not $root) {
        $root = git rev-parse --show-toplevel 2>$null
    }
    if (-not $root) { throw "请在 ShenrenshibuStoryLib 仓库内运行此脚本" }
    Set-Location $root

    git config core.hooksPath "正文/管线/检查"

    $legacy = Join-Path $root ".git\hooks\pre-commit"
    if (Test-Path $legacy) {
        @"
#!/bin/sh
# 已停用：提交前检查统一由 core.hooksPath=正文/管线/检查/pre-commit 负责。
exit 0
"@ | Set-Content -Path $legacy -Encoding utf8NoBOM
        Write-Host "已停用 .git/hooks/pre-commit（避免与 hooksPath 重复执行）"
    }

    Write-Host "已设置 core.hooksPath = 正文/管线/检查"
    Write-Host "提交时：仅当暂存区含 正文/*.md 时运行一次；成功时静默（--quiet）"
    Write-Host "跳过：git commit --no-verify  或  `$env:SKIP_CANON_LINK_CHECK=1"
} finally {
    Pop-Location
}
