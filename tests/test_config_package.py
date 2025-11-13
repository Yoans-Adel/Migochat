"""
Comprehensive Config Package Tests
Tests for config/ directory including database_config.py and logging_config.py
Testing all integration points across the project
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import TYPE_CHECKING
from datetime import datetime
import logging
import sys

if TYPE_CHECKING:
    from typing import Any, Dict, Generator
    from sqlalchemy.orm import Session


# ============================================================================
# DATABASE CONFIG TESTS
# ============================================================================

@pytest.mark.config
@pytest.mark.unit
class TestDatabaseConfig:
    """Test database_config module functionality"""

    def test_database_config_imports(self):
        """Test that database_config module can be imported"""
        from config import database_config
        assert database_config is not None

    def test_database_url_format(self):
        """Test DATABASE_URL is properly formatted for SQLite"""
        from config.database_config import DATABASE_URL
        assert DATABASE_URL.startswith("sqlite:///")
        assert "bww_ai_assistant.db" in DATABASE_URL
        assert DATABASE_URL.count("/") >= 3

    def test_database_dir_created(self):
        """Test database directory is created automatically"""
        from config.database_config import DATABASE_DIR
        assert DATABASE_DIR.exists()
        assert DATABASE_DIR.is_dir()
        assert DATABASE_DIR.name == "database"

    def test_engine_creation(self):
        """Test SQLAlchemy engine is created with correct settings"""
        from config.database_config import engine
        assert engine is not None
        assert hasattr(engine, 'connect')
        assert hasattr(engine, 'dispose')

    def test_engine_pool_configuration(self):
        """Test engine pool has correct configuration"""
        from config.database_config import engine
        # Check pool settings
        assert engine.pool._pre_ping is True
        assert engine.pool._recycle == 300

    def test_session_factory_creation(self):
        """Test SessionLocal factory is created and works"""
        from config.database_config import SessionLocal
        assert SessionLocal is not None
        session = SessionLocal()
        assert session is not None
        assert hasattr(session, 'query')
        assert hasattr(session, 'commit')
        session.close()

    def test_base_declarative_class(self):
        """Test Base declarative class exists and is usable"""
        from config.database_config import Base
        assert Base is not None
        assert hasattr(Base, 'metadata')
        assert hasattr(Base.metadata, 'create_all')
        assert hasattr(Base.metadata, 'tables')


@pytest.mark.config
@pytest.mark.unit
class TestDatabaseEnums:
    """Test all database enum types"""

    def test_message_direction_enum(self):
        """Test MessageDirection enum values"""
        from config.database_config import MessageDirection
        assert MessageDirection.INBOUND.value == "inbound"
        assert MessageDirection.OUTBOUND.value == "outbound"
        # Test enum has only 2 values
        assert len(list(MessageDirection)) == 2

    def test_message_status_enum(self):
        """Test MessageStatus enum values"""
        from config.database_config import MessageStatus
        assert MessageStatus.SENT.value == "sent"
        assert MessageStatus.DELIVERED.value == "delivered"
        assert MessageStatus.READ.value == "read"
        assert MessageStatus.FAILED.value == "failed"
        assert len(list(MessageStatus)) == 4

    def test_message_source_enum(self):
        """Test MessageSource enum values"""
        from config.database_config import MessageSource
        assert MessageSource.MESSENGER.value == "messenger"
        assert MessageSource.WHATSAPP.value == "whatsapp"
        assert MessageSource.LEAD_CENTER.value == "lead_center"
        assert MessageSource.MANUAL.value == "manual"
        assert len(list(MessageSource)) == 4

    def test_lead_stage_enum(self):
        """Test LeadStage enum values"""
        from config.database_config import LeadStage
        assert LeadStage.NEW.value == "new"
        assert LeadStage.CONTACTED.value == "contacted"
        assert LeadStage.QUALIFIED.value == "qualified"
        assert LeadStage.HOT.value == "hot"
        assert LeadStage.PROPOSAL.value == "proposal"
        assert LeadStage.NEGOTIATION.value == "negotiation"
        assert LeadStage.CLOSED_WON.value == "closed_won"
        assert LeadStage.CLOSED_LOST.value == "closed_lost"
        assert len(list(LeadStage)) == 8

    def test_customer_label_enum(self):
        """Test CustomerLabel enum values"""
        from config.database_config import CustomerLabel
        assert CustomerLabel.HOT.value == "hot"
        assert CustomerLabel.WARM.value == "warm"
        assert CustomerLabel.COLD.value == "cold"
        assert CustomerLabel.UNQUALIFIED.value == "unqualified"
        assert len(list(CustomerLabel)) == 4

    def test_customer_type_enum(self):
        """Test CustomerType enum values"""
        from config.database_config import CustomerType
        assert CustomerType.INDIVIDUAL.value == "individual"
        assert CustomerType.BUSINESS.value == "business"
        assert CustomerType.WHOLESALE.value == "wholesale"
        assert CustomerType.RETAIL.value == "retail"
        assert CustomerType.LEAD.value == "lead"
        assert len(list(CustomerType)) == 5

    def test_post_type_enum(self):
        """Test PostType enum values"""
        from config.database_config import PostType
        assert PostType.POST.value == "post"
        assert PostType.STORY.value == "story"
        assert PostType.REEL.value == "reel"
        assert PostType.AD.value == "ad"
        assert len(list(PostType)) == 4

    def test_governorate_enum(self):
        """Test Governorate enum has all Egyptian governorates"""
        from config.database_config import Governorate
        # Check some major governorates
        assert hasattr(Governorate, 'CAIRO')
        assert hasattr(Governorate, 'ALEXANDRIA')
        assert hasattr(Governorate, 'GIZA')
        # Should have 27 governorates
        assert len(list(Governorate)) == 27


@pytest.mark.config
@pytest.mark.unit
class TestDatabaseModels:
    """Test database model definitions"""

    def test_user_model_exists(self):
        """Test User model is defined"""
        from config.database_config import User
        assert User is not None
        assert User.__tablename__ == "users"

    def test_user_model_columns(self):
        """Test User model has all required columns"""
        from config.database_config import User
        columns = [col.name for col in User.__table__.columns]
        
        required_columns = [
            'id', 'psid', 'phone_number', 'first_name', 'last_name',
            'profile_pic', 'locale', 'timezone', 'gender', 'governorate',
            'lead_stage', 'customer_label', 'customer_type', 'lead_score',
            'created_at', 'updated_at', 'last_message_at', 'last_seen_at'
        ]
        
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"

    def test_message_model_exists(self):
        """Test Message model is defined"""
        from config.database_config import Message
        assert Message is not None
        assert Message.__tablename__ == "messages"

    def test_message_model_columns(self):
        """Test Message model has all required columns"""
        from config.database_config import Message
        columns = [col.name for col in Message.__table__.columns]
        
        required_columns = [
            'id', 'user_id', 'facebook_message_id', 'whatsapp_message_id',
            'text', 'message_type', 'direction', 'status', 'source',
            'post_id', 'ad_campaign_id', 'is_ai_response', 'ai_model_used',
            'response_time_ms', 'created_at', 'sent_at', 'delivered_at', 'read_at'
        ]
        
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"

    def test_conversation_model_exists(self):
        """Test Conversation model is defined"""
        from config.database_config import Conversation
        assert Conversation is not None
        assert Conversation.__tablename__ == "conversations"

    def test_lead_activity_model_exists(self):
        """Test LeadActivity model is defined"""
        from config.database_config import LeadActivity
        assert LeadActivity is not None
        assert LeadActivity.__tablename__ == "lead_activities"

    def test_post_model_exists(self):
        """Test Post model is defined"""
        from config.database_config import Post
        assert Post is not None
        assert Post.__tablename__ == "posts"

    def test_ad_campaign_model_exists(self):
        """Test AdCampaign model is defined"""
        from config.database_config import AdCampaign
        assert AdCampaign is not None
        assert AdCampaign.__tablename__ == "ad_campaigns"

    def test_user_relationships(self):
        """Test User model has correct relationships"""
        from config.database_config import User
        assert hasattr(User, 'messages')
        assert hasattr(User, 'conversations')
        assert hasattr(User, 'lead_activities')


@pytest.mark.config
@pytest.mark.unit
class TestDatabaseUtilityFunctions:
    """Test database utility functions"""

    def test_get_session_generator(self):
        """Test get_session generator function"""
        from config.database_config import get_session
        assert callable(get_session)
        # It's a generator function
        gen = get_session()
        assert hasattr(gen, '__next__')

    def test_create_database_function(self):
        """Test create_database function"""
        from config.database_config import create_database, Base
        try:
            create_database()
            # Verify tables are created
            assert len(Base.metadata.tables) > 0
        except Exception as e:
            pytest.fail(f"create_database failed: {e}")

    def test_backup_database_function(self):
        """Test backup_database creates backup file"""
        from config.database_config import backup_database, DATABASE_DIR
        try:
            backup_file = backup_database()
            assert backup_file is not None
            assert Path(backup_file).exists()
            assert "backup" in str(backup_file)
            # Cleanup
            Path(backup_file).unlink()
        except Exception as e:
            pytest.fail(f"backup_database failed: {e}")

    def test_restore_database_function_exists(self):
        """Test restore_database function exists"""
        from config.database_config import restore_database
        assert callable(restore_database)

    def test_drop_database_function_exists(self):
        """Test drop_database function exists"""
        from config.database_config import drop_database
        assert callable(drop_database)

    def test_check_database_health_function(self):
        """Test check_database_health returns health status"""
        from config.database_config import check_database_health
        result = check_database_health()
        assert isinstance(result, dict)
        assert 'status' in result
        assert result['status'] in ['healthy', 'unhealthy']


# ============================================================================
# LOGGING CONFIG TESTS
# ============================================================================

@pytest.mark.config
@pytest.mark.unit
class TestLoggingConfig:
    """Test logging_config module functionality"""

    def setup_method(self):
        """Setup test environment"""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

    def teardown_method(self):
        """Cleanup test environment"""
        # Clear handlers again
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

    def test_logging_config_imports(self):
        """Test that logging_config module can be imported"""
        from config import logging_config
        assert logging_config is not None

    def test_setup_logging_function(self):
        """Test setup_logging function returns handlers and paths"""
        from config.logging_config import setup_logging
        handlers, log_files = setup_logging()
        
        assert isinstance(handlers, dict)
        assert isinstance(log_files, dict)
        assert len(handlers) > 0
        assert len(log_files) > 0

    def test_setup_logging_creates_logs_dir(self):
        """Test setup_logging creates logs directory"""
        from config.logging_config import setup_logging
        
        # Remove logs dir if exists
        logs_dir = Path("logs")
        if logs_dir.exists():
            # Just verify it exists
            assert logs_dir.is_dir()
        
        setup_logging()
        assert logs_dir.exists()
        assert logs_dir.is_dir()

    def test_logging_handler_types(self):
        """Test all handlers are RotatingFileHandler"""
        from config.logging_config import setup_logging
        import logging.handlers
        
        handlers, _ = setup_logging()
        
        expected_handlers = [
            'app', 'error', 'debug', 'access', 'ai',
            'database', 'webhook', 'messenger', 'whatsapp'
        ]
        
        for handler_name in expected_handlers:
            assert handler_name in handlers
            assert isinstance(handlers[handler_name], logging.handlers.RotatingFileHandler)

    def test_log_file_paths_format(self):
        """Test log file paths have timestamp format"""
        from config.logging_config import setup_logging
        
        _, log_files = setup_logging()
        timestamp = datetime.now().strftime("%Y%m%d")
        
        for log_type, log_path in log_files.items():
            assert isinstance(log_path, Path)
            assert log_path.parent.name == "logs"
            assert timestamp in str(log_path)
            assert log_path.suffix == ".log"

    def test_get_logger_function(self):
        """Test get_logger function returns logger instance"""
        from config.logging_config import get_logger
        
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_log_handlers_have_formatters(self):
        """Test all handlers have formatters configured"""
        from config.logging_config import setup_logging
        
        handlers, _ = setup_logging()
        
        for handler in handlers.values():
            assert handler.formatter is not None

    def test_log_levels_configuration(self):
        """Test handlers have correct log levels"""
        from config.logging_config import setup_logging
        
        handlers, _ = setup_logging()
        
        assert handlers['app'].level == logging.INFO
        assert handlers['error'].level == logging.ERROR
        assert handlers['debug'].level == logging.DEBUG
        assert handlers['access'].level == logging.INFO
        assert handlers['ai'].level == logging.INFO

    def test_rotating_file_handler_settings(self):
        """Test rotating file handlers have correct settings"""
        from config.logging_config import setup_logging
        
        handlers, _ = setup_logging()
        
        # Check all handlers have rotation settings
        for handler in handlers.values():
            assert handler.maxBytes == 10 * 1024 * 1024  # 10MB
            assert handler.backupCount == 5

    def test_logger_specific_configuration(self):
        """Test specific loggers are configured correctly"""
        from config.logging_config import setup_logging
        
        setup_logging()
        
        # Test AI service logger
        ai_logger = logging.getLogger('app.services.ai_service')
        assert ai_logger is not None
        assert ai_logger.propagate is False

    def test_console_handler_added(self):
        """Test console handler is added to root logger"""
        from config.logging_config import setup_logging
        
        setup_logging()
        root_logger = logging.getLogger()
        
        # Should have console handler (StreamHandler)
        console_handlers = [h for h in root_logger.handlers 
                           if isinstance(h, logging.StreamHandler) 
                           and not isinstance(h, logging.handlers.RotatingFileHandler)]
        assert len(console_handlers) > 0


# ============================================================================
# CONFIG PACKAGE INTEGRATION TESTS
# ============================================================================

@pytest.mark.config
@pytest.mark.integration
class TestConfigPackageIntegration:
    """Test config package integration with the project"""

    def test_config_package_imports(self):
        """Test config package can be imported"""
        import config
        assert config is not None

    def test_config_exports_database_config(self):
        """Test config package exports database_config"""
        import config
        assert hasattr(config, 'database_config')

    def test_config_exports_logging_config(self):
        """Test config package exports logging_config"""
        import config
        assert hasattr(config, 'logging_config')

    def test_config_get_config_function(self):
        """Test config package has get_config function"""
        from config import get_config
        assert callable(get_config)

    def test_database_and_logging_work_together(self):
        """Test database and logging configs work together"""
        from config.database_config import SessionLocal
        from config.logging_config import setup_logging, get_logger
        
        # Setup logging first
        setup_logging()
        logger = get_logger("integration_test")
        
        # Create database session
        session = SessionLocal()
        assert session is not None
        
        # Log database operation
        logger.info("Database session created for integration test")
        
        # Cleanup
        session.close()

    def test_scripts_can_import_database_config(self):
        """Test scripts can import database_config functions"""
        from config.database_config import (
            create_database, backup_database, restore_database,
            drop_database, check_database_health, DATABASE_DIR, DATABASE_URL
        )
        
        assert callable(create_database)
        assert callable(backup_database)
        assert callable(restore_database)
        assert callable(drop_database)
        assert callable(check_database_health)
        assert DATABASE_DIR is not None
        assert DATABASE_URL is not None

    def test_server_can_import_logging_config(self):
        """Test Server can import logging_config functions"""
        from config.logging_config import setup_logging, get_logger
        
        assert callable(setup_logging)
        assert callable(get_logger)


# ============================================================================
# CRITICAL CONFIG TESTS
# ============================================================================

@pytest.mark.config
@pytest.mark.critical
class TestConfigCriticalFunctions:
    """Critical tests that must pass for config to work"""

    def test_database_connection_works(self):
        """CRITICAL: Test database connection is functional"""
        from config.database_config import engine
        from sqlalchemy import text
        
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                assert result is not None
        except Exception as e:
            pytest.fail(f"Database connection failed: {e}")

    def test_logging_system_functional(self):
        """CRITICAL: Test logging system works end-to-end"""
        from config.logging_config import setup_logging, get_logger
        
        try:
            setup_logging()
            logger = get_logger("critical_test")
            logger.info("Critical test message")
            # If we reach here, logging works
            assert True
        except Exception as e:
            pytest.fail(f"Logging system failed: {e}")

    def test_session_creation_and_cleanup(self):
        """CRITICAL: Test session lifecycle"""
        from config.database_config import SessionLocal
        from sqlalchemy import text
        
        session = None
        try:
            session = SessionLocal()
            assert session is not None
            # Test basic query
            result = session.execute(text("SELECT 1"))
            assert result is not None
        finally:
            if session:
                session.close()

    def test_all_database_tables_created(self):
        """CRITICAL: Test all expected tables are created"""
        from config.database_config import create_database, Base
        from sqlalchemy import inspect
        
        create_database()
        
        expected_tables = [
            "users", "messages", "conversations",
            "lead_activities", "posts", "ad_campaigns"
        ]
        
        actual_tables = list(Base.metadata.tables.keys())
        
        for table in expected_tables:
            assert table in actual_tables, f"Missing table: {table}"

    def test_config_directory_structure(self):
        """CRITICAL: Test config directory structure"""
        config_dir = Path("config")
        
        assert config_dir.exists(), "Config directory must exist"
        assert (config_dir / "__init__.py").exists(), "__init__.py missing"
        assert (config_dir / "database_config.py").exists(), "database_config.py missing"
        assert (config_dir / "logging_config.py").exists(), "logging_config.py missing"


# ============================================================================
# CONFIG SMOKE TESTS
# ============================================================================

@pytest.mark.config
@pytest.mark.smoke
class TestConfigSmoke:
    """Quick smoke tests for config package"""

    def test_import_all_config_modules(self):
        """Smoke: Import all config modules"""
        import config
        from config import database_config
        from config import logging_config
        
        assert all([config, database_config, logging_config])

    def test_basic_database_operations(self):
        """Smoke: Basic database operations"""
        from config.database_config import SessionLocal
        from sqlalchemy import text
        
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()

    def test_basic_logging_operations(self):
        """Smoke: Basic logging operations"""
        from config.logging_config import get_logger
        
        logger = get_logger("smoke_test")
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warning")


# ============================================================================
# CONFIG INTEGRATION WITH PROJECT COMPONENTS
# ============================================================================

@pytest.mark.config
@pytest.mark.integration
class TestConfigProjectIntegration:
    """Test config integration with specific project components"""

    def test_db_manager_integration(self):
        """Test config integration with scripts/db_manager.py"""
        # db_manager uses these functions from database_config
        from config.database_config import (
            create_database, backup_database, restore_database,
            drop_database, check_database_health, DATABASE_DIR, DATABASE_URL
        )
        
        # Verify all functions work
        assert callable(create_database)
        assert callable(backup_database)
        health = check_database_health()
        assert health['status'] in ['healthy', 'unhealthy']

    def test_main_app_logging_integration(self):
        """Test config integration with Server/main.py"""
        from config.logging_config import setup_logging, get_logger
        
        # Server/main.py uses setup_logging and get_logger
        setup_logging()
        logger = get_logger("main_app")
        
        assert logger is not None
        logger.info("Test from main app")

    def test_scripts_logging_integration(self):
        """Test config integration with scripts"""
        from config.logging_config import setup_logging, get_logger
        
        # All scripts use setup_logging and get_logger
        setup_logging()
        
        loggers = [
            get_logger("setup"),
            get_logger("log_manager"),
            get_logger("db_manager")
        ]
        
        for logger in loggers:
            assert logger is not None
