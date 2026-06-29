#!/usr/bin/env pwsh
# UAT-036 batchmode runner (no GUI): EditMode + PlayMode in one session
param(
    [string]$UnityExe = "D:\Unity Editor\2022.3.62f3c1\Editor\Unity.exe"
)

$ErrorActionPreference = "Stop"
$proj = (Get-Item -LiteralPath "$PSScriptRoot\..\..\..").FullName
$lock = Join-Path $proj "Temp\UnityLockfile"

function Clear-ShenRenShiBuLock {
    Get-Process Unity -ErrorAction SilentlyContinue | ForEach-Object {
        $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)" -ErrorAction SilentlyContinue).CommandLine
        if ($cmd -and $cmd -like "*$proj*") {
            Write-Host "Stopping Unity PID $($_.Id)"
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
    if (Test-Path $lock) {
        Remove-Item -LiteralPath $lock -Force -ErrorAction SilentlyContinue
    }
}

if (-not (Test-Path $UnityExe)) {
    Write-Error "Unity not found: $UnityExe"
}

Clear-ShenRenShiBuLock

$log = Join-Path $proj "Logs\uat036-batch-exec.log"
$args = @(
    "-batchmode",
    "-nographics",
    "-projectPath", $proj,
    "-executeMethod", "_01_Scripts.Editor.Uat036BatchTestRunner.RunAll",
    "-logFile", $log
)
Write-Host "Running UAT-036 batchmode (EditMode -> PlayMode)..."
$p = Start-Process -FilePath $UnityExe -ArgumentList $args -PassThru -Wait -NoNewWindow
Write-Host "Exit code: $($p.ExitCode)"
if (Test-Path $log) {
    Select-String -Path $log -Pattern "UAT-036 batch" | Select-Object -Last 15 | ForEach-Object { $_.Line }
}
exit $p.ExitCode
