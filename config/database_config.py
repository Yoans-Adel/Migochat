# Database Configuration for Bww-AI-Assistant
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
import enum

# Database configuration
DATABASE_DIR = Path("database")
DATABASE_DIR.mkdir(exist_ok=True)

# Database file path
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/bww_ai_assistant.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "check_same_thread": False,  # For SQLite
        "timeout": 20
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Enums


class MessageDirection(enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageStatus(enum.Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class MessageSource(enum.Enum):
    MESSENGER = "messenger"
    WHATSAPP = "whatsapp"
    LEAD_CENTER = "lead_center"
    MANUAL = "manual"


class LeadStage(enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    HOT = "hot"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class CustomerLabel(enum.Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    UNQUALIFIED = "unqualified"


class CustomerType(enum.Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    WHOLESALE = "wholesale"
    RETAIL = "retail"
    LEAD = "lead"


class PostType(enum.Enum):
    POST = "post"
    STORY = "story"
    REEL = "reel"
    AD = "ad"


class Governorate(enum.Enum):
    CAIRO = "cairo"
    ALEXANDRIA = "alexandria"
    GIZA = "giza"
    SHARKIA = "sharkia"
    DAQAHLIA = "daqahlia"
    BEHEIRA = "beheira"
    KAFR_EL_SHEIKH = "kafr_el_sheikh"
    GHARBIA = "gharbia"
    MONUFIA = "monufia"
    QALYUBIA = "qalyubia"
    DAMIETTA = "damietta"
    PORT_SAID = "port_said"
    ISMAILIA = "ismailia"
    SUEZ = "suez"
    NORTH_SINAI = "north_sinai"
    SOUTH_SINAI = "south_sinai"
    RED_SEA = "red_sea"
    NEW_VALLEY = "new_valley"
    MATROUH = "matrouh"
    LUXOR = "luxor"
    ASWAN = "aswan"
    QENA = "qena"
    SOHAG = "sohag"
    ASSIUT = "assiut"
    MINYA = "minya"
    BENI_SUEF = "beni_suef"
    FAYOUM = "fayoum"

# Database Models


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    psid = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_pic = Column(String(500))
    locale = Column(String(10), default="ar_AR")
    timezone = Column(Integer, default=2)
    gender = Column(String(10))
    governorate = Column(Enum(Governorate))

    # Lead management fields
    lead_stage = Column(Enum(LeadStage), default=LeadStage.NEW)
    customer_label = Column(Enum(CustomerLabel), default=CustomerLabel.COLD)
    customer_type = Column(Enum(CustomerType), default=CustomerType.INDIVIDUAL)
    lead_score = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_message_at = Column(DateTime)
    last_seen_at = Column(DateTime)

    # Relationships
    messages = relationship("Message", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    lead_activities = relationship("LeadActivity", back_populates="user")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    facebook_message_id = Column(String(255), unique=True, index=True)
    whatsapp_message_id = Column(String(255), unique=True, index=True)

    # Message content
    text = Column(Text)
    message_type = Column(String(50), default="text")
    direction = Column(Enum(MessageDirection), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT)

    # Source tracking
    source = Column(Enum(MessageSource), default=MessageSource.MESSENGER)
    post_id = Column(String(255))
    ad_campaign_id = Column(String(255))

    # AI response tracking
    is_ai_response = Column(Boolean, default=False)
    ai_model_used = Column(String(50))
    response_time_ms = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="messages")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Conversation metadata
    is_active = Column(Boolean, default=True)
    message_count = Column(Integer, default=0)
    last_message_text = Column(Text)
    last_message_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="conversations")


class LeadActivity(Base):
    __tablename__ = "lead_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Activity details
    activity_type = Column(String(50), nullable=False)  # message, call, meeting, etc.
    description = Column(Text)
    stage_before = Column(Enum(LeadStage))
    stage_after = Column(Enum(LeadStage))
    label_before = Column(Enum(CustomerLabel))
    label_after = Column(Enum(CustomerLabel))
    score_change = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="lead_activities")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    facebook_post_id = Column(String(255), unique=True, index=True)

    # Post details
    post_type = Column(Enum(PostType), default=PostType.POST)
    content = Column(Text)
    media_url = Column(String(500))

    # Engagement metrics
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    posted_at = Column(DateTime)


class AdCampaign(Base):
    __tablename__ = "ad_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    facebook_campaign_id = Column(String(255), unique=True, index=True)

    # Campaign details
    name = Column(String(255))
    objective = Column(String(100))
    status = Column(String(50))

    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Integer, default=0)  # in cents

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime)
    ended_at = Column(DateTime)

# Database utility functions


def get_session():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_database():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise


def drop_database():
    """Drop all database tables"""
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ Database tables dropped successfully")
    except Exception as e:
        print(f"❌ Error dropping database tables: {e}")
        raise


def backup_database():
    """Create a backup of the database"""
    try:
        import shutil
        from datetime import datetime

        backup_dir = DATABASE_DIR / "backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"bww_ai_assistant_backup_{timestamp}.db"

        shutil.copy2(DATABASE_DIR / "bww_ai_assistant.db", backup_file)
        print(f"✅ Database backup created: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Error creating database backup: {e}")
        raise


def restore_database(backup_file: str) -> None:
    """Restore database from backup"""
    try:
        import shutil
        from pathlib import Path

        backup_path = Path(backup_file)
        shutil.copy2(backup_path, DATABASE_DIR / "bww_ai_assistant.db")
        print(f"✅ Database restored from: {backup_file}")
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        raise

# Database health check


def check_database_health() -> dict[str, str | list[str]]:
    """Check database health and connectivity"""
    try:
        from sqlalchemy import text
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()

        # Check if all tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        expected_tables = [
            "users", "messages", "conversations",
            "lead_activities", "posts", "ad_campaigns"
        ]

        missing_tables = [table for table in expected_tables if table not in tables]

        if missing_tables:
            return {
                "status": "unhealthy",
                "error": f"Missing tables: {missing_tables}"
            }

        return {
            "status": "healthy",
            "tables": str(tables),
            "connection": "ok"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
