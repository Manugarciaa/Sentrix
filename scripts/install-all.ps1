# Script de instalación completa para Sentrix (Windows PowerShell)
# Instala todas las dependencias de backend, yolo-service, shared y frontend
# Ejecutar desde la raíz del proyecto: .\scripts\install-all.ps1

$ErrorActionPreference = "Stop"

Write-Host "=========================================="
Write-Host "Sentrix - Instalación Completa (Windows)"
Write-Host "=========================================="

# Cambiar a directorio raíz del proyecto
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptPath "..")

function Print-Step {
    param($Message)
    Write-Host "`n==> $Message" -ForegroundColor Blue
}

function Print-Success {
    param($Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Print-Error {
    param($Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# Verificar Python
Print-Step "Verificando Python..."
try {
    $pythonVersion = & python --version 2>&1
    Print-Success "Python encontrado: $pythonVersion"
} catch {
    Print-Error "Python no encontrado. Instale Python 3.8+ primero."
    exit 1
}

# Verificar Node.js
Print-Step "Verificando Node.js..."
try {
    $nodeVersion = & node --version 2>&1
    Print-Success "Node.js encontrado: $nodeVersion"
} catch {
    Print-Error "Node.js no encontrado. Instale Node.js 16+ primero."
    exit 1
}

# Guardar directorio raíz
$rootDir = Get-Location

# 1. Instalar Shared Library
Print-Step "Instalando Shared Library..."
Set-Location shared
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
Print-Success "Shared library instalada"
deactivate
Set-Location $rootDir

# 2. Instalar Backend
Print-Step "Instalando Backend..."
Set-Location backend
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ..\shared
Print-Success "Backend instalado"
deactivate
Set-Location $rootDir

# 3. Instalar YOLO Service
Print-Step "Instalando YOLO Service..."
Set-Location yolo-service
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
Print-Success "YOLO Service instalado"
deactivate
Set-Location $rootDir

# 4. Instalar Frontend
Print-Step "Instalando Frontend..."
Set-Location frontend
npm install
Print-Success "Frontend instalado"
Set-Location $rootDir

# Mensaje final
Write-Host ""
Write-Host "=========================================="
Write-Host "✓ Instalación completa exitosa" -ForegroundColor Green
Write-Host "=========================================="
Write-Host ""
Write-Host "Próximos pasos:"
Write-Host "1. Configura el archivo .env con tus credenciales"
Write-Host "   copy .env.example .env"
Write-Host ""
Write-Host "2. Inicia Redis (Docker):"
Write-Host "   docker run -d -p 6379:6379 --name sentrix-redis redis:7-alpine"
Write-Host ""
Write-Host "3. Ejecuta las migraciones de base de datos:"
Write-Host "   cd backend"
Write-Host "   .\venv\Scripts\activate"
Write-Host "   alembic upgrade head"
Write-Host ""
Write-Host "4. Inicia todos los servicios:"
Write-Host "   .\scripts\start-all.ps1"
Write-Host ""
