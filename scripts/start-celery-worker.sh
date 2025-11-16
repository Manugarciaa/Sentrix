#!/bin/bash
# Start Celery Worker for Async Task Processing

set -e

echo "================================"
echo "Sentrix Celery Worker"
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
export ENVIRONMENT=${ENVIRONMENT:-development}
export LOG_LEVEL=${LOG_LEVEL:-INFO}
export REDIS_URL=${REDIS_URL:-redis://localhost:6379/0}
export YOLO_SERVICE_URL=${YOLO_SERVICE_URL:-http://localhost:8001}

echo ""
echo "================================"
echo "Configuration:"
echo "  Environment: $ENVIRONMENT"
echo "  Log Level: $LOG_LEVEL"
echo "  Redis: $REDIS_URL"
echo "  YOLO Service: $YOLO_SERVICE_URL"
echo "  Concurrency: 4 workers"
echo "  Queue: analysis"
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
echo "Starting Celery worker..."
echo "Press Ctrl+C to stop"
echo ""

# Start worker
celery -A src.celery_app worker \
    --loglevel=$LOG_LEVEL \
    --concurrency=4 \
    --queue=analysis \
    --max-tasks-per-child=50 \
    --prefetch-multiplier=1
