# Sentrix - Docker Start Script (Windows PowerShell)
# Inicio rápido de todos los servicios con Docker

Write-Host "🐳 Sentrix - Docker Startup Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "📋 Verificando Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERROR: Docker no está corriendo" -ForegroundColor Red
    Write-Host "   Por favor inicia Docker Desktop y vuelve a intentar" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker está corriendo" -ForegroundColor Green
Write-Host ""

# Check if .env exists
Write-Host "📋 Verificando configuración..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Archivo .env no encontrado" -ForegroundColor Yellow
    Write-Host "   Copiando .env.docker a .env..." -ForegroundColor Yellow
    Copy-Item ".env.docker" ".env"
    Write-Host "✅ Archivo .env creado" -ForegroundColor Green
} else {
    Write-Host "✅ Archivo .env encontrado" -ForegroundColor Green
}
Write-Host ""

# Ask user what to do
Write-Host "🚀 ¿Qué deseas hacer?" -ForegroundColor Cyan
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
        Write-Host "🔨 Building y starting todos los servicios..." -ForegroundColor Yellow
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d

        Write-Host ""
        Write-Host "⏳ Esperando que la base de datos esté lista..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10

        Write-Host ""
        Write-Host "🔄 Ejecutando migraciones..." -ForegroundColor Yellow
        docker-compose exec -T backend alembic upgrade head

        Write-Host ""
        Write-Host "✅ TODO LISTO!" -ForegroundColor Green
    }
    "2" {
        Write-Host ""
        Write-Host "🚀 Iniciando servicios..." -ForegroundColor Yellow
        docker-compose up -d

        Write-Host ""
        Write-Host "✅ Servicios iniciados!" -ForegroundColor Green
    }
    "3" {
        Write-Host ""
        Write-Host "🛑 Parando servicios..." -ForegroundColor Yellow
        docker-compose down

        Write-Host ""
        Write-Host "✅ Servicios detenidos!" -ForegroundColor Green
    }
    "4" {
        Write-Host ""
        Write-Host "📜 Mostrando logs (Ctrl+C para salir)..." -ForegroundColor Yellow
        docker-compose logs -f
    }
    "5" {
        Write-Host ""
        Write-Host "⚠️  ADVERTENCIA: Esto eliminará TODA la base de datos" -ForegroundColor Red
        $confirm = Read-Host "¿Estás seguro? (escribe 'SI' para confirmar)"

        if ($confirm -eq "SI") {
            Write-Host ""
            Write-Host "🗑️  Eliminando todo..." -ForegroundColor Red
            docker-compose down -v
            docker system prune -f

            Write-Host ""
            Write-Host "✅ Todo eliminado. Usa opción 1 para reiniciar" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "❌ Cancelado" -ForegroundColor Yellow
        }
    }
    default {
        Write-Host ""
        Write-Host "❌ Opción inválida" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "📊 Estado de los servicios:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "🌐 URLs de los servicios:" -ForegroundColor Cyan
Write-Host "   Backend API:    http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:       http://localhost:8000/docs" -ForegroundColor White
Write-Host "   YOLO Service:   http://localhost:8001" -ForegroundColor White
Write-Host "   Frontend:       http://localhost:3000" -ForegroundColor White
Write-Host "   PostgreSQL:     localhost:5432" -ForegroundColor White
Write-Host "   Redis:          localhost:6379" -ForegroundColor White

Write-Host ""
Write-Host "💡 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   Ver logs:       docker-compose logs -f" -ForegroundColor White
Write-Host "   Ver estado:     docker-compose ps" -ForegroundColor White
Write-Host "   Parar todo:     docker-compose down" -ForegroundColor White
Write-Host "   Reiniciar:      docker-compose restart" -ForegroundColor White

Write-Host ""
Write-Host "🎉 ¡Listo para desarrollar!" -ForegroundColor Green
