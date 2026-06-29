#!/usr/bin/env pwsh
param(
    [int]$TimeoutSeconds = 900
)

$ErrorActionPreference = "Stop"
$proj = (Get-Item -LiteralPath "$PSScriptRoot\..\..\..").FullName
$request = Join-Path $proj "Temp\uat036-run.request"
$result = Join-Path $proj "Temp\uat036-run.result"
$tempDir = Join-Path $proj "Temp"

if (-not (Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
}

if (Test-Path $result) { Remove-Item -LiteralPath $result -Force }
Set-Content -LiteralPath $request -Value (Get-Date).ToString("O") -Encoding UTF8
Write-Host "Request: $request"
Write-Host "Waiting for result (max ${TimeoutSeconds}s)..."

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $deadline) {
    if (Test-Path $result) {
        $text = Get-Content -LiteralPath $result -Raw
        Write-Host "Result: $text"
        if ($text -match '^PASS') { exit 0 }
        exit 1
    }
    Start-Sleep -Seconds 2
}

Write-Host "Timeout: no result at $result"
exit 2
