# Start backend API (FastAPI/Uvicorn) in this window with live logs
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Move to project root
Set-Location "C:\Metis"

# Enable local dev bypass for auth
$env:ALLOW_DEV_BYPASS = '1'

# Use the project venv python
$python = "C:\Metis\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  Write-Error "Python venv not found at $python"
  exit 1
}

# Run the server
& $python "run_server.py"
