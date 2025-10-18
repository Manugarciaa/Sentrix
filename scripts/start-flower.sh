#!/bin/bash
# Start Flower - Celery Monitoring UI

set -e

echo "================================"
echo "Flower - Celery Monitoring UI"
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

# Set environment variables
export REDIS_URL=${REDIS_URL:-redis://localhost:6379/0}

echo ""
echo "================================"
echo "Configuration:"
echo "  Redis: $REDIS_URL"
echo "  Web UI: http://localhost:5555"
echo "================================"
echo ""

# Check if Redis is running
echo "Checking Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is running"
else
    echo "✗ Redis is not running!"
    echo "  Start Redis first: redis-server"
    exit 1
fi

cd backend

echo ""
echo "Starting Flower..."
echo "Access at: http://localhost:5555"
echo "Press Ctrl+C to stop"
echo ""

# Start Flower
celery -A src.celery_app flower --port=5555
