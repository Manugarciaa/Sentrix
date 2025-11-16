#!/bin/bash
# Show Sentrix System Status

echo "=================================="
echo "   SENTRIX SYSTEM STATUS"
echo "=================================="
echo ""

# Check Python
echo "📦 Python:"
python --version 2>/dev/null || echo "  ✗ Python not found"
echo ""

# Check Redis
echo "🔴 Redis:"
if redis-cli ping > /dev/null 2>&1; then
    echo "  ✓ Running"
    redis-cli info server | grep "redis_version" | sed 's/redis_version:/  Version: /'
else
    echo "  ✗ Not running (run: redis-server)"
fi
echo ""

# Check Backend
echo "🌐 Backend API:"
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "  ✓ Running at http://localhost:8000"
    echo "  📚 Docs: http://localhost:8000/docs"
else
    echo "  ✗ Not running"
fi
echo ""

# Check Celery Worker
echo "⚙️  Celery Worker:"
if pgrep -f "celery.*worker" > /dev/null; then
    echo "  ✓ Running"
    WORKERS=$(pgrep -f "celery.*worker" | wc -l)
    echo "  Workers: $WORKERS"
else
    echo "  ✗ Not running (run: ./scripts/start-celery-worker.sh)"
fi
echo ""

# Check Flower
echo "🌸 Flower Monitoring:"
if curl -s http://localhost:5555 > /dev/null 2>&1; then
    echo "  ✓ Running at http://localhost:5555"
else
    echo "  ✗ Not running (optional - run: ./scripts/start-flower.sh)"
fi
echo ""

# Check Health Endpoints
echo "🏥 Health Checks:"
if curl -s http://localhost:8000/api/v1/health/ready > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/api/v1/health/ready)
    if echo "$HEALTH" | grep -q "ready"; then
        echo "  ✓ All systems operational"
    else
        echo "  ⚠ Some services unavailable"
    fi
else
    echo "  ✗ Cannot check (backend not running)"
fi
echo ""

# Circuit Breaker Status
echo "🔄 Circuit Breaker:"
if curl -s http://localhost:8000/api/v1/health/circuit-breakers > /dev/null 2>&1; then
    CB_STATE=$(curl -s http://localhost:8000/api/v1/health/circuit-breakers | grep -o '"state":"[^"]*"' | cut -d'"' -f4)
    if [ "$CB_STATE" = "closed" ]; then
        echo "  ✓ State: Closed (Normal)"
    elif [ "$CB_STATE" = "open" ]; then
        echo "  ⚠ State: Open (YOLO service unavailable)"
    else
        echo "  ℹ State: $CB_STATE"
    fi
else
    echo "  ✗ Cannot check"
fi
echo ""

# Test Results
echo "🧪 Tests:"
if [ -f "backend/.coverage" ]; then
    echo "  ✓ Tests have been run"
    echo "  📊 Coverage report: backend/htmlcov/index.html"
else
    echo "  ℹ Run: ./scripts/run-tests.sh"
fi
echo ""

# Phase Status
echo "📈 Implementation Progress:"
echo "  Phase 0 (Critical):  ████████████████████████████ 100% (4/4) ✅"
echo "  Phase 1 (High):      ████████████████████████████ 100% (4/4) ✅"
echo "  Phase 2 (Medium):    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% (0/3)"
echo "  Phase 3 (Long):      ░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0% (0/4)"
echo ""
echo "  Overall:             ███████████████░░░░░░░░░░░░░  53% (8/15)"
echo ""

echo "=================================="
echo "✅ Phase 1 Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Review PHASE_1_COMPLETE.md"
echo "  2. Test async endpoints"
echo "  3. Monitor in Flower UI"
echo "  4. Run full test suite"
echo ""
