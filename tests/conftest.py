"""
Pytest Configuration and Fixtures
Shared fixtures for all tests
"""

import pytest
import os
import sys
import uuid
from pathlib import Path
from typing import Generator, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after adding to path
from Server.config import settings
from database import Base, get_engine
from Server.main import app


# ==================== Fixtures ====================

@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine"""
    # Use in-memory SQLite for testing
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(test_db_engine) -> Generator[TestClient, None, None]:
    """Create FastAPI test client with test database"""
    # Create session factory for test database
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )
    
    def override_get_session():
        """Override get_session to use test database"""
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    # Import and override the get_session dependency
    from database import get_session
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def test_settings() -> Dict[str, Any]:
    """Test configuration settings"""
    return {
        "FB_APP_ID": os.getenv("FB_APP_ID", "test_app_id"),
        "FB_APP_SECRET": os.getenv("FB_APP_SECRET", "test_secret"),
        "FB_PAGE_ACCESS_TOKEN": os.getenv("FB_PAGE_ACCESS_TOKEN", "test_token"),
        "WHATSAPP_ACCESS_TOKEN": os.getenv("WHATSAPP_ACCESS_TOKEN", "test_token"),
        "WHATSAPP_PHONE_NUMBER_ID": os.getenv("WHATSAPP_PHONE_NUMBER_ID", "123456"),
        "WHATSAPP_VERIFY_TOKEN": os.getenv("WHATSAPP_VERIFY_TOKEN", "test_verify"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", "test_gemini_key"),
    }


@pytest.fixture(scope="function")
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing"""
    return {
        "facebook_id": "test_facebook_123",
        "name": "Test User",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+201234567890",
        "email": "test@example.com"
    }


@pytest.fixture(scope="function")
def sample_message_data() -> Dict[str, Any]:
    """Sample message data for testing"""
    return {
        "message_id": "test_msg_123",
        "text": "مرحبا، أريد الاستفسار عن المنتجات",
        "platform": "messenger",
        "direction": "incoming"
    }


@pytest.fixture(scope="function")
def sample_webhook_payload() -> Dict[str, Any]:
    """Sample webhook payload for testing"""
    return {
        "object": "page",
        "entry": [{
            "id": "page_id",
            "time": 1234567890,
            "messaging": [{
                "sender": {"id": "user_id_123"},
                "recipient": {"id": "page_id"},
                "timestamp": 1234567890,
                "message": {
                    "mid": "msg_id_123",
                    "text": "Hello, test message"
                }
            }]
        }]
    }


@pytest.fixture(scope="function")
def mock_whatsapp_response():
    """Mock WhatsApp API response"""
    return {
        "messaging_product": "whatsapp",
        "contacts": [{
            "input": "+201234567890",
            "wa_id": "201234567890"
        }],
        "messages": [{
            "id": "wamid.test123"
        }]
    }


@pytest.fixture(scope="function")
def mock_messenger_response():
    """Mock Messenger API response"""
    return {
        "recipient_id": "user_id_123",
        "message_id": "msg_id_123"
    }


@pytest.fixture(scope="function")
def mock_gemini_response():
    """Mock Gemini AI response"""
    return {
        "text": "مرحبا! كيف يمكنني مساعدتك اليوم؟",
        "candidates": [{
            "content": {
                "parts": [{
                    "text": "مرحبا! كيف يمكنني مساعدتك اليوم؟"
                }]
            }
        }]
    }


# ==================== Test Database Helpers ====================

@pytest.fixture(scope="function")
def create_test_user(db_session):
    """Helper to create test users"""
    from database import User
    
    def _create_user(**kwargs):
        # Generate unique psid if not provided
        if "psid" not in kwargs:
            kwargs["psid"] = f"test_{uuid.uuid4().hex[:12]}"
        
        defaults = {
            "first_name": "Test",
            "last_name": "User",
            "platform": "facebook"
        }
        defaults.update(kwargs)
        user = User(**defaults)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    return _create_user


@pytest.fixture(scope="function")
def create_test_message(db_session, create_test_user):
    """Helper to create test messages"""
    from database import Message, MessageDirection, MessageStatus
    
    def _create_message(**kwargs):
        # Create user if not provided
        if "user_id" not in kwargs:
            user = create_test_user()
            kwargs["user_id"] = user.id
        
        # Generate unique facebook_message_id if not provided
        if "facebook_message_id" not in kwargs:
            kwargs["facebook_message_id"] = f"test_msg_{uuid.uuid4().hex[:12]}"
        
        defaults = {
            "sender_id": "sender_123",
            "recipient_id": "page_123",
            "message_text": "Test message",
            "direction": MessageDirection.INBOUND,
            "status": MessageStatus.DELIVERED,
            "platform": "messenger"
        }
        defaults.update(kwargs)
        message = Message(**defaults)
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        return message
    
    return _create_message


@pytest.fixture(scope="function")
def create_test_conversation(db_session, create_test_user):
    """Helper to create test conversations"""
    from database import Conversation
    
    def _create_conversation(**kwargs):
        if "user_id" not in kwargs:
            user = create_test_user()
            kwargs["user_id"] = user.id
        
        # Conversation doesn't have platform field
        conversation = Conversation(**kwargs)
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        return conversation
    
    return _create_conversation


# ==================== Cleanup ====================

@pytest.fixture(autouse=True)
def reset_app_state():
    """Reset app state between tests"""
    yield
    # Cleanup after each test
    app.dependency_overrides.clear()


# ==================== Marks ====================

def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
    config.addinivalue_line(
        "markers", "critical: Critical tests that must pass"
    )
