# Config Package Usage Examples

## 📚 Practical Examples for Using Config Package

This document provides real-world examples of using the config package in the Migochat project.

---

## 🗄️ Database Config Examples

### Example 1: Basic Database Session Usage

```python
from config.database_config import SessionLocal, User

def get_user_by_psid(psid: str):
    """Get user from database by PSID"""
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(psid=psid).first()
        return user
    finally:
        session.close()

# Usage
user = get_user_by_psid("1234567890")
print(f"User: {user.first_name} {user.last_name}")
```

### Example 2: Using Context Manager with get_session()

```python
from config.database_config import get_session, User, Message

def create_user_with_message(psid: str, first_name: str, message_text: str):
    """Create user and initial message"""
    for session in get_session():
        # Create user
        user = User(
            psid=psid,
            first_name=first_name,
            locale="ar_AR",
            timezone=2
        )
        session.add(user)
        session.commit()
        
        # Create message
        message = Message(
            user_id=user.id,
            text=message_text,
            direction=MessageDirection.INBOUND,
            source=MessageSource.MESSENGER
        )
        session.add(message)
        session.commit()
        
        return user.id

# Usage
from config.database_config import MessageDirection, MessageSource
user_id = create_user_with_message("9876543210", "Ahmed", "مرحبا")
```

### Example 3: Lead Management with Enums

```python
from config.database_config import (
    SessionLocal, User, LeadActivity,
    LeadStage, CustomerLabel
)

def update_lead_stage(user_id: int, new_stage: LeadStage, new_label: CustomerLabel):
    """Update lead stage and track activity"""
    session = SessionLocal()
    try:
        # Get user
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return None
        
        # Track activity
        activity = LeadActivity(
            user_id=user_id,
            activity_type="stage_change",
            description=f"Stage changed from {user.lead_stage.value} to {new_stage.value}",
            stage_before=user.lead_stage,
            stage_after=new_stage,
            label_before=user.customer_label,
            label_after=new_label,
            score_change=10
        )
        
        # Update user
        user.lead_stage = new_stage
        user.customer_label = new_label
        user.lead_score += 10
        
        session.add(activity)
        session.commit()
        
        return user
    finally:
        session.close()

# Usage
updated_user = update_lead_stage(
    user_id=1,
    new_stage=LeadStage.QUALIFIED,
    new_label=CustomerLabel.HOT
)
```

### Example 4: Message Tracking with AI Response

```python
from config.database_config import (
    SessionLocal, Message, MessageDirection,
    MessageStatus, MessageSource
)
from datetime import datetime, timezone

def save_ai_response(user_id: int, prompt: str, response: str, response_time_ms: int):
    """Save user message and AI response"""
    session = SessionLocal()
    try:
        # Save user message
        user_message = Message(
            user_id=user_id,
            text=prompt,
            direction=MessageDirection.INBOUND,
            source=MessageSource.MESSENGER,
            status=MessageStatus.READ,
            created_at=datetime.now(timezone.utc)
        )
        session.add(user_message)
        
        # Save AI response
        ai_message = Message(
            user_id=user_id,
            text=response,
            direction=MessageDirection.OUTBOUND,
            source=MessageSource.MANUAL,
            status=MessageStatus.SENT,
            is_ai_response=True,
            ai_model_used="gemini-1.5-pro",
            response_time_ms=response_time_ms,
            created_at=datetime.now(timezone.utc)
        )
        session.add(ai_message)
        
        session.commit()
        return ai_message.id
    finally:
        session.close()

# Usage
message_id = save_ai_response(
    user_id=1,
    prompt="ما هي أسعار منتجاتكم؟",
    response="أسعارنا تبدأ من 100 جنيه...",
    response_time_ms=1250
)
```

### Example 5: Database Health Monitoring

```python
from config.database_config import check_database_health
import time

def monitor_database_health(interval_seconds: int = 60):
    """Monitor database health periodically"""
    while True:
        health = check_database_health()
        
        if health['status'] == 'healthy':
            print(f"✅ Database healthy - Tables: {health.get('tables', 'N/A')}")
        else:
            print(f"❌ Database unhealthy - Error: {health['error']}")
            # Send alert
            send_alert(f"Database health check failed: {health['error']}")
        
        time.sleep(interval_seconds)

# Usage (in background task)
# monitor_database_health(300)  # Check every 5 minutes
```

### Example 6: Database Backup & Restore

```python
from config.database_config import backup_database, restore_database, DATABASE_DIR
from pathlib import Path
from datetime import datetime

def scheduled_backup():
    """Create scheduled database backup"""
    try:
        backup_file = backup_database()
        print(f"✅ Backup created: {backup_file}")
        
        # Keep only last 7 backups
        cleanup_old_backups(days=7)
        
        return backup_file
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def cleanup_old_backups(days: int = 7):
    """Delete backups older than specified days"""
    backup_dir = DATABASE_DIR / "backups"
    cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
    
    for backup_file in backup_dir.glob("*.db"):
        if backup_file.stat().st_mtime < cutoff_time:
            backup_file.unlink()
            print(f"🗑️ Deleted old backup: {backup_file.name}")

def restore_from_backup(backup_filename: str):
    """Restore database from specific backup"""
    backup_file = DATABASE_DIR / "backups" / backup_filename
    
    if not backup_file.exists():
        print(f"❌ Backup file not found: {backup_filename}")
        return False
    
    try:
        restore_database(str(backup_file))
        print(f"✅ Database restored from: {backup_filename}")
        return True
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        return False

# Usage
backup_file = scheduled_backup()
# restore_from_backup("bww_ai_assistant_backup_20241231_120000.db")
```

---

## 📝 Logging Config Examples

### Example 7: Service-Specific Logging

```python
from config.logging_config import get_logger

class MessengerService:
    def __init__(self):
        self.logger = get_logger('app.services.messenger_service', 'messenger')
    
    def send_message(self, recipient_id: str, message: str):
        """Send message via Messenger"""
        self.logger.info(f"Sending message to {recipient_id}")
        
        try:
            # Send message logic
            response = self._send_via_api(recipient_id, message)
            self.logger.info(f"Message sent successfully - ID: {response['message_id']}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            raise

# Usage
messenger = MessengerService()
messenger.send_message("1234567890", "Hello!")
```

### Example 8: AI Service Logging with Timing

```python
from config.logging_config import get_logger
import time

class GeminiService:
    def __init__(self):
        self.logger = get_logger('app.services.ai_service', 'ai')
    
    def generate_response(self, prompt: str):
        """Generate AI response with timing"""
        start_time = time.time()
        self.logger.info(f"Generating response for prompt: {prompt[:50]}...")
        
        try:
            # AI generation logic
            response = self._call_gemini_api(prompt)
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            self.logger.info(
                f"Response generated successfully - "
                f"Time: {elapsed_ms}ms, "
                f"Length: {len(response)} chars"
            )
            
            return response, elapsed_ms
        except Exception as e:
            self.logger.error(f"AI generation failed: {e}")
            raise

# Usage
ai_service = GeminiService()
response, time_ms = ai_service.generate_response("ما هي أسعار المنتجات؟")
```

### Example 9: Webhook Event Logging

```python
from config.logging_config import get_logger
from typing import Dict, Any
import json

class WebhookHandler:
    def __init__(self):
        self.logger = get_logger('app.routes.webhook', 'webhook')
    
    def handle_webhook(self, event_type: str, payload: Dict[str, Any]):
        """Handle webhook with detailed logging"""
        self.logger.info(f"Received webhook - Type: {event_type}")
        self.logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            # Process webhook
            result = self._process_event(event_type, payload)
            
            self.logger.info(
                f"Webhook processed successfully - "
                f"Type: {event_type}, "
                f"Result: {result['status']}"
            )
            
            return result
        except Exception as e:
            self.logger.error(
                f"Webhook processing failed - "
                f"Type: {event_type}, "
                f"Error: {e}"
            )
            raise

# Usage
webhook = WebhookHandler()
result = webhook.handle_webhook('message', {'sender': '123', 'text': 'Hi'})
```

### Example 10: Database Operation Logging

```python
from config.logging_config import get_logger
from config.database_config import SessionLocal, User

class DatabaseService:
    def __init__(self):
        self.logger = get_logger('app.services.database_service', 'database')
    
    def create_user(self, psid: str, first_name: str):
        """Create user with logging"""
        self.logger.info(f"Creating user - PSID: {psid}, Name: {first_name}")
        
        session = SessionLocal()
        try:
            user = User(psid=psid, first_name=first_name)
            session.add(user)
            session.commit()
            
            self.logger.info(f"User created successfully - ID: {user.id}")
            return user
        except Exception as e:
            self.logger.error(f"User creation failed: {e}")
            session.rollback()
            raise
        finally:
            session.close()

# Usage
db_service = DatabaseService()
user = db_service.create_user("1234567890", "Ahmed")
```

### Example 11: Error Tracking with Context

```python
from config.logging_config import get_logger
import traceback

class ErrorHandler:
    def __init__(self):
        self.logger = get_logger('app.error_handler', 'error')
    
    def handle_error(self, error: Exception, context: dict):
        """Handle error with full context"""
        self.logger.error(
            f"Error occurred: {str(error)}\n"
            f"Context: {context}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        
        # Store in database for analytics
        self._store_error_analytics(error, context)

# Usage
try:
    # Some operation
    risky_operation()
except Exception as e:
    error_handler = ErrorHandler()
    error_handler.handle_error(e, {
        'user_id': 123,
        'operation': 'send_message',
        'timestamp': datetime.now()
    })
```

---

## 🔗 Combined Database + Logging Examples

### Example 12: Complete Message Flow

```python
from config.database_config import (
    SessionLocal, User, Message, Conversation,
    MessageDirection, MessageStatus, MessageSource
)
from config.logging_config import get_logger
from datetime import datetime, timezone

class MessageHandler:
    def __init__(self):
        self.logger = get_logger('app.services.message_handler', 'messenger')
    
    def process_incoming_message(self, psid: str, text: str, source: str = "messenger"):
        """Process incoming message with full tracking"""
        self.logger.info(f"Processing message from {psid}")
        
        session = SessionLocal()
        try:
            # Get or create user
            user = session.query(User).filter_by(psid=psid).first()
            if not user:
                self.logger.info(f"Creating new user - PSID: {psid}")
                user = User(psid=psid, locale="ar_AR")
                session.add(user)
                session.commit()
            
            # Save message
            message = Message(
                user_id=user.id,
                text=text,
                direction=MessageDirection.INBOUND,
                source=MessageSource[source.upper()],
                status=MessageStatus.READ,
                created_at=datetime.now(timezone.utc)
            )
            session.add(message)
            
            # Update conversation
            conversation = session.query(Conversation).filter_by(
                user_id=user.id,
                is_active=True
            ).first()
            
            if not conversation:
                self.logger.info(f"Creating new conversation for user {user.id}")
                conversation = Conversation(user_id=user.id)
                session.add(conversation)
            
            conversation.message_count += 1
            conversation.last_message_text = text
            conversation.last_message_at = datetime.now(timezone.utc)
            
            # Update user
            user.last_message_at = datetime.now(timezone.utc)
            
            session.commit()
            
            self.logger.info(
                f"Message processed - "
                f"User: {user.id}, "
                f"Message: {message.id}, "
                f"Conversation: {conversation.id}"
            )
            
            return message.id
        except Exception as e:
            self.logger.error(f"Message processing failed: {e}")
            session.rollback()
            raise
        finally:
            session.close()

# Usage
handler = MessageHandler()
message_id = handler.process_incoming_message("1234567890", "مرحبا", "messenger")
```

### Example 13: Analytics and Reporting

```python
from config.database_config import SessionLocal, Message, User
from config.logging_config import get_logger
from sqlalchemy import func
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self):
        self.logger = get_logger('app.services.analytics', 'app')
    
    def get_daily_stats(self, date: datetime = None):
        """Get daily statistics"""
        if date is None:
            date = datetime.now()
        
        self.logger.info(f"Generating stats for {date.strftime('%Y-%m-%d')}")
        
        session = SessionLocal()
        try:
            start_of_day = date.replace(hour=0, minute=0, second=0)
            end_of_day = date.replace(hour=23, minute=59, second=59)
            
            # Total messages
            total_messages = session.query(Message).filter(
                Message.created_at >= start_of_day,
                Message.created_at <= end_of_day
            ).count()
            
            # AI responses
            ai_responses = session.query(Message).filter(
                Message.created_at >= start_of_day,
                Message.created_at <= end_of_day,
                Message.is_ai_response == True
            ).count()
            
            # Average response time
            avg_response_time = session.query(
                func.avg(Message.response_time_ms)
            ).filter(
                Message.created_at >= start_of_day,
                Message.created_at <= end_of_day,
                Message.is_ai_response == True
            ).scalar()
            
            # New users
            new_users = session.query(User).filter(
                User.created_at >= start_of_day,
                User.created_at <= end_of_day
            ).count()
            
            stats = {
                'date': date.strftime('%Y-%m-%d'),
                'total_messages': total_messages,
                'ai_responses': ai_responses,
                'avg_response_time_ms': int(avg_response_time or 0),
                'new_users': new_users
            }
            
            self.logger.info(f"Stats generated: {stats}")
            return stats
        finally:
            session.close()

# Usage
analytics = AnalyticsService()
today_stats = analytics.get_daily_stats()
print(f"Messages today: {today_stats['total_messages']}")
```

---

## 🚀 Best Practices

### 1. Always Close Sessions
```python
# ❌ Bad
session = SessionLocal()
user = session.query(User).first()
# Session never closed!

# ✅ Good
session = SessionLocal()
try:
    user = session.query(User).first()
finally:
    session.close()

# ✅ Better
for session in get_session():
    user = session.query(User).first()
```

### 2. Use Specific Loggers
```python
# ❌ Bad
logger = logging.getLogger(__name__)

# ✅ Good
from config.logging_config import get_logger
logger = get_logger('app.services.my_service', 'app')
```

### 3. Handle Exceptions Properly
```python
# ✅ Best Practice
from config.logging_config import get_logger
from config.database_config import SessionLocal

logger = get_logger('app.service', 'app')
session = SessionLocal()

try:
    # Database operations
    session.add(object)
    session.commit()
    logger.info("Operation successful")
except Exception as e:
    logger.error(f"Operation failed: {e}")
    session.rollback()
    raise
finally:
    session.close()
```

### 4. Use Enums for Type Safety
```python
# ❌ Bad
message.source = "messenger"  # String, prone to typos

# ✅ Good
from config.database_config import MessageSource
message.source = MessageSource.MESSENGER  # Type-safe enum
```

---

## 📚 Additional Resources

- See `docs/CONFIG_INTEGRATION_ANALYSIS.md` for full integration details
- See `tests/test_config_package.py` for testing examples
- See `config/database_config.py` for all available models and enums
- See `config/logging_config.py` for logging configuration details
