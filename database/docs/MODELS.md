# 📦 SQLAlchemy Models Documentation

**Project**: Migochat Database Models  
**ORM**: SQLAlchemy 2.0 (Modern Mapped Annotations)  
**Last Updated**: 2025-11-11

---

## 🎯 Overview

This document provides comprehensive documentation for all SQLAlchemy ORM models used in Migochat.

### Architecture:
- ✅ **SQLAlchemy 2.0** with `Mapped[]` annotations
- ✅ **Type-safe** with full mypy compatibility
- ✅ **Relationship management** with back_populates
- ✅ **Enum-based** field types for data integrity
- ✅ **Timezone-aware** datetime fields (UTC)

---

## 📚 Base Model

### `Base` - Declarative Base

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass
```

**Usage**: All models inherit from `Base`

**Features**:
- Provides `__tablename__` convention
- Enables SQLAlchemy query interface
- Metadata registry for migrations

---

## 👤 User Model

### `User` - Customer/Lead Entity

**Table**: `users`  
**Purpose**: Represents customers and leads from all platforms

```python
class User(Base):
    __tablename__ = "users"
    
    # Primary identification
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    psid: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    
    # Profile information
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    profile_pic: Mapped[Optional[str]] = mapped_column(String(500))
    governorate: Mapped[Optional[Governorate]] = mapped_column(SQLEnum(Governorate))
    
    # Platform details
    platform: Mapped[str] = mapped_column(String(50), default="facebook")
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Lead management
    lead_stage: Mapped[LeadStage] = mapped_column(SQLEnum(LeadStage), default=LeadStage.INTAKE)
    customer_label: Mapped[Optional[CustomerLabel]] = mapped_column(SQLEnum(CustomerLabel))
    customer_type: Mapped[Optional[CustomerType]] = mapped_column(SQLEnum(CustomerType))
    lead_score: Mapped[int] = mapped_column(default=0)
    last_stage_change: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    messages: Mapped[list["Message"]] = relationship(back_populates="user")
    lead_activities: Mapped[list["LeadActivity"]] = relationship(back_populates="user")
```

**Key Features**:
- **PSID-based**: Unique page-scoped ID for Facebook, phone for WhatsApp
- **Multi-platform**: Supports facebook, whatsapp, telegram
- **Lead tracking**: Full lead lifecycle management
- **Timezone-aware**: All timestamps in UTC

**Relationships**:
- ➡️ `messages` (1:N) - All messages from/to this user
- ➡️ `lead_activities` (1:N) - Lead management history

**Example Usage**:
```python
# Create new user
user = User(
    psid="1234567890",
    first_name="Ahmed",
    platform="facebook",
    lead_stage=LeadStage.INTAKE
)
session.add(user)
session.commit()

# Query with relationships
user = session.query(User).filter(User.psid == "1234567890").first()
print(f"Messages: {len(user.messages)}")
print(f"Lead Stage: {user.lead_stage.value}")
```

---

## 💬 Message Model

### `Message` - Message Storage

**Table**: `messages`  
**Purpose**: Store all messages with source attribution

```python
class Message(Base):
    __tablename__ = "messages"
    
    # Identification
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Message participants
    sender_id: Mapped[str] = mapped_column(String(50))
    recipient_id: Mapped[str] = mapped_column(String(50))
    
    # Content
    message_text: Mapped[Optional[str]] = mapped_column(Text)
    direction: Mapped[MessageDirection] = mapped_column(SQLEnum(MessageDirection))
    status: Mapped[MessageStatus] = mapped_column(SQLEnum(MessageStatus), default=MessageStatus.SENT)
    
    # Metadata
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    facebook_message_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    message_type: Mapped[str] = mapped_column(String(50), default="text")
    message_metadata: Mapped[Optional[str]] = mapped_column(Text)
    platform: Mapped[str] = mapped_column(String(50), default="facebook")
    
    # Source tracking
    message_source: Mapped[MessageSource] = mapped_column(SQLEnum(MessageSource), default=MessageSource.DIRECT_MESSAGE)
    post_id: Mapped[Optional[int]] = mapped_column(ForeignKey("posts.id"))
    post_type: Mapped[Optional[PostType]] = mapped_column(SQLEnum(PostType))
    ad_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ad_campaigns.id"))
    comment_id: Mapped[Optional[str]] = mapped_column(String(100))
    referral_source: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="messages")
    post: Mapped[Optional["Post"]] = relationship(foreign_keys=[post_id], back_populates="messages")
    ad_campaign: Mapped[Optional["AdCampaign"]] = relationship(foreign_keys=[ad_id], back_populates="messages")
```

**Key Features**:
- **Source attribution**: Track if message came from ad, post, or direct
- **Bi-directional**: INBOUND (customer → bot) or OUTBOUND (bot → customer)
- **Multi-type**: text, image, file, location, etc.
- **Status tracking**: sent, delivered, read, failed

**Example Usage**:
```python
# Incoming message
message = Message(
    user_id=user.id,
    sender_id=user.psid,
    recipient_id=PAGE_ID,
    message_text="مرحبا، أريد شراء المنتج",
    direction=MessageDirection.INBOUND,
    platform="facebook",
    message_source=MessageSource.DIRECT_MESSAGE
)

# Message from post comment
message = Message(
    user_id=user.id,
    message_source=MessageSource.POST_COMMENT,
    post_id=post.id,
    comment_id="comment_123",
    message_text="كم السعر؟"
)
```

---

## 🗨️ Conversation Model

### `Conversation` - Thread Tracking

**Table**: `conversations`  
**Purpose**: Track active conversation threads

```python
class Conversation(Base):
    __tablename__ = "conversations"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    last_activity: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    message_count: Mapped[int] = mapped_column(default=0)
    
    # Relationships
    user: Mapped["User"] = relationship()
```

**Usage**:
```python
# Create conversation
conv = Conversation(user_id=user.id)

# Update activity
conv.last_activity = datetime.now(timezone.utc)
conv.message_count += 1
```

---

## 📊 LeadActivity Model

### `LeadActivity` - Audit Trail

**Table**: `lead_activities`  
**Purpose**: Track all lead management changes

```python
class LeadActivity(Base):
    __tablename__ = "lead_activities"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    activity_type: Mapped[str] = mapped_column(String(50))
    old_value: Mapped[Optional[str]] = mapped_column(String(100))
    new_value: Mapped[Optional[str]] = mapped_column(String(100))
    reason: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    automated: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="lead_activities")
```

**Activity Types**:
- `stage_change` - Lead stage updated
- `label_change` - Customer label changed
- `score_update` - Lead score modified
- `type_change` - Customer type updated

**Example**:
```python
# Log stage change
activity = LeadActivity(
    user_id=user.id,
    activity_type="stage_change",
    old_value="INTAKE",
    new_value="NURTURE",
    reason="Customer showed interest in products",
    automated=True
)
```

---

## 📝 Post Model

### `Post` - Facebook Post Tracking

**Table**: `posts`  
**Purpose**: Track Facebook posts for attribution

```python
class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    facebook_post_id: Mapped[str] = mapped_column(String(100), unique=True)
    post_type: Mapped[PostType] = mapped_column(SQLEnum(PostType))
    post_content: Mapped[Optional[str]] = mapped_column(Text)
    post_price: Mapped[Optional[str]] = mapped_column(String(100))
    post_data: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    messages: Mapped[list["Message"]] = relationship(foreign_keys="Message.post_id", back_populates="post")
```

**Example**:
```python
# Product post
post = Post(
    facebook_post_id="post_123",
    post_type=PostType.PRODUCT,
    post_content="جاكيت شتوي للبيع - 500 جنيه",
    post_price="500 EGP",
    post_data='{"category": "winter", "size": "L"}'
)
```

---

## 📢 AdCampaign Model

### `AdCampaign` - Ad Campaign Tracking

**Table**: `ad_campaigns`  
**Purpose**: Track Facebook ad campaigns

```python
class AdCampaign(Base):
    __tablename__ = "ad_campaigns"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    facebook_ad_id: Mapped[str] = mapped_column(String(100), unique=True)
    campaign_name: Mapped[Optional[str]] = mapped_column(String(200))
    ad_content: Mapped[Optional[str]] = mapped_column(Text)
    target_audience: Mapped[Optional[str]] = mapped_column(Text)
    budget: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    messages: Mapped[list["Message"]] = relationship(foreign_keys="Message.ad_id", back_populates="ad_campaign")
```

---

## ⚙️ AppSettings Model

### `AppSettings` - Dynamic Configuration

**Table**: `app_settings`  
**Purpose**: Store editable app configuration

```python
class AppSettings(Base):
    __tablename__ = "app_settings"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    updated_by: Mapped[str] = mapped_column(String(100), default="admin")
```

**Example**:
```python
# Store API key (sensitive)
setting = AppSettings(
    key="gemini_api_key",
    value="AIzaSy...",
    category="ai",
    is_sensitive=True,
    description="Google Gemini API Key"
)

# Store threshold (not sensitive)
setting = AppSettings(
    key="lead_score_threshold",
    value="75",
    category="system",
    is_sensitive=False
)
```

---

## 🔗 Relationship Patterns

### One-to-Many (1:N)
```python
# User → Messages
user.messages  # List[Message]
message.user   # User

# Usage
user = session.query(User).first()
for message in user.messages:
    print(message.message_text)
```

### Optional Relationships (N:1)
```python
# Message → Post (optional)
message.post  # Optional[Post]

# Check if exists
if message.post:
    print(f"From post: {message.post.post_content}")
```

---

## 📝 Best Practices

### Creating Records
```python
# Use context manager
from database.context import get_db_context

with get_db_context() as session:
    user = User(psid="123", first_name="Ahmed")
    session.add(user)
    session.commit()
    # Auto-rollback on exception
```

### Querying with Relationships
```python
# Eager loading (prevent N+1)
from sqlalchemy.orm import joinedload

users = session.query(User).options(
    joinedload(User.messages)
).all()

# All messages loaded in single query!
for user in users:
    print(f"{user.first_name}: {len(user.messages)} messages")
```

### Updating Records
```python
user = session.query(User).filter(User.psid == "123").first()
user.lead_stage = LeadStage.NURTURE
session.commit()
```

---

## 🎯 Type Safety

All models use **SQLAlchemy 2.0 Mapped annotations**:

```python
# Type-safe column definitions
id: Mapped[int]                    # Required int
name: Mapped[Optional[str]]         # Optional string
created_at: Mapped[datetime]        # Required datetime
messages: Mapped[list["Message"]]   # Relationship list
```

**Benefits**:
- ✅ mypy/pyright type checking
- ✅ IDE autocomplete
- ✅ Runtime type validation
- ✅ Better code maintainability

---

**Documentation Version**: 1.0  
**Last Updated**: 2025-11-11  
**ORM Version**: SQLAlchemy 2.0+
