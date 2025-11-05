"""
Database Models Module
SQLAlchemy ORM models for the application
"""
from typing import Optional
from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
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

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class User(Base):
    """User model - represents customers/leads"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    psid: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # Page-Scoped ID
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    profile_pic: Mapped[Optional[str]] = mapped_column(String(500))
    governorate: Mapped[Optional[Governorate]] = mapped_column(SQLEnum(Governorate))
    platform: Mapped[str] = mapped_column(String(50), default="facebook")  # facebook, whatsapp, telegram
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))  # For WhatsApp users
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Lead Management Fields
    lead_stage: Mapped[LeadStage] = mapped_column(SQLEnum(LeadStage), default=LeadStage.INTAKE)
    customer_label: Mapped[Optional[CustomerLabel]] = mapped_column(SQLEnum(CustomerLabel))
    customer_type: Mapped[Optional[CustomerType]] = mapped_column(SQLEnum(CustomerType))
    lead_score: Mapped[int] = mapped_column(default=0)
    last_stage_change: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    messages: Mapped[list["Message"]] = relationship(back_populates="user")
    lead_activities: Mapped[list["LeadActivity"]] = relationship(back_populates="user")


class Message(Base):
    """Message model - stores all messages"""
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    sender_id: Mapped[str] = mapped_column(String(50))  # PSID
    recipient_id: Mapped[str] = mapped_column(String(50))  # Page ID
    message_text: Mapped[Optional[str]] = mapped_column(Text)
    direction: Mapped[MessageDirection] = mapped_column(SQLEnum(MessageDirection))
    status: Mapped[MessageStatus] = mapped_column(SQLEnum(MessageStatus), default=MessageStatus.SENT)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    facebook_message_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    message_type: Mapped[str] = mapped_column(String(50), default="text")  # text, image, file, etc.
    message_metadata: Mapped[Optional[str]] = mapped_column(Text)  # JSON string for additional data
    platform: Mapped[str] = mapped_column(String(50), default="facebook")

    # Message Source Tracking
    message_source: Mapped[MessageSource] = mapped_column(SQLEnum(MessageSource), default=MessageSource.DIRECT_MESSAGE)
    post_id: Mapped[Optional[int]] = mapped_column(ForeignKey("posts.id"))
    post_type: Mapped[Optional[PostType]] = mapped_column(SQLEnum(PostType))
    ad_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ad_campaigns.id"))
    comment_id: Mapped[Optional[str]] = mapped_column(String(100))  # Facebook Comment ID if converted from comment
    referral_source: Mapped[Optional[str]] = mapped_column(String(200))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="messages")
    post: Mapped[Optional["Post"]] = relationship(foreign_keys=[post_id], back_populates="messages")
    ad_campaign: Mapped[Optional["AdCampaign"]] = relationship(foreign_keys=[ad_id], back_populates="messages")


class Conversation(Base):
    """Conversation model - tracks active conversations"""
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_activity: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    message_count: Mapped[int] = mapped_column(default=0)

    # Relationships
    user: Mapped["User"] = relationship()


class LeadActivity(Base):
    """Lead activity model - tracks lead management changes"""
    __tablename__ = "lead_activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    activity_type: Mapped[str] = mapped_column(String(50))  # stage_change, label_change, etc.
    old_value: Mapped[Optional[str]] = mapped_column(String(100))
    new_value: Mapped[Optional[str]] = mapped_column(String(100))
    reason: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    automated: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="lead_activities")


class Post(Base):
    """Post model - tracks Facebook posts"""
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    facebook_post_id: Mapped[str] = mapped_column(String(100), unique=True)
    post_type: Mapped[PostType] = mapped_column(SQLEnum(PostType))
    post_content: Mapped[Optional[str]] = mapped_column(Text)
    post_price: Mapped[Optional[str]] = mapped_column(String(100))
    post_data: Mapped[Optional[str]] = mapped_column(Text)  # JSON string for product data
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    messages: Mapped[list["Message"]] = relationship(foreign_keys="Message.post_id", back_populates="post")


class AdCampaign(Base):
    """Ad campaign model - tracks Facebook ads"""
    __tablename__ = "ad_campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    facebook_ad_id: Mapped[str] = mapped_column(String(100), unique=True)
    campaign_name: Mapped[Optional[str]] = mapped_column(String(200))
    ad_content: Mapped[Optional[str]] = mapped_column(Text)
    target_audience: Mapped[Optional[str]] = mapped_column(Text)  # JSON string for targeting data
    budget: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    messages: Mapped[list["Message"]] = relationship(foreign_keys="Message.ad_id", back_populates="ad_campaign")


class AppSettings(Base):
    """Application settings model - stores editable configuration (Admin only)"""
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))  # facebook, whatsapp, ai, system
    is_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)  # For API keys, tokens
    description: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by: Mapped[str] = mapped_column(String(100), default="admin")
