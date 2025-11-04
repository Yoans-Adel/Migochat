"""
Database Models Module
SQLAlchemy ORM models for the application
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

from database.enums import (
    MessageSource,
    PostType,
    LeadStage,
    CustomerLabel,
    CustomerType,
    Governorate,
    MessageDirection,
    MessageStatus
)

Base = declarative_base()

class User(Base):
    """User model - represents customers/leads"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    psid = Column(String(50), unique=True, index=True, nullable=False)  # Page-Scoped ID
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_pic = Column(String(500))
    governorate = Column(Enum(Governorate))
    platform = Column(String(50), default="facebook")  # facebook, whatsapp, telegram
    phone_number = Column(String(20))  # For WhatsApp users
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_message_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Lead Management Fields
    lead_stage = Column(Enum(LeadStage), default=LeadStage.INTAKE)
    customer_label = Column(Enum(CustomerLabel))
    customer_type = Column(Enum(CustomerType))
    lead_score = Column(Integer, default=0)
    last_stage_change = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    messages = relationship("Message", back_populates="user")
    lead_activities = relationship("LeadActivity", back_populates="user")

class Message(Base):
    """Message model - stores all messages"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_id = Column(String(50), nullable=False)  # PSID
    recipient_id = Column(String(50), nullable=False)  # Page ID
    message_text = Column(Text)
    direction = Column(Enum(MessageDirection), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    facebook_message_id = Column(String(100), unique=True)
    message_type = Column(String(50), default="text")  # text, image, file, etc.
    message_metadata = Column(Text)  # JSON string for additional data
    platform = Column(String(50), default="facebook")

    # Message Source Tracking
    message_source = Column(Enum(MessageSource), default=MessageSource.DIRECT_MESSAGE)
    post_id = Column(Integer, ForeignKey("posts.id"))
    post_type = Column(Enum(PostType))
    ad_id = Column(Integer, ForeignKey("ad_campaigns.id"))
    comment_id = Column(String(100))  # Facebook Comment ID if converted from comment
    referral_source = Column(String(200))

    # Relationships
    user = relationship("User", back_populates="messages")
    post = relationship("Post", foreign_keys=[post_id], back_populates="messages")
    ad_campaign = relationship("AdCampaign", foreign_keys=[ad_id], back_populates="messages")

class Conversation(Base):
    """Conversation model - tracks active conversations"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)

    # Relationships
    user = relationship("User")

class LeadActivity(Base):
    """Lead activity model - tracks lead management changes"""
    __tablename__ = "lead_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # stage_change, label_change, etc.
    old_value = Column(String(100))
    new_value = Column(String(100))
    reason = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    automated = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="lead_activities")

class Post(Base):
    """Post model - tracks Facebook posts"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    facebook_post_id = Column(String(100), unique=True, nullable=False)
    post_type = Column(Enum(PostType), nullable=False)
    post_content = Column(Text)
    post_price = Column(String(100))
    post_data = Column(Text)  # JSON string for product data
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    # Relationships
    messages = relationship("Message", foreign_keys="Message.post_id", back_populates="post")

class AdCampaign(Base):
    """Ad campaign model - tracks Facebook ads"""
    __tablename__ = "ad_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    facebook_ad_id = Column(String(100), unique=True, nullable=False)
    campaign_name = Column(String(200))
    ad_content = Column(Text)
    target_audience = Column(Text)  # JSON string for targeting data
    budget = Column(String(100))
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    messages = relationship("Message", foreign_keys="Message.ad_id", back_populates="ad_campaign")

class AppSettings(Base):
    """Application settings model - stores editable configuration (Admin only)"""
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    category = Column(String(50))  # facebook, whatsapp, ai, system
    is_sensitive = Column(Boolean, default=False)  # For API keys, tokens
    description = Column(Text)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by = Column(String(100), default="admin")

