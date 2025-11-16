#!/bin/bash
# Sentrix Backend - Test Runner Script
# Script para ejecutar tests con coverage

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🧪 Sentrix Backend - Test Runner${NC}"
echo -e "${CYAN}=================================${NC}\n"

# Parse arguments
TEST_TYPE="all"
COVERAGE=true
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit)
            TEST_TYPE="unit"
            shift
            ;;
        --integration)
            TEST_TYPE="integration"
            shift
            ;;
        --api)
            TEST_TYPE="api"
            shift
            ;;
        --smoke)
            TEST_TYPE="smoke"
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: ./run_tests.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --unit           Run only unit tests"
            echo "  --integration    Run only integration tests"
            echo "  --api            Run only API tests"
            echo "  --smoke          Run only smoke tests"
            echo "  --no-coverage    Run without coverage"
            echo "  --verbose        Verbose output"
            echo "  --help           Show this help"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -vv"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=html --cov-report=term-missing"
fi

# Add markers based on test type
case $TEST_TYPE in
    unit)
        PYTEST_CMD="$PYTEST_CMD -m unit"
        echo -e "${YELLOW}Running UNIT tests...${NC}\n"
        ;;
    integration)
        PYTEST_CMD="$PYTEST_CMD -m integration"
        echo -e "${YELLOW}Running INTEGRATION tests...${NC}\n"
        ;;
    api)
        PYTEST_CMD="$PYTEST_CMD -m api"
        echo -e "${YELLOW}Running API tests...${NC}\n"
        ;;
    smoke)
        PYTEST_CMD="$PYTEST_CMD -m smoke"
        echo -e "${YELLOW}Running SMOKE tests...${NC}\n"
        ;;
    all)
        echo -e "${YELLOW}Running ALL tests...${NC}\n"
        ;;
esac

# Run tests
eval $PYTEST_CMD

# Capture exit code
EXIT_CODE=$?

echo ""
echo -e "${CYAN}=================================${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Tests PASSED${NC}"
else
    echo -e "${RED}❌ Tests FAILED${NC}"
fi

if [ "$COVERAGE" = true ]; then
    echo -e "${CYAN}📊 Coverage report: htmlcov/index.html${NC}"
fi

echo -e "${CYAN}=================================${NC}\n"

exit $EXIT_CODE
