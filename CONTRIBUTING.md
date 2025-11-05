# Contributing to Migochat 🤝

First off, thank you for considering contributing to Migochat! It's people like you that make Migochat such a great tool.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Git Commit Messages](#git-commit-messages)

---

## 📜 Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inspiring community for all.

### Our Standards

- ✅ Using welcoming and inclusive language
- ✅ Being respectful of differing viewpoints and experiences
- ✅ Gracefully accepting constructive criticism
- ✅ Focusing on what is best for the community
- ✅ Showing empathy towards other community members

---

## 🎯 How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check existing issues to avoid duplicates.

**When submitting a bug report, include:**
- Clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and logs
- Screenshots if applicable

**Template:**
```markdown
**Bug Description:**
[Clear description of the bug]

**Steps to Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Environment:**
- OS: [e.g., Windows 11]
- Python: [e.g., 3.13.2]
- Version: [e.g., 0.2.0]

**Additional Context:**
[Any other relevant information]
```

---

### Suggesting Features 💡

Feature suggestions are welcome! Please:
- Use a clear and descriptive title
- Provide detailed description of the proposed feature
- Explain why this feature would be useful
- Include examples or mockups if applicable

**Template:**
```markdown
**Feature Request:**
[Clear title]

**Description:**
[Detailed description of the feature]

**Use Case:**
[Why this feature is needed]

**Proposed Solution:**
[How you think this should work]

**Alternatives Considered:**
[Other solutions you've thought about]
```

---

### Contributing Code 💻

1. **Fork the Repository**
   ```bash
   git clone https://github.com/Yoans-Adel/Migochat.git
   cd Migochat
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make Your Changes**
   - Follow our coding standards
   - Add tests for new features
   - Update documentation

4. **Test Your Changes**
   ```bash
   pytest tests/ --cov=app --cov-report=html
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.13.2 or higher
- pip (Python package manager)
- Virtual environment tool
- Git

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Yoans-Adel/Migochat.git
   cd Migochat
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment:**
   ```bash
   # Windows
   .venv\Scripts\activate

   # Linux/Mac
   source .venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r tests/requirements-test.txt
   ```

5. **Setup environment variables:**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   ```

6. **Run tests:**
   ```bash
   pytest tests/ --tb=short -v
   ```

7. **Start development server:**
   ```bash
   python run.py
   ```

---

## 📝 Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

#### Type Hints (Required ✅)
```python
from typing import Dict, List, Optional, Any

def process_message(
    message: str,
    user_id: int,
    metadata: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Process incoming message."""
    pass
```

#### Docstrings (Required ✅)
```python
def calculate_lead_score(user: User, message: str) -> int:
    """
    Calculate lead score based on user activity.
    
    Args:
        user: User object with activity history
        message: Current message text
        
    Returns:
        int: Lead score between 0-100
        
    Raises:
        ValueError: If user is None
    """
    pass
```

#### Naming Conventions
- **Classes:** `PascalCase` (e.g., `MessengerService`)
- **Functions/Methods:** `snake_case` (e.g., `send_message`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)
- **Private methods:** `_snake_case` (e.g., `_validate_data`)

#### Code Organization
```python
# 1. Standard library imports
import logging
from datetime import datetime

# 2. Third-party imports
from fastapi import APIRouter
from sqlalchemy import func

# 3. Local imports
from app.services import MessengerService
from database import User, Message
```

#### Error Handling
```python
# Good ✅
try:
    result = process_data(data)
    return {"success": True, "data": result}
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    return {"success": False, "error": str(e)}
except Exception as e:
    logger.exception("Unexpected error")
    raise

# Bad ❌
try:
    result = process_data(data)
except:
    pass  # Silent failure
```

---

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── test_server.py              # Server integration tests
├── test_messaging/             # Messaging service tests
│   ├── test_messenger.py
│   └── test_whatsapp.py
├── test_ai/                    # AI service tests
│   └── test_gemini.py
└── test_business/              # Business logic tests
    ├── test_leads.py
    └── test_keywords.py
```

### Writing Tests

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch

class TestMessengerService:
    def test_send_message_success(self):
        """Test successful message sending."""
        service = MessengerService()
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            
            result = service.send_message("123", "Hello")
            
            assert result["success"] is True
            mock_post.assert_called_once()
```

#### Integration Tests
```python
def test_message_flow_end_to_end(test_client, test_db):
    """Test complete message processing flow."""
    # 1. Receive webhook
    response = test_client.post(
        "/webhook/messenger",
        json={"entry": [{"messaging": [...]}]}
    )
    assert response.status_code == 200
    
    # 2. Verify database
    message = test_db.query(Message).first()
    assert message is not None
    
    # 3. Verify response sent
    # ...
```

### Test Coverage Requirements

- **New Features:** 80%+ coverage
- **Bug Fixes:** Add regression test
- **Critical Paths:** 100% coverage

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_server.py

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run with verbose output
pytest tests/ -v

# Run failed tests only
pytest tests/ --lf
```

---

## 🔄 Pull Request Process

### Before Submitting

- ✅ Code follows our style guide
- ✅ All tests pass
- ✅ New tests added for new features
- ✅ Documentation updated
- ✅ No breaking changes (or clearly documented)
- ✅ Commit messages follow our format

### PR Template

```markdown
## Description
[Clear description of changes]

## Type of Change
- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guide
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings

## Related Issues
Fixes #123
Related to #456
```

### Review Process

1. **Automated Checks:** CI/CD runs tests
2. **Code Review:** Maintainer reviews code
3. **Feedback:** Address review comments
4. **Approval:** Maintainer approves PR
5. **Merge:** Squash and merge to main

---

## 📝 Git Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat:** New feature
- **fix:** Bug fix
- **docs:** Documentation changes
- **style:** Code style changes (formatting)
- **refactor:** Code refactoring
- **test:** Adding or updating tests
- **chore:** Maintenance tasks

### Examples

```bash
# Feature
git commit -m "feat(messaging): add WhatsApp template support"

# Bug fix
git commit -m "fix(leads): correct lead score calculation"

# Documentation
git commit -m "docs(api): update API endpoint documentation"

# With body
git commit -m "feat(ai): add Gemini multimodal support

- Add image processing capability
- Implement video analysis
- Update AI response handler

Closes #123"
```

---

## 📚 Additional Resources

### Documentation
- [Project Status](./PROJECT_STATUS.md)
- [Changelog](./CHANGELOG.md)
- [README](./README.md)

### External Links
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 🤝 Community

### Getting Help

- **GitHub Issues:** For bugs and feature requests
- **Discussions:** For questions and ideas
- **Email:** yoans@example.com (replace with actual email)

### Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to Migochat! 🎉**

*Last Updated: November 5, 2025*
