#!/bin/bash
# Start Backend in Development Mode with all Phase 1 features

set -e

echo "================================"
echo "Sentrix Backend - Development"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "Error: Must run from project root (Sentrix/)"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python -m venv venv
    cd ..
fi

# Activate virtual environment
echo "Activating virtual environment..."
source backend/venv/bin/activate || . backend/venv/Scripts/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
cd backend
pip install -r requirements.txt
pip install -e ../shared

# Set development environment variables
export ENVIRONMENT=development
export LOG_LEVEL=INFO
export REDIS_URL=${REDIS_URL:-redis://localhost:6379/0}
export YOLO_SERVICE_URL=${YOLO_SERVICE_URL:-http://localhost:8001}

echo ""
echo "================================"
echo "Configuration:"
echo "  Environment: $ENVIRONMENT"
echo "  Log Level: $LOG_LEVEL"
echo "  Redis: $REDIS_URL"
echo "  YOLO Service: $YOLO_SERVICE_URL"
echo "================================"
echo ""

# Check if Redis is running
echo "Checking Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is running"
else
    echo "⚠ Redis is not running. Start with: redis-server"
    echo "  Celery workers will not function without Redis."
fi

echo ""
echo "Starting backend server..."
echo "Access at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""

# Start the server
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
