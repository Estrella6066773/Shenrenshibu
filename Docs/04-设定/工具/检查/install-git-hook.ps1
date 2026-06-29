# 将 Git hooksPath 指向本目录，使 pre-commit 在提交前检查设定设计链接
$ErrorActionPreference = "Stop"

$RepoRoot = git rev-parse --show-toplevel 2>$null
if (-not $RepoRoot) {
    Write-Error "Not inside a git repository."
}

$HookDir = Join-Path $RepoRoot "Docs\04-设定\工具\检查"
if (-not (Test-Path (Join-Path $HookDir "pre-commit"))) {
    Write-Error "pre-commit not found at $HookDir"
}

$RelativeHookDir = "Docs/04-设定/工具/检查"
git config core.hooksPath $RelativeHookDir

Write-Host "core.hooksPath = $RelativeHookDir"
Write-Host "Link check runs only when staged files include Docs/04-设定/*.md"
Write-Host "Skip once: git commit --no-verify  or  `$env:SKIP_CANON_LINK_CHECK=1"
