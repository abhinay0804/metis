# Start backend API (FastAPI/Uvicorn) in this window with live logs
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Move to project root
Set-Location "C:\Optiv Security"

# Enable local dev bypass for auth
$env:ALLOW_DEV_BYPASS = '1'

# Use the project venv python
$python = "C:\Optiv Security\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  Write-Error "Python venv not found at $python"
  exit 1
}

# Run the server
& $python "run_server.py"
