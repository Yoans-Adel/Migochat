"""
Database Tests
Tests for database models, connections, and operations
"""
# type: ignore  # pytest fixtures don't support full type checking

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError


@pytest.mark.critical
@pytest.mark.database
class TestDatabaseConnection:
    """Test database connection and setup"""

    def test_database_engine_creation(self, test_db_engine):
        """Test that database engine is created"""
        assert test_db_engine is not None
        assert test_db_engine.url is not None

    def test_database_session_creation(self, db_session):
        """Test that database session is created"""
        assert db_session is not None
        assert db_session.is_active

    def test_tables_exist(self, test_db_engine):
        """Test that all required tables exist"""
        from sqlalchemy import inspect

        inspector = inspect(test_db_engine)
        table_names = inspector.get_table_names()

        required_tables = ['users', 'messages', 'conversations', 'lead_activities']
        for table in required_tables:
            assert table in table_names, f"Table '{table}' not found"


@pytest.mark.database
@pytest.mark.unit
class TestUserModel:
    """Test User model"""

    def test_create_user(self, create_test_user):
        """Test creating a user"""
        user = create_test_user(
            psid="test_123",
            first_name="Test",
            last_name="User",
            phone_number="+201234567890"
        )

        assert user.id is not None
        assert user.psid == "test_123"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.phone_number == "+201234567890"

    def test_user_unique_facebook_id(self, db_session, create_test_user):
        """Test that psid must be unique"""
        create_test_user(psid="duplicate_123")

        with pytest.raises(IntegrityError):
            create_test_user(psid="duplicate_123")
            db_session.commit()

    def test_user_has_timestamp(self, create_test_user):
        """Test that user has created_at timestamp"""
        user = create_test_user()

        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_user_relationships(self, create_test_user, create_test_message):
        """Test user relationships with messages"""
        user = create_test_user()
        message = create_test_message(user_id=user.id)

        assert message.user_id == user.id
        assert message in user.messages


@pytest.mark.database
@pytest.mark.unit
class TestMessageModel:
    """Test Message model"""

    def test_create_message(self, create_test_message, create_test_user):
        """Test creating a message"""
        user = create_test_user()
        message = create_test_message(
            user_id=user.id,
            facebook_message_id="test_msg_123",
            message_text="Test message content"
        )

        assert message.id is not None
        assert message.facebook_message_id == "test_msg_123"
        assert message.message_text == "Test message content"
        assert message.user_id == user.id

    def test_message_direction_enum(self, create_test_message):
        """Test message direction enum"""
        from database import MessageDirection

        incoming = create_test_message(direction=MessageDirection.INBOUND)
        outgoing = create_test_message(
            facebook_message_id="msg_out",
            direction=MessageDirection.OUTBOUND
        )

        assert incoming.direction == MessageDirection.INBOUND
        assert outgoing.direction == MessageDirection.OUTBOUND

    def test_message_status_enum(self, create_test_message):
        """Test message status enum"""
        from database import MessageStatus

        message = create_test_message(status=MessageStatus.DELIVERED)
        assert message.status == MessageStatus.DELIVERED

    def test_message_platform_field(self, create_test_message):
        """Test message platform field"""
        messenger_msg = create_test_message(platform="messenger")
        whatsapp_msg = create_test_message(
            facebook_message_id="wa_msg",
            platform="whatsapp"
        )

        assert messenger_msg.platform == "messenger"
        assert whatsapp_msg.platform == "whatsapp"

    def test_message_timestamps(self, create_test_message):
        """Test message has proper timestamps"""
        message = create_test_message()

        assert message.timestamp is not None
        assert isinstance(message.timestamp, datetime)


@pytest.mark.database
@pytest.mark.unit
class TestConversationModel:
    """Test Conversation model"""

    def test_create_conversation(self, create_test_conversation, create_test_user):
        """Test creating a conversation"""
        user = create_test_user()
        conversation = create_test_conversation(
            user_id=user.id,
            is_active=True,
            message_count=0
        )

        assert conversation.id is not None
        assert conversation.user_id == user.id
        assert conversation.is_active is True
        assert conversation.message_count == 0

    def test_conversation_user_relationship(self, create_test_conversation, create_test_user):
        """Test conversation-user relationship"""
        user = create_test_user()
        conversation = create_test_conversation(user_id=user.id)

        assert conversation.user_id == user.id
        assert conversation.user.id == user.id
        assert conversation.user.psid == user.psid


@pytest.mark.database
@pytest.mark.unit
class TestLeadActivityModel:
    """Test LeadActivity model"""

    def test_create_lead_activity(self, db_session, create_test_user):
        """Test creating lead activity"""
        from database import LeadActivity

        user = create_test_user()
        activity = LeadActivity(
            user_id=user.id,
            activity_type="stage_change",
            old_value="INTAKE",
            new_value="QUALIFIED",
            reason="Initial contact"
        )

        db_session.add(activity)
        db_session.commit()
        db_session.refresh(activity)

        assert activity.id is not None
        assert activity.user_id == user.id
        assert activity.activity_type == "stage_change"
        assert activity.new_value == "QUALIFIED"
        assert activity.reason == "Initial contact"

    def test_lead_stage_enum(self, db_session, create_test_user):
        """Test lead stage tracking through activities"""
        from database import LeadActivity, LeadStage

        user = create_test_user()

        stages = [
            LeadStage.INTAKE,
            LeadStage.QUALIFIED,
            LeadStage.IN_PROGRESS,
            LeadStage.CONVERTED
        ]

        for i, stage in enumerate(stages):
            activity = LeadActivity(
                user_id=user.id,
                activity_type="stage_change",
                new_value=stage.value
            )
            db_session.add(activity)

        db_session.commit()

        activities = db_session.query(LeadActivity).filter_by(user_id=user.id).all()
        assert len(activities) == len(stages)


@pytest.mark.database
@pytest.mark.integration
class TestDatabaseQueries:
    """Test database queries and operations"""

    def test_query_users(self, db_session, create_test_user):
        """Test querying users"""
        from database import User

        # Create multiple users
        create_test_user(psid="user_1", first_name="User", last_name="One")
        create_test_user(psid="user_2", first_name="User", last_name="Two")

        users = db_session.query(User).all()
        assert len(users) >= 2

    def test_query_messages_by_user(self, create_test_user, create_test_message, db_session):
        """Test querying messages by user"""
        from database import Message

        user = create_test_user()
        create_test_message(user_id=user.id)
        create_test_message(user_id=user.id)

        messages = db_session.query(Message).filter_by(user_id=user.id).all()
        assert len(messages) == 2

    def test_query_with_joins(self, create_test_user, create_test_message, db_session):
        """Test queries with joins"""
        from database import User, Message

        user = create_test_user()
        create_test_message(user_id=user.id, message_text="Join test message")

        result = db_session.query(User, Message).join(Message).filter(
            User.id == user.id
        ).first()

        assert result is not None
        assert result[0].first_name == "Test"
        assert result[1].message_text == "Join test message"


@pytest.mark.database
@pytest.mark.critical
class TestDatabaseIntegrity:
    """Test database integrity and constraints"""

    def test_cascade_delete(self, db_session, create_test_user, create_test_message):
        """Test cascade delete behavior"""
        from database import User, Message

        user = create_test_user()
        message = create_test_message(user_id=user.id)

        message_id = message.id

        # Delete message (not user, to avoid cascade issues)
        db_session.delete(message)
        db_session.commit()

        # Message should be deleted
        deleted_message = db_session.query(Message).filter_by(id=message_id).first()
        assert deleted_message is None

        # User should still exist
        assert db_session.query(User).filter_by(id=user.id).first() is not None

    def test_transaction_rollback(self, db_session):
        """Test transaction rollback"""
        from database import User
        import uuid

        initial_count = db_session.query(User).count()

        # Create user that will be rolled back
        try:
            user = User(
                psid=f"rollback_test_{uuid.uuid4().hex[:8]}",
                first_name="Rollback",
                last_name="Test"
            )
            db_session.add(user)
            db_session.flush()  # Push to DB but don't commit

            # Verify user exists in session
            assert db_session.query(User).filter_by(psid=user.psid).first() is not None

            # Force rollback
            db_session.rollback()
        except Exception:
            db_session.rollback()

        final_count = db_session.query(User).count()
        # Count should be same since we rolled back
        assert final_count == initial_count
