# 🗄️ Database Schema Documentation

**Project**: Migochat (BWW AI Assistant)  
**Database**: SQLite (Production-ready with SQLAlchemy ORM)  
**Last Updated**: 2025-11-11  
**Version**: 1.0

---

## 📋 Overview

The Migochat database is designed to handle multi-platform social media messaging with intelligent lead management and analytics tracking.

### Database Features:
- ✅ **Multi-platform support** (Facebook Messenger, WhatsApp)
- ✅ **Lead lifecycle tracking** (Intake → Nurture → Convert)
- ✅ **Message source attribution** (Ads, Posts, Direct)
- ✅ **Conversation threading**
- ✅ **Activity audit trails**
- ✅ **Dynamic settings storage**

---

## 🏗️ Entity Relationship Diagram

```
┌──────────────┐
│    User      │ ← Customer/Lead (PSID-based)
└──────┬───────┘
       │
       ├──────────► Messages (1:N)
       ├──────────► LeadActivities (1:N)
       └──────────► Conversations (1:N)

┌──────────────┐
│   Message    │ ← All platform messages
└──────┬───────┘
       │
       ├──────────► User (N:1)
       ├──────────► Post (N:1) [optional]
       └──────────► AdCampaign (N:1) [optional]

┌──────────────┐
│    Post      │ ← Facebook posts tracking
└──────┬───────┘
       │
       └──────────► Messages (1:N)

┌──────────────┐
│ AdCampaign   │ ← Facebook ads tracking
└──────┬───────┘
       │
       └──────────► Messages (1:N)

┌──────────────┐
│ LeadActivity │ ← Lead management history
└──────┬───────┘
       │
       └──────────► User (N:1)

┌──────────────┐
│ Conversation │ ← Active conversation threads
└──────┬───────┘
       │
       └──────────► User (N:1)

┌──────────────┐
│ AppSettings  │ ← Dynamic configuration
└──────────────┘
```

---

## 📊 Tables Schema

### 1. `users` - Customer/Lead Management

**Purpose**: Store customer information and lead tracking data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, INDEX | Auto-increment user ID |
| `psid` | VARCHAR(50) | UNIQUE, INDEX, NOT NULL | Page-Scoped ID (Facebook) or Phone (WhatsApp) |
| `first_name` | VARCHAR(100) | NULLABLE | Customer first name |
| `last_name` | VARCHAR(100) | NULLABLE | Customer last name |
| `profile_pic` | VARCHAR(500) | NULLABLE | Profile picture URL |
| `governorate` | ENUM | NULLABLE | Egyptian governorate (CAIRO, GIZA, etc.) |
| `platform` | VARCHAR(50) | DEFAULT 'facebook' | Source platform (facebook, whatsapp) |
| `phone_number` | VARCHAR(20) | NULLABLE | Phone number (WhatsApp users) |
| `created_at` | DATETIME | DEFAULT NOW() | Account creation timestamp |
| `last_message_at` | DATETIME | NULLABLE | Last message timestamp |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active status flag |
| `lead_stage` | ENUM | DEFAULT 'INTAKE' | Lead pipeline stage |
| `customer_label` | ENUM | NULLABLE | Customer classification |
| `customer_type` | ENUM | NULLABLE | Customer type (NEW, RETURNING, VIP) |
| `lead_score` | INTEGER | DEFAULT 0 | Lead scoring (0-100) |
| `last_stage_change` | DATETIME | DEFAULT NOW() | Last lead stage update |

**Indexes**:
- PRIMARY: `id`
- UNIQUE: `psid`
- INDEX: `id`, `psid`

**Relationships**:
- ➡️ `messages` (1:N)
- ➡️ `lead_activities` (1:N)
- ➡️ `conversations` (1:1)

---

### 2. `messages` - Message Storage

**Purpose**: Store all messages across all platforms with source tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Auto-increment message ID |
| `user_id` | INTEGER | FOREIGN KEY → users.id | Message sender/recipient user |
| `sender_id` | VARCHAR(50) | NOT NULL | PSID of sender |
| `recipient_id` | VARCHAR(50) | NOT NULL | Page ID or phone number |
| `message_text` | TEXT | NULLABLE | Message content |
| `direction` | ENUM | NOT NULL | INBOUND or OUTBOUND |
| `status` | ENUM | DEFAULT 'SENT' | Message delivery status |
| `timestamp` | DATETIME | DEFAULT NOW() | Message timestamp |
| `facebook_message_id` | VARCHAR(100) | UNIQUE, NULLABLE | Facebook message ID |
| `message_type` | VARCHAR(50) | DEFAULT 'text' | Message type (text, image, file) |
| `message_metadata` | TEXT | NULLABLE | JSON metadata |
| `platform` | VARCHAR(50) | DEFAULT 'facebook' | Platform source |
| `message_source` | ENUM | DEFAULT 'DIRECT_MESSAGE' | Message source type |
| `post_id` | INTEGER | FOREIGN KEY → posts.id, NULLABLE | Related post |
| `post_type` | ENUM | NULLABLE | Post type if from post |
| `ad_id` | INTEGER | FOREIGN KEY → ad_campaigns.id, NULLABLE | Related ad campaign |
| `comment_id` | VARCHAR(100) | NULLABLE | Facebook comment ID |
| `referral_source` | VARCHAR(200) | NULLABLE | Referral tracking |

**Indexes**:
- PRIMARY: `id`
- UNIQUE: `facebook_message_id`
- INDEX: `user_id`, `timestamp`

**Relationships**:
- ⬅️ `user` (N:1)
- ⬅️ `post` (N:1, optional)
- ⬅️ `ad_campaign` (N:1, optional)

---

### 3. `conversations` - Conversation Tracking

**Purpose**: Track active conversation threads and metrics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Conversation ID |
| `user_id` | INTEGER | FOREIGN KEY → users.id | Related user |
| `started_at` | DATETIME | DEFAULT NOW() | Conversation start time |
| `last_activity` | DATETIME | DEFAULT NOW() | Last message time |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active status |
| `message_count` | INTEGER | DEFAULT 0 | Total messages in thread |

**Relationships**:
- ⬅️ `user` (N:1)

---

### 4. `lead_activities` - Lead Management History

**Purpose**: Audit trail for all lead management changes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Activity ID |
| `user_id` | INTEGER | FOREIGN KEY → users.id | Related user |
| `activity_type` | VARCHAR(50) | NOT NULL | Activity type (stage_change, label_change) |
| `old_value` | VARCHAR(100) | NULLABLE | Previous value |
| `new_value` | VARCHAR(100) | NULLABLE | New value |
| `reason` | TEXT | NULLABLE | Change reason/notes |
| `timestamp` | DATETIME | DEFAULT NOW() | Activity timestamp |
| `automated` | BOOLEAN | DEFAULT FALSE | Automated vs manual change |

**Relationships**:
- ⬅️ `user` (N:1)

---

### 5. `posts` - Facebook Posts Tracking

**Purpose**: Track Facebook posts for message source attribution.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Post ID |
| `facebook_post_id` | VARCHAR(100) | UNIQUE, NOT NULL | Facebook post ID |
| `post_type` | ENUM | NOT NULL | Post type (PRODUCT, INFO, AD) |
| `post_content` | TEXT | NULLABLE | Post text content |
| `post_price` | VARCHAR(100) | NULLABLE | Product price if applicable |
| `post_data` | TEXT | NULLABLE | JSON product data |
| `created_at` | DATETIME | DEFAULT NOW() | Post creation time |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active status |

**Relationships**:
- ➡️ `messages` (1:N)

---

### 6. `ad_campaigns` - Facebook Ads Tracking

**Purpose**: Track Facebook ad campaigns for attribution.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Campaign ID |
| `facebook_ad_id` | VARCHAR(100) | UNIQUE, NOT NULL | Facebook ad ID |
| `campaign_name` | VARCHAR(200) | NULLABLE | Campaign name |
| `ad_content` | TEXT | NULLABLE | Ad content/copy |
| `target_audience` | TEXT | NULLABLE | JSON targeting data |
| `budget` | VARCHAR(100) | NULLABLE | Campaign budget |
| `status` | VARCHAR(50) | DEFAULT 'active' | Campaign status |
| `created_at` | DATETIME | DEFAULT NOW() | Campaign start date |

**Relationships**:
- ➡️ `messages` (1:N)

---

### 7. `app_settings` - Dynamic Configuration

**Purpose**: Store editable configuration (admin-managed).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | Setting ID |
| `key` | VARCHAR(100) | UNIQUE, INDEX, NOT NULL | Setting key name |
| `value` | TEXT | NULLABLE | Setting value |
| `category` | VARCHAR(50) | NULLABLE | Category (facebook, whatsapp, ai) |
| `is_sensitive` | BOOLEAN | DEFAULT FALSE | Sensitive data flag (API keys) |
| `description` | TEXT | NULLABLE | Setting description |
| `updated_at` | DATETIME | AUTO UPDATE | Last update timestamp |
| `updated_by` | VARCHAR(100) | DEFAULT 'admin' | Who updated |

**Example Settings**:
```python
{
    "fb_page_access_token": "EAAe...",  # is_sensitive=True
    "gemini_api_key": "AIza...",        # is_sensitive=True
    "lead_scoring_threshold": "75",     # is_sensitive=False
}
```

---

## 🔑 Enumerations (ENUMs)

### MessageSource
```python
DIRECT_MESSAGE = "direct_message"
POST_COMMENT = "post_comment"
AD_MESSAGE = "ad_message"
LEAD_AD = "lead_ad"
STORY_REPLY = "story_reply"
```

### PostType
```python
PRODUCT = "product"
INFO = "info"
AD = "ad"
```

### LeadStage
```python
INTAKE = "intake"          # Initial contact
NURTURE = "nurture"        # Follow-up phase
CONVERT = "convert"        # Ready to purchase
QUALIFIED = "qualified"    # High-value lead
UNQUALIFIED = "unqualified"  # Low potential
LOST = "lost"              # Lost opportunity
```

### CustomerLabel
```python
HOT = "hot"                # High interest
WARM = "warm"              # Moderate interest
COLD = "cold"              # Low interest
```

### CustomerType
```python
NEW = "new"
RETURNING = "returning"
VIP = "vip"
```

### Governorate
```python
CAIRO = "cairo"
GIZA = "giza"
ALEXANDRIA = "alexandria"
# ... all 27 Egyptian governorates
```

### MessageDirection
```python
INBOUND = "inbound"        # Customer → Bot
OUTBOUND = "outbound"      # Bot → Customer
```

### MessageStatus
```python
SENT = "sent"
DELIVERED = "delivered"
READ = "read"
FAILED = "failed"
```

---

## 📈 Database Statistics

**Tables**: 7  
**Relationships**: 8  
**Indexes**: 12+  
**Enums**: 8  

**Estimated Size** (for 10,000 users):
- `users`: ~2 MB
- `messages`: ~50 MB (avg 50 msgs/user)
- `conversations`: ~0.5 MB
- `lead_activities`: ~5 MB
- **Total**: ~60 MB

---

## 🔧 Performance Optimizations

### Indexes:
- ✅ `users.psid` - UNIQUE index for fast PSID lookups
- ✅ `messages.user_id` - Fast message queries per user
- ✅ `messages.timestamp` - Time-based queries
- ✅ `app_settings.key` - Fast settings lookup

### Query Patterns:
```python
# Fast PSID lookup
user = session.query(User).filter(User.psid == "123456").first()

# Messages for user (indexed)
messages = session.query(Message).filter(Message.user_id == user.id).all()

# Recent conversations (indexed timestamp)
recent = session.query(Message).order_by(Message.timestamp.desc()).limit(50).all()
```

---

## 🔒 Data Integrity

### Constraints:
- ✅ Foreign Keys enforced
- ✅ UNIQUE constraints on external IDs
- ✅ NOT NULL on critical fields
- ✅ DEFAULT values for timestamps

### Cascading:
- ❌ **No CASCADE DELETE** (data preservation)
- ⚠️ Manual cleanup required for orphaned records

---

## 📝 Migration Strategy

Currently: **Direct SQLAlchemy models** (no migrations yet)  
Future: **Alembic migrations** for schema versioning

**Migration Path**:
1. Initialize Alembic: `alembic init database/migrations`
2. Generate baseline: `alembic revision --autogenerate -m "Initial schema"`
3. Apply migrations: `alembic upgrade head`

---

**Documentation Version**: 1.0  
**Last Updated**: 2025-11-11  
**Maintained By**: Development Team
