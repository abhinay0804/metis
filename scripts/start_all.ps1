# Open two PowerShell windows and start both backend and frontend with live logs
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = "C:\Optiv Security"
$backendScript = Join-Path $root "scripts\start_backend.ps1"
$frontendScript = Join-Path $root "scripts\start_frontend.ps1"

if (-not (Test-Path $backendScript)) { throw "Missing $backendScript" }
if (-not (Test-Path $frontendScript)) { throw "Missing $frontendScript" }

# Start backend window
Start-Process -FilePath pwsh -ArgumentList "-NoExit -Command & '"+$backendScript+"'" | Out-Null

# Start frontend window
Start-Process -FilePath pwsh -ArgumentList "-NoExit -Command & '"+$frontendScript+"'" | Out-Null

Write-Host "Launched two PowerShell windows: backend and frontend."
