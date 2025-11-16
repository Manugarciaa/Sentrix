# Sentrix Backend Tests

Comprehensive test suite for the Sentrix Backend, similar in structure to the yolo-service tests but adapted for backend API testing.

## 🏗️ Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── test_models.py                 # Database models and enums tests
├── test_yolo_integration.py       # YOLO service integration utilities tests
├── test_yolo_service_client.py    # YOLO service client tests
├── test_api_endpoints.py          # API endpoint tests
├── test_complete_system.py        # Complete system integration tests
└── README.md                      # This file
```

## 🧪 Test Categories

### Unit Tests
- **`test_models.py`**: Database models, enums, relationships
- **`test_yolo_integration.py`**: YOLO response parsing and mapping

### Integration Tests
- **`test_yolo_service_client.py`**: HTTP client for YOLO service
- **`test_api_endpoints.py`**: FastAPI endpoint testing

### System Tests
- **`test_complete_system.py`**: End-to-end workflow testing

## 🚀 Running Tests

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --unit
python run_tests.py --api
python run_tests.py --system
```

### Individual Test Files
```bash
# Unit tests
pytest tests/test_models.py -v
pytest tests/test_yolo_integration.py -v

# Integration tests
pytest tests/test_yolo_service_client.py -v

# API tests
pytest tests/test_api_endpoints.py -v

# System tests
pytest tests/test_complete_system.py -v
```

### With Coverage
```bash
# Generate coverage report
python run_tests.py --coverage

# Or directly with pytest
pytest --cov=app --cov-report=html
```

## 📊 Test Markers

Tests are marked with pytest markers for better organization:

- `@pytest.mark.unit`: Fast unit tests
- `@pytest.mark.integration`: Integration tests (may be slower)
- `@pytest.mark.api`: API endpoint tests
- `@pytest.mark.database`: Tests requiring database
- `@pytest.mark.yolo`: Tests interacting with YOLO service

### Running by Markers
```bash
# Run only unit tests
pytest -m unit

# Run only API tests
pytest -m api

# Skip integration tests
pytest -m "not integration"
```

## 🔧 Test Configuration

### Fixtures (`conftest.py`)
- `db_session`: Clean database session for each test
- `client`: FastAPI test client
- `async_client`: Async test client
- `mock_yolo_service`: Mocked YOLO service responses
- `sample_image_data`: Sample image data for testing
- `sample_analysis_data`: Sample analysis data

### Environment Variables
Tests use a separate SQLite database and mock external services by default.

## 📝 Test Coverage

Target coverage: **80%** minimum

Coverage includes:
- [OK] Database models and relationships
- [OK] YOLO service integration
- [OK] API endpoints
- [OK] Error handling
- [OK] Request/response validation
- [OK] Authentication workflows
- [OK] GPS data processing

## 🏃‍♂️ Continuous Integration

Tests are designed to run in CI/CD environments:

```bash
# CI command
python run_tests.py --all
```

Outputs:
- Test results (console)
- Coverage report (HTML + XML)
- JUnit XML for CI systems

## 🧩 Test Data

### Mock YOLO Responses
The test suite includes realistic mock responses that match the actual YOLO service format:

```python
{
    "success": True,
    "detections": [
        {
            "class_id": 0,
            "class_name": "Basura",
            "confidence": 0.75,
            "risk_level": "MEDIO",
            "location": {"has_location": True, ...}
        }
    ],
    "risk_assessment": {"level": "MEDIO", ...}
}
```

### Sample Images
Tests use minimal valid JPEG headers for file upload testing without requiring actual image files.

## 🔍 Debugging Tests

### Verbose Output
```bash
pytest -v -s tests/test_api_endpoints.py
```

### Debug Specific Test
```bash
pytest -v -s tests/test_api_endpoints.py::TestAnalysisEndpoints::test_create_analysis_with_file
```

### With Debugger
```bash
pytest --pdb tests/test_models.py
```

## 🌐 Integration with YOLO Service

Some integration tests can run against a real YOLO service:

```bash
# Start your YOLO service on localhost:8001
cd ../yolo-service
python main.py

# Run integration tests
pytest -m integration
```

Tests gracefully skip if the YOLO service is not available.

## 📈 Performance Tests

Performance tests validate:
- Response times under load
- Memory usage patterns
- Concurrent request handling

```bash
python run_tests.py --performance
```

## 🛠️ Writing New Tests

### Test Naming Convention
- Files: `test_*.py`
- Classes: `Test*`
- Methods: `test_*`

### Example Test Structure
```python
class TestNewFeature:
    """Test new feature functionality"""

    def test_basic_functionality(self, client):
        """Test basic feature works"""
        response = client.get("/api/v1/new-feature")
        assert response.status_code == 200

    @pytest.mark.integration
    def test_integration_with_yolo(self, mock_yolo_service):
        """Test integration with YOLO service"""
        # Test implementation
        pass
```

## 📋 Pre-commit Checks

Before committing code, run:

```bash
# Full test suite with linting
python run_tests.py --all

# Quick checks
python run_tests.py --lint --unit
```

## 🎯 Test Goals

1. **Reliability**: Catch regressions early
2. **Documentation**: Tests as living documentation
3. **Confidence**: Safe refactoring and feature additions
4. **Quality**: Maintain high code standards

## 🤝 Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure >80% coverage for new code
3. Add appropriate test markers
4. Update this README if needed
5. Run full test suite before PR

---

For questions about testing, see the main project documentation or ask the team! 🚀