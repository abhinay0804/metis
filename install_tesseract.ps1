# PowerShell script to install Tesseract OCR on Windows
# This script downloads and installs Tesseract OCR for image text extraction

Write-Host "Installing Tesseract OCR for image text extraction..." -ForegroundColor Green

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This script needs to run as Administrator to install Tesseract." -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Manual Installation Steps:" -ForegroundColor Cyan
    Write-Host "1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki"
    Write-Host "2. Install the .exe file"
    Write-Host "3. Add Tesseract to your PATH environment variable"
    Write-Host "4. Restart your terminal/IDE"
    exit 1
}

# Check if Tesseract is already installed
try {
    $tesseractVersion = & tesseract --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Tesseract is already installed:" -ForegroundColor Green
        Write-Host $tesseractVersion
        exit 0
    }
}
catch {
    # Tesseract not found, continue with installation
}

# Check if winget is available (Windows Package Manager)
try {
    $wingetVersion = & winget --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installing Tesseract using winget..." -ForegroundColor Yellow
        & winget install --id UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Tesseract installed successfully via winget!" -ForegroundColor Green
            Write-Host "Please restart your terminal/IDE to use OCR functionality." -ForegroundColor Yellow
            exit 0
        }
    }
}
catch {
    # winget not available, try other methods
}

# Check if Chocolatey is available
try {
    $chocoVersion = & choco --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installing Tesseract using Chocolatey..." -ForegroundColor Yellow
        & choco install tesseract -y
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Tesseract installed successfully via Chocolatey!" -ForegroundColor Green
            Write-Host "Please restart your terminal/IDE to use OCR functionality." -ForegroundColor Yellow
            exit 0
        }
    }
}
catch {
    # Chocolatey not available
}

# Manual download method
Write-Host "Package managers not available. Attempting manual download..." -ForegroundColor Yellow

$downloadUrl = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
$installerPath = "$env:TEMP\tesseract-installer.exe"

try {
    Write-Host "Downloading Tesseract installer..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
    
    Write-Host "Running Tesseract installer..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait
    
    # Add to PATH if not already there
    $tesseractPath = "C:\Program Files\Tesseract-OCR"
    if (Test-Path $tesseractPath) {
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", [EnvironmentVariableTarget]::Machine)
        if ($currentPath -notlike "*$tesseractPath*") {
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$tesseractPath", [EnvironmentVariableTarget]::Machine)
            Write-Host "Added Tesseract to system PATH." -ForegroundColor Green
        }
    }
    
    # Clean up
    Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
    
    Write-Host "Tesseract installation completed!" -ForegroundColor Green
    Write-Host "Please restart your terminal/IDE to use OCR functionality." -ForegroundColor Yellow
    
} catch {
    Write-Host "Manual installation failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install manually:" -ForegroundColor Cyan
    Write-Host "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki"
    Write-Host "2. Install the .exe file"
    Write-Host "3. Add Tesseract to your PATH environment variable"
    Write-Host "4. Restart your terminal/IDE"
}
