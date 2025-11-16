# Sentrix - Docker Start Script (Windows PowerShell)
# Inicio rápido de todos los servicios con Docker

Write-Host "Sentrix - Docker Startup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[INFO] Verificando Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker no está corriendo" -ForegroundColor Red
    Write-Host "        Por favor inicia Docker Desktop y vuelve a intentar" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Docker está corriendo" -ForegroundColor Green
Write-Host ""

# Check if .env exists
Write-Host "[INFO] Verificando configuración..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "[WARN] Archivo .env no encontrado" -ForegroundColor Yellow
    Write-Host "       Copiando .env.docker a .env..." -ForegroundColor Yellow
    Copy-Item ".env.docker" ".env"
    Write-Host "[OK] Archivo .env creado" -ForegroundColor Green
} else {
    Write-Host "[OK] Archivo .env encontrado" -ForegroundColor Green
}
Write-Host ""

# Ask user what to do
Write-Host "¿Qué deseas hacer?" -ForegroundColor Cyan
Write-Host "1. Iniciar TODO (primera vez o después de cambios)" -ForegroundColor White
Write-Host "2. Iniciar servicios (uso normal)" -ForegroundColor White
Write-Host "3. Parar TODO" -ForegroundColor White
Write-Host "4. Ver logs" -ForegroundColor White
Write-Host "5. Resetear TODO (¡ELIMINA LA BASE DE DATOS!)" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "Selecciona una opción (1-5)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "[BUILD] Building y starting todos los servicios..." -ForegroundColor Yellow
        docker-compose -f ../docker-compose.yml down
        docker-compose -f ../docker-compose.yml build --no-cache
        docker-compose -f ../docker-compose.yml up -d

        Write-Host ""
        Write-Host "[WAIT] Esperando que la base de datos esté lista..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10

        Write-Host ""
        Write-Host "[MIGRATE] Ejecutando migraciones..." -ForegroundColor Yellow
        docker-compose -f ../docker-compose.yml exec -T backend alembic upgrade head

        Write-Host ""
        Write-Host "[OK] TODO LISTO!" -ForegroundColor Green
    }
    "2" {
        Write-Host ""
        Write-Host "[START] Iniciando servicios..." -ForegroundColor Yellow
        docker-compose -f ../docker-compose.yml up -d

        Write-Host ""
        Write-Host "[OK] Servicios iniciados!" -ForegroundColor Green
    }
    "3" {
        Write-Host ""
        Write-Host "[STOP] Parando servicios..." -ForegroundColor Yellow
        docker-compose -f ../docker-compose.yml down

        Write-Host ""
        Write-Host "[OK] Servicios detenidos!" -ForegroundColor Green
    }
    "4" {
        Write-Host ""
        Write-Host "[LOGS] Mostrando logs (Ctrl+C para salir)..." -ForegroundColor Yellow
        docker-compose -f ../docker-compose.yml logs -f
    }
    "5" {
        Write-Host ""
        Write-Host "[WARN] ADVERTENCIA: Esto eliminará TODA la base de datos" -ForegroundColor Red
        $confirm = Read-Host "¿Estás seguro? (escribe 'SI' para confirmar)"

        if ($confirm -eq "SI") {
            Write-Host ""
            Write-Host "[DELETE] Eliminando todo..." -ForegroundColor Red
            docker-compose -f ../docker-compose.yml down -v
            docker system prune -f

            Write-Host ""
            Write-Host "[OK] Todo eliminado. Usa opción 1 para reiniciar" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "[CANCEL] Cancelado" -ForegroundColor Yellow
        }
    }
    default {
        Write-Host ""
        Write-Host "[ERROR] Opción inválida" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Estado de los servicios:" -ForegroundColor Cyan
docker-compose -f ../docker-compose.yml ps

Write-Host ""
Write-Host "URLs de los servicios:" -ForegroundColor Cyan
Write-Host "   Backend API:    http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:       http://localhost:8000/docs" -ForegroundColor White
Write-Host "   YOLO Service:   http://localhost:8001" -ForegroundColor White
Write-Host "   Frontend:       http://localhost:3000" -ForegroundColor White
Write-Host "   PostgreSQL:     localhost:5432" -ForegroundColor White
Write-Host "   Redis:          localhost:6379" -ForegroundColor White

Write-Host ""
Write-Host "Comandos útiles:" -ForegroundColor Cyan
Write-Host "   Ver logs:       docker-compose -f ../docker-compose.yml logs -f" -ForegroundColor White
Write-Host "   Ver estado:     docker-compose -f ../docker-compose.yml ps" -ForegroundColor White
Write-Host "   Parar todo:     docker-compose -f ../docker-compose.yml down" -ForegroundColor White
Write-Host "   Reiniciar:      docker-compose -f ../docker-compose.yml restart" -ForegroundColor White

Write-Host ""
Write-Host "[OK] Listo para desarrollar!" -ForegroundColor Green
