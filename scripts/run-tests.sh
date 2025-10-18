#!/bin/bash
# Run All Tests with Coverage

set -e

echo "================================"
echo "Sentrix Test Suite"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "Error: Must run from project root (Sentrix/)"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source backend/venv/bin/activate || . backend/venv/Scripts/activate

# Set test environment
export ENVIRONMENT=testing
export LOG_LEVEL=WARNING

cd backend

echo ""
echo "Running tests..."
echo ""

# Run tests with coverage
pytest tests/ -v \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=70

echo ""
echo "================================"
echo "Test Summary"
echo "================================"
echo ""
echo "Coverage report generated in: backend/htmlcov/index.html"
echo ""
echo "Test breakdown:"
echo "  - Phase 0: Timeouts, Secret Validation, Exception Handling, Health Checks"
echo "  - Phase 1: Structured Logging, Circuit Breaker, Celery Tasks"
echo ""
