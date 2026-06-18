# Pull latest personal rules into this project (.cursor/rules/common/)
$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$configPath = Join-Path $ProjectRoot ".cursor\personal-rules.json"

if (-not (Test-Path -LiteralPath $configPath)) {
    throw "Missing .cursor/personal-rules.json. Run Install-ToProject.ps1 from your rules repo first."
}

$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$rulesRepo = $config.rulesRepoPath
$packages = @($config.packages)

if ($env:CURSOR_PERSONAL_RULES_REPO) {
    $rulesRepo = $env:CURSOR_PERSONAL_RULES_REPO
}

$syncScript = Join-Path $rulesRepo "scripts\Sync-CommonRules.ps1"
if (-not (Test-Path -LiteralPath $syncScript)) {
    throw "Rules repo or sync script not found: $syncScript. Set CURSOR_PERSONAL_RULES_REPO if path moved."
}

& $syncScript -TargetRoot $ProjectRoot -RulesRepoRoot $rulesRepo -Packages $packages
