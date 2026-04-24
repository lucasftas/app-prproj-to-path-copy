# Build pipeline: PyInstaller (onedir) -> Inno Setup (.exe instalador).
#
# Pre-requisitos:
#   - Python 3.12+ com PyInstaller instalado (pip install pyinstaller)
#   - Inno Setup 6 em C:\Users\<USER>\AppData\Local\Programs\Inno Setup 6\ISCC.exe
#
# Uso:
#   & ".\scripts\build_release.ps1"
#
# Saida:
#   dist\prproj-to-path-copy\           : bundle portatil (onedir)
#   dist\installer\prproj-to-path-copy-0.1.0-setup.exe : instalador final

# IMPORTANTE: nao usar $ErrorActionPreference='Stop' — PyInstaller escreve
# INFO/WARNING no stderr e o PS 5.1 interpretaria como erro fatal. Aqui a
# deteccao de falha e feita apenas via $LASTEXITCODE, que e o que importa.

$root = Split-Path -Parent $PSScriptRoot
Push-Location $root

Write-Host "=== 1. Limpando builds anteriores ===" -ForegroundColor Cyan
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist")  { Remove-Item -Recurse -Force "dist" }

Write-Host ""
Write-Host "=== 2. PyInstaller (gera dist/prproj-to-path-copy/) ===" -ForegroundColor Cyan
python -m PyInstaller `
    --name "prproj-to-path-copy" `
    --windowed `
    --noconfirm `
    --clean `
    --icon "assets\icon.ico" `
    --add-data "assets\icon.ico;assets" `
    "src\app.py"

if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Write-Host "PyInstaller falhou (exit $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== 3. Inno Setup (gera dist/installer/*-setup.exe) ===" -ForegroundColor Cyan
$iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) {
    Pop-Location
    Write-Host "ISCC.exe nao encontrado em $iscc - instalar Inno Setup 6" -ForegroundColor Red
    exit 1
}
& $iscc "installer\installer.iss"

if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Write-Host "Inno Setup falhou (exit $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== BUILD OK ===" -ForegroundColor Green
$setup = Get-ChildItem -Path "dist\installer" -Filter "*-setup.exe" | Select-Object -First 1
if ($setup) {
    $sizeMB = [math]::Round($setup.Length / 1MB, 2)
    Write-Host ("Instalador: {0} ({1} MB)" -f $setup.FullName, $sizeMB) -ForegroundColor Green
}
Pop-Location
