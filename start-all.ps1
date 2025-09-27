# PowerShell script to start all Sentrix services
Write-Host "=========================================" -ForegroundColor Green
Write-Host "SENTRIX - Iniciando todos los servicios" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Check if we're in the correct directory
if (!(Test-Path "backend")) {
    Write-Host "Error: No se encuentra la carpeta 'backend'. Asegurate de ejecutar este script desde la raiz del proyecto." -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}

if (!(Test-Path "yolo-service")) {
    Write-Host "Error: No se encuentra la carpeta 'yolo-service'. Asegurate de ejecutar este script desde la raiz del proyecto." -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}

if (!(Test-Path "frontend")) {
    Write-Host "Error: No se encuentra la carpeta 'frontend'. Asegurate de ejecutar este script desde la raiz del proyecto." -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}

Write-Host ""
Write-Host "[1/3] Iniciando Backend Service (Puerto 8000)..." -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[2/3] Iniciando YOLO Service (Puerto 8001)..." -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd yolo-service; python server.py"

# Wait a moment for YOLO service to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[3/3] Iniciando Frontend (Puerto 3000)..." -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "TODOS LOS SERVICIOS INICIADOS" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Backend:   http://localhost:8000 (Docs: http://localhost:8000/docs)" -ForegroundColor Cyan
Write-Host "YOLO:      http://localhost:8001 (Docs: http://localhost:8001/docs)" -ForegroundColor Cyan
Write-Host "Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para detener los servicios, cierra las ventanas de terminal abiertas"
Write-Host "o presiona Ctrl+C en cada ventana."
Write-Host "=========================================" -ForegroundColor Green

Read-Host "Presiona Enter para cerrar esta ventana"