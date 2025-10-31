# 🧪 BWW Assistant - Test Suite

## 📋 Overview

Comprehensive test suite for BWW Assistant application covering:

- ✅ Unit Tests - Individual components
- ✅ Integration Tests - Component interactions
- ✅ API Tests - HTTP endpoints
- ✅ Database Tests - Data persistence
- ✅ Service Tests - External integrations

## 🚀 Quick Start

### Install Test Dependencies

```bash
pip install -r tests/requirements-test.txt
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=Server --cov=app --cov=database --cov-report=html
```

### Run Specific Test Categories

```bash
# Critical tests only
pytest -m critical

# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# Database tests
pytest -m database

# Service tests
pytest -m services

# API tests
pytest -m api
```

### Run Specific Test Files

```bash
# Configuration tests
pytest tests/test_config.py

# Database tests
pytest tests/test_database.py

# Server tests
pytest tests/test_server.py

# WhatsApp service tests
pytest tests/unit/test_whatsapp_service.py
```

## 📊 Test Structure

```Structure
tests/
├── conftest.py                    # Shared fixtures and configuration
├── pytest.ini                     # Pytest configuration
├── requirements-test.txt          # Test dependencies
│
├── test_config.py                 # ✅ Configuration tests
├── test_database.py               # ✅ Database models & operations
├── test_server.py                 # ✅ Server startup & endpoints
│
└── unit/                          # Unit tests
    ├── test_whatsapp_service.py   # ✅ WhatsApp Business API
    ├── test_messenger_service.py  # ✅ Facebook Messenger API
    └── test_gemini_service.py     # ✅ Google Gemini AI
```

## 🏷️ Test Markers

| Marker | Description | Command |
|--------|-------------|---------|
| `critical` | Must-pass tests | `pytest -m critical` |
| `unit` | Unit tests | `pytest -m unit` |
| `integration` | Integration tests | `pytest -m integration` |
| `e2e` | End-to-end tests | `pytest -m e2e` |
| `database` | Database tests | `pytest -m database` |
| `services` | Service layer tests | `pytest -m services` |
| `api` | API endpoint tests | `pytest -m api` |
| `config` | Configuration tests | `pytest -m config` |
| `slow` | Slow-running tests | `pytest -m "not slow"` (skip slow) |

## 📈 Coverage Reports

After running tests with coverage:

```bash
pytest --cov=Server --cov=app --cov=database --cov-report=html
```

Open coverage report:

```bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

## ✅ Test Categories

### 1. Configuration Tests (`test_config.py`)

- ✅ Configuration loading
- ✅ Environment variables
- ✅ API keys validation
- ✅ Database URL format
- ✅ Required settings presence

### 2. Database Tests (`test_database.py`)

- ✅ Database connection
- ✅ Table creation
- ✅ User model CRUD
- ✅ Message model operations
- ✅ Conversation tracking
- ✅ Lead activity logging
- ✅ Relationships & joins
- ✅ Transaction rollback
- ✅ Data integrity

### 3. Server Tests (`test_server.py`)

- ✅ Application startup
- ✅ Routes registration
- ✅ Static files serving
- ✅ Webhook verification
- ✅ API endpoints
- ✅ Dashboard pages
- ✅ Error handling (404, 405, 422)
- ✅ Database integration

### 4. Service Tests

#### WhatsApp Service (`test_whatsapp_service.py`)

- ✅ Service initialization
- ✅ Send text message
- ✅ Phone number validation
- ✅ Message formatting
- ✅ API error handling

#### Messenger Service (`test_messenger_service.py`)

- ✅ Service initialization
- ✅ Send text message
- ✅ Quick replies
- ✅ Button templates
- ✅ Message structure validation

#### Gemini AI Service (`test_gemini_service.py`)

- ✅ Service initialization
- ✅ Response generation
- ✅ Arabic text handling
- ✅ Prompt formatting
- ✅ Error handling

## 🔧 Configuration for Tests

### Environment Variables

Create `.env.test` file:

```env
# Facebook
FB_APP_ID=test_app_id
FB_APP_SECRET=test_secret
FB_PAGE_ACCESS_TOKEN=test_token
FB_VERIFY_TOKEN=test_verify

# WhatsApp
WHATSAPP_ACCESS_TOKEN=test_token
WHATSAPP_PHONE_NUMBER_ID=123456
WHATSAPP_VERIFY_TOKEN=test_verify

# Gemini AI
GEMINI_API_KEY=test_key

# Database (uses in-memory SQLite for tests)
DATABASE_URL=sqlite:///:memory:

# App
DEBUG=True
```

### Running Tests in CI/CD

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r tests/requirements-test.txt
    
    - name: Run tests
      run: pytest --cov --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 📝 Writing New Tests

### Test Template

```python
import pytest

@pytest.mark.unit
class TestMyFeature:
    """Test description"""
    
    def test_feature_works(self):
        """Test specific behavior"""
        # Arrange
        expected = "value"
        
        # Act
        result = my_function()
        
        # Assert
        assert result == expected
```

### Using Fixtures

```python
def test_with_database(db_session, create_test_user):
    """Test using database fixtures"""
    user = create_test_user(name="Test User")
    assert user.id is not None
```

### Mocking External APIs

```python
from unittest.mock import patch

@patch('requests.post')
def test_api_call(mock_post):
    """Test with mocked API"""
    mock_post.return_value.json.return_value = {"status": "ok"}
    result = call_api()
    assert result["status"] == "ok"
```

## 🎯 Best Practices

1. **Run tests before commit**

   ```bash
   pytest -m critical
   ```

2. **Check coverage regularly**

   ```bash
   pytest --cov --cov-report=term-missing
   ```

3. **Keep tests fast**
   - Use in-memory database
   - Mock external APIs
   - Skip slow tests in development

4. **Write descriptive test names**

   ```python
   def test_user_creation_with_valid_data_succeeds()
   def test_invalid_phone_number_raises_validation_error()
   ```

5. **One assertion per test** (when possible)

6. **Use fixtures for common setup**

7. **Test edge cases and error handling**

## 🐛 Debugging Tests

### Run single test with verbose output

```bash
pytest tests/test_config.py::TestServerConfig::test_config_import -vv
```

### Run with debugging

```bash
pytest --pdb  # Drop into debugger on failure
```

### Show print statements

```bash
pytest -s  # Show print() output
```

### Run failed tests only

```bash
pytest --lf  # Last failed
pytest --ff  # Failed first
```

## 📞 Support

For issues or questions about tests:

1. Check this README
2. Review test logs
3. Check fixture definitions in `conftest.py`
4. Contact development team

## 🎉 Test Success Criteria

✅ All critical tests pass
✅ Code coverage > 80%
✅ No test failures in CI/CD
✅ Performance tests within acceptable range

---
