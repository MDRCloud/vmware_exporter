# Build Script for VMware Exporter (Windows)

$ErrorActionPreference = "Stop"

# Add local WiX to PATH if present
if (Test-Path "wix") {
    $Env:PATH += ";$PSScriptRoot\wix"
}

Write-Host "Checking prerequisites..."
if (-not (Get-Command "pyinstaller" -ErrorAction SilentlyContinue)) {
    Write-Error "PyInstaller is not found. Please run: pip install pyinstaller"
}
if (-not (Get-Command "candle" -ErrorAction SilentlyContinue)) {
    Write-Error "WiX Toolset (candle.exe) is not found. Please install WiX Toolset or ensure 'wix' folder is present."
}

$SkipMSI = $false

Write-Host "Step 1: Installing Dependencies..."
pip install -r requirements.txt
# Ensure AntiGravity is installed or mock it if strictly internal
# pip install AntiGravity 

Write-Host "Step 2: Building EXE with PyInstaller..."
# usage of spec file
pyinstaller vmware_exporter.spec --clean --noconfirm

if (-not (Test-Path "dist\vmware_exporter.exe")) {
    Write-Error "Build failed. vmware_exporter.exe not found."
}

if (-not $SkipMSI) {
    Write-Host "Step 3: Compiling WiX Installer..."
    candle installer.wxs -out installer.wixobj
    if ($LASTEXITCODE -ne 0) { Write-Error "WiX compilation failed." }

    Write-Host "Step 4: Linking WiX Installer..."
    light installer.wixobj -out vmware_exporter.msi -ext WixUIExtension
    if ($LASTEXITCODE -ne 0) { Write-Error "WiX linking failed." }
} else {
    Write-Host "Skipping WiX steps."
}

Write-Host "Build Complete!"
Write-Host "Artifacts:"
Write-Host " - EXE: dist\vmware_exporter.exe"
if (-not $SkipMSI) {
    Write-Host " - MSI: vmware_exporter.msi"
}
