# Start frontend (Vite React) in this window with live logs
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Move to UI root
Set-Location "C:\Optiv Security\optiv-metis-ui\optiv-metis-data-craft-main"

# Start Vite dev server
npm run dev -- --host --port 5173
