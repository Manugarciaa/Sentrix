# Sentrix Backend - Test Runner Script (Windows PowerShell)
# Script para ejecutar tests con coverage

param(
    [switch]$Unit,
    [switch]$Integration,
    [switch]$Api,
    [switch]$Smoke,
    [switch]$NoCoverage,
    [switch]$Verbose,
    [switch]$Help
)

Write-Host "🧪 Sentrix Backend - Test Runner" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

if ($Help) {
    Write-Host "Usage: .\run_tests.ps1 [OPTIONS]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor White
    Write-Host "  -Unit          Run only unit tests" -ForegroundColor Gray
    Write-Host "  -Integration   Run only integration tests" -ForegroundColor Gray
    Write-Host "  -Api           Run only API tests" -ForegroundColor Gray
    Write-Host "  -Smoke         Run only smoke tests" -ForegroundColor Gray
    Write-Host "  -NoCoverage    Run without coverage" -ForegroundColor Gray
    Write-Host "  -Verbose       Verbose output" -ForegroundColor Gray
    Write-Host "  -Help          Show this help" -ForegroundColor Gray
    exit 0
}

# Build pytest command
$pytestCmd = "pytest"

if ($Verbose) {
    $pytestCmd += " -vv"
}

if (-not $NoCoverage) {
    $pytestCmd += " --cov=src --cov-report=html --cov-report=term-missing"
}

# Add markers based on test type
if ($Unit) {
    $pytestCmd += " -m unit"
    Write-Host "Running UNIT tests...`n" -ForegroundColor Yellow
}
elseif ($Integration) {
    $pytestCmd += " -m integration"
    Write-Host "Running INTEGRATION tests...`n" -ForegroundColor Yellow
}
elseif ($Api) {
    $pytestCmd += " -m api"
    Write-Host "Running API tests...`n" -ForegroundColor Yellow
}
elseif ($Smoke) {
    $pytestCmd += " -m smoke"
    Write-Host "Running SMOKE tests...`n" -ForegroundColor Yellow
}
else {
    Write-Host "Running ALL tests...`n" -ForegroundColor Yellow
}

# Run tests
Invoke-Expression $pytestCmd
$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan

if ($exitCode -eq 0) {
    Write-Host "✅ Tests PASSED" -ForegroundColor Green
}
else {
    Write-Host "❌ Tests FAILED" -ForegroundColor Red
}

if (-not $NoCoverage) {
    Write-Host "📊 Coverage report: htmlcov\index.html" -ForegroundColor Cyan
}

Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

exit $exitCode
