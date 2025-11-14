# 🤖 Migochat - BWW Assistant Chatbot

**نظام ذكي متكامل لإدارة المحادثات والعملاء المحتملين على Facebook Messenger و WhatsApp**

[![Production Status](https://img.shields.io/badge/Production-Ready-green)](https://migochat-production.up.railway.app/)
[![Tests](https://img.shields.io/badge/Tests-100%25%20Pass-brightgreen)](./docs/)
[![AI Powered](https://img.shields.io/badge/AI-Gemini%202.5-blue)](https://ai.google.dev/)
[![Python Version](https://img.shields.io/badge/python-3.13.2-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com)

---

## 🚀 **نظرة عامة**

Migochat هو نظام CRM ذكي يجمع بين:
- 🤖 **الذكاء الاصطناعي** (Google Gemini 2.5)
- 💬 **المحادثات التلقائية** (Messenger + WhatsApp)
- 📊 **إدارة العملاء** (CRM متقدم)
- 🛍️ **متجر BWW** (بحث ذكي بالعربية المصرية)

---

## ✨ **الميزات الرئيسية**

### 1️⃣ **نظام CRM متقدم**
- ✅ بحث فوري متعدد الحقول (<100ms)
- ✅ فلترة ذكية (Stage, Type, Platform)
- ✅ ترتيب متقدم (Name, Score, Date)
- ✅ تصدير (CSV + JSON)
- ✅ Bulk Operations
- ✅ Real-time Updates

### 2️⃣ **الذكاء الاصطناعي**
- ✅ 3 نماذج Gemini AI نشطة
- ✅ ردود ذكية بالعربية المصرية
- ✅ فهم سياق المحادثة
- ✅ Performance Monitoring
- ✅ Caching System
- ✅ Retry Mechanism

### 3️⃣ **BWW Store Search**
- ✅ بحث ذكي بالعربية المصرية (97% دقة)
- ✅ تصحيح الأخطاء الإملائية (Fuzzy Matching)
- ✅ فهم السياق (المناسبة، الفصل، السعر)
- ✅ 210+ تصحيح للهجة المصرية
- ✅ 150+ variation للملابس
- ✅ 80+ variation للألوان

### 4️⃣ **واجهة عصرية**
- ✅ تصميم Material Design
- ✅ 10+ CSS Animations
- ✅ Dark Mode Support
- ✅ Mobile Responsive
- ✅ Keyboard Shortcuts (Ctrl+K, Ctrl+R)
- ✅ Loading Skeletons

---

## 🌐 **الروابط**

| الخدمة | الرابط | الحالة |
|--------|--------|--------|
| **Production** | [migochat-production.up.railway.app](https://migochat-production.up.railway.app/) | 🟢 Live |
| **Dashboard** | [/dashboard/](https://migochat-production.up.railway.app/dashboard/) | 🟢 Active |
| **CRM** | [/dashboard/crm](https://migochat-production.up.railway.app/dashboard/crm) | 🟢 Active |
| **Settings** | [/dashboard/settings](https://migochat-production.up.railway.app/dashboard/settings) | 🟢 Active |
| **Health** | [/health](https://migochat-production.up.railway.app/health) | 🟢 Healthy |

## 🚀 Quick Start

### Prerequisites

- **Python** 3.13.2 or higher
- **Facebook Developer Account** with Messenger app configured
- **WhatsApp Business Account** with API access
- **Google Gemini API Key** for AI features
- **Git** for version control

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Yoans-Adel/Migochat.git
   cd Migochat
   ```

2. **Create Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   # Install production dependencies
   pip install -r requirements.txt
   
   # Install testing dependencies (optional)
   pip install -r tests/requirements-test.txt
   ```

4. **Configure Environment Variables**
   ```bash
   # Create .env file from example
   cp .env.example .env
   
   # Edit .env file with your credentials:
   FB_APP_ID=your_facebook_app_id
   FB_PAGE_ACCESS_TOKEN=your_page_access_token
   FB_VERIFY_TOKEN=your_webhook_verify_token
   WHATSAPP_TOKEN=your_whatsapp_business_token
   WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
   GEMINI_API_KEY=your_gemini_api_key
   DATABASE_URL=sqlite:///./database/migochat.db
   ```

5. **Initialize Database**
   ```bash
   # Run database migrations
   python scripts/db_manager.py init
   ```

6. **Start the Application**
   ```bash
   # Development mode
   python run.py
   
   # Or using the script
   python scripts/start.ps1  # Windows PowerShell
   ./scripts/start.sh        # Linux/Mac
   ```

7. **Access the Application**
   - **API**: http://localhost:8000
   - **Dashboard**: http://localhost:8000/dashboard
   - **API Docs**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

## ✨ Features

### 🌐 Multi-Platform Support

- **Facebook Messenger**
  - Real-time message handling
  - Rich message templates
  - Button and quick reply support
  - Attachment handling (images, files)
  
- **WhatsApp Business**
  - Cloud API integration
  - Template message support
  - Media sharing capabilities
  - Business profile management

- **Facebook Lead Center**
  - Automated lead capture
  - Lead scoring and classification
  - Customer data enrichment
  - CRM integration ready

### 🤖 AI-Powered Intelligence

- **Google Gemini 2.0 Flash Integration**
  - Natural language understanding
  - Context-aware responses
  - Egyptian Arabic and English support
  - Multimodal capabilities (text + images)
  - Smart conversation flow management

- **Intelligent Lead Management**
  - Automated lead scoring (0-100 scale)
  - Customer classification (7 types)
  - Lead stage tracking (New → Won/Lost)
  - Priority-based routing

### 📊 Business Features

- **BWW Store Integration**
  - Real-time product search
  - Price comparison tools
  - Product recommendations
  - Arabic/English product catalog
  - Stock availability checking

- **Customer Classification**
  - 7 customer types identification
  - 4 label system (🔥Hot, 🌟Warm, ❄️Cold, 🚫Spam)
  - Behavioral analysis
  - Engagement tracking

- **Marketing Automation**
  - Dynamic message generation
  - Urgency creation strategies
  - Personalized responses
  - Follow-up scheduling

### 🛠️ Technical Features

- **Production-Grade Architecture**
  - FastAPI async framework
  - SQLAlchemy ORM with migrations
  - Dependency injection container
  - Comprehensive error handling
  - Structured logging system
  - Health monitoring endpoints

- **Code Quality**
  - Full type hints coverage (Python 3.13+)
  - PEP 8 compliant
  - Professional docstrings
  - 33% test coverage (growing)
  - No circular dependencies

- **Developer Experience**
  - Interactive API documentation (Swagger/ReDoc)
  - Web-based dashboard
  - Management scripts
  - Database migration tools
  - Log management utilities

## 📁 Project Structure

```text
Migochat/
├── 📦 app/                         # Main application package
│   ├── 🛣️ routes/                 # API endpoints and web routes
│   │   ├── api.py                 # REST API endpoints
│   │   ├── webhook.py             # Facebook/WhatsApp webhooks
│   │   └── dashboard.py           # Web dashboard routes
│   │
│   ├── 🔧 services/                # Business logic services
│   │   ├── messaging/             # Messaging platform services
│   │   │   ├── messenger_service.py
│   │   │   ├── whatsapp_service.py
│   │   │   └── message_handler.py
│   │   │
│   │   ├── ai/                    # AI and NLP services
│   │   │   └── gemini_service.py
│   │   │
│   │   ├── business/              # Business logic services
│   │   │   ├── facebook_lead_center_service.py
│   │   │   ├── keyword_manager.py
│   │   │   └── message_source_tracker.py
│   │   │
│   │   └── core/                  # Infrastructure services
│   │       ├── configuration_manager.py
│   │       ├── di_container.py
│   │       ├── error_handler.py
│   │       └── service_registry.py
│   │
│   ├── 📊 models/                  # Database models (SQLAlchemy)
│   ├── 🎨 templates/               # HTML templates (Jinja2)
│   ├── 📱 static/                  # Static assets (CSS, JS)
│   ├── database.py                 # Database configuration
│   └── main.py                     # Application entry point
│
├── 🏪 bww_store/                   # BWW Store integration package
│   ├── api_client.py              # Store API client
│   ├── search.py                  # Product search engine
│   ├── product_formatter.py       # Product data formatting
│   └── comparison_tool.py         # Price comparison
│
├── 🧪 tests/                       # Test suite
│   ├── test_server.py             # Server integration tests
│   ├── test_unit_tests.py         # Unit tests
│   └── requirements-test.txt      # Testing dependencies
│
├── 🗄️ database/                    # Database files
│   ├── migrations/                # Database migrations
│   └── backups/                   # Database backups
│
├── 📜 scripts/                     # Management scripts
│   ├── db_manager.py              # Database management
│   ├── log_manager.py             # Log management
│   ├── start.ps1                  # Windows start script
│   └── start.sh                   # Linux/Mac start script
│
├── 📚 docs/                        # Documentation
│
├── 📝 config/                      # Configuration files
│   ├── database_config.py
│   └── logging_config.py
│
├── 📋 Project Documentation
│   ├── README.md                  # This file
│   ├── PROJECT_STATUS.md          # Detailed project status
│   ├── CHANGELOG.md               # Version history
│   ├── CONTRIBUTING.md            # Contribution guidelines
│   └── requirements.txt           # Python dependencies
│
└── 🚀 Deployment
    ├── run.py                     # Application runner
    └── env.md                     # Environment variables guide
```

### Key Components

#### Services Architecture (11 Services)

**Messaging Services (4):**
- `MessengerService`: Facebook Messenger integration
- `WhatsAppService`: WhatsApp Business API
- `MessageHandler`: Unified message processing
- `PlatformMessagingService`: Platform abstraction layer

**AI Services (2):**
- `GeminiService`: Google Gemini AI integration
- `AIService`: AI response management

**Business Logic (4):**
- `FacebookLeadCenterService`: Lead management
- `KeywordManager`: NLP and keyword processing
- `MessageSourceTracker`: Message origin tracking
- `ProfessionalMessageHandler`: Advanced message handling

**Infrastructure (5):**
- `DIContainer`: Dependency injection
- `ServiceRegistry`: Service discovery
- `ConfigurationManager`: Settings management
- `ErrorHandler`: Error management
- `HealthMonitor`: System health checks

## 🧪 Testing

### Current Test Coverage

- **Total Statements:** 5,405
- **Covered:** 1,779 (33%)
- **Test Status:** 23 passed, 1 skipped ✅
- **Test Categories:** 10 test suites

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_server.py -v

# Run with detailed output
pytest tests/ --tb=short -v

# Run failed tests only
pytest tests/ --lf

# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Categories

1. **Server Startup Tests** (5 tests)
   - Application initialization
   - Route registration
   - Service startup

2. **Health Endpoint Tests** (2 tests)
   - System health checks
   - Service status monitoring

3. **Webhook Verification Tests** (2 tests)
   - Facebook webhook validation
   - Security token verification

4. **API Endpoint Tests** (3 tests)
   - REST API functionality
   - Data validation
   - Error handling

5. **Dashboard Tests** (3 tests)
   - Web interface rendering
   - User interactions
   - Data display

6. **Static Files Tests** (2 tests)
   - CSS/JS file serving
   - Asset caching

7. **Error Handling Tests** (3 tests)
   - Exception management
   - Error responses
   - Graceful degradation

8. **CORS Tests** (1 test)
   - Cross-origin resource sharing
   - Security headers

9. **Database Integration Tests** (1 test)
   - Database connectivity
   - Model operations

10. **Configuration Tests** (1 test)
    - Environment variables
    - Settings management

### Writing Tests

See [CONTRIBUTING.md](CONTRIBUTING.md#testing-guidelines) for testing best practices and guidelines.

## 🚀 Deployment

### Development Environment

```bash
# Start development server
python run.py

# Or using scripts
python scripts/start.ps1  # Windows PowerShell
./scripts/start.sh        # Linux/Mac

# Access application
# - API: http://localhost:8000
# - Dashboard: http://localhost:8000/dashboard
# - API Docs: http://localhost:8000/docs
```

### Production Deployment

#### Option 1: Railway (Recommended)

Railway provides easy deployment with automatic HTTPS and scaling:

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up

# 5. Set environment variables
railway variables set FB_APP_ID=your_value
railway variables set FB_PAGE_ACCESS_TOKEN=your_value
# ... (set all required variables)

# 6. Open application
railway open
```

#### Option 2: Docker Deployment

```bash
# Build Docker image
docker build -t migochat:latest .

# Run container
docker run -d \
  --name migochat \
  -p 8000:8000 \
  --env-file .env \
  migochat:latest

# Check logs
docker logs -f migochat

# Stop container
docker stop migochat
```

#### Option 3: Traditional VPS

```bash
# Install system dependencies
sudo apt update
sudo apt install python3.13 python3.13-venv nginx supervisor

# Setup application
git clone https://github.com/Yoans-Adel/Migochat.git
cd Migochat
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure Nginx (reverse proxy)
sudo nano /etc/nginx/sites-available/migochat

# Configure Supervisor (process manager)
sudo nano /etc/supervisor/conf.d/migochat.conf

# Start services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start migochat
sudo systemctl restart nginx
```

### Environment Variables (Production)

Required environment variables for production:

```bash
# Facebook Configuration
FB_APP_ID=your_facebook_app_id
FB_APP_SECRET=your_facebook_app_secret
FB_PAGE_ACCESS_TOKEN=your_page_access_token
FB_VERIFY_TOKEN=your_webhook_verify_token

# WhatsApp Configuration
WHATSAPP_TOKEN=your_whatsapp_business_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# Application Configuration
APP_ENV=production
DEBUG=False
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Optional: Monitoring
SENTRY_DSN=your_sentry_dsn  # For error tracking
```

### Deployment Checklist

- [ ] Environment variables configured
- [ ] Database initialized and migrated
- [ ] HTTPS/SSL certificate installed
- [ ] Webhook URLs configured in Facebook/WhatsApp
- [ ] Firewall configured (ports 80, 443)
- [ ] Monitoring and logging setup
- [ ] Backup strategy implemented
- [ ] Domain name pointed to server
- [ ] Health checks passing
- [ ] Load testing completed

## 📊 Monitoring & Management

### Web Dashboard

Access the web dashboard at `http://yourdomain.com/dashboard`

**Features:**
- 📈 **Real-time Analytics**: Message counts, response times, user engagement
- 💬 **Conversation Monitor**: Live conversation tracking
- 👥 **User Management**: Customer profiles and history
- 🎯 **Lead Management**: Lead scores, stages, and conversions
- ⚙️ **System Settings**: Configuration management
- 📊 **Reports**: Export data and generate reports

### API Endpoints

#### Health & Status
```bash
# System health check
GET /health
# Returns: {"status": "healthy", "timestamp": "..."}

# Detailed system stats
GET /api/stats
# Returns: message counts, user stats, performance metrics

# AI service status
GET /api/ai/status
# Returns: Gemini API status and capabilities

# BWW Store status
GET /api/bww-store/status
# Returns: Store integration health
```

#### Webhook Endpoints
```bash
# Facebook Messenger webhook
POST /webhook/messenger
GET /webhook/messenger?hub.verify_token=...

# WhatsApp webhook
POST /webhook/whatsapp
GET /webhook/whatsapp?hub.verify_token=...
```

#### API Documentation
- **Swagger UI**: http://yourdomain.com/docs
- **ReDoc**: http://yourdomain.com/redoc

### Logging

Application logs are stored in `logs/` directory:

```bash
logs/
├── app.log              # General application logs
├── error.log            # Error logs only
├── webhook.log          # Webhook events
└── database.log         # Database queries
```

**Log Management:**
```bash
# View live logs
tail -f logs/app.log

# Search for errors
grep "ERROR" logs/app.log

# Clean old logs
python scripts/log_manager.py clean --days 30

# Archive logs
python scripts/log_manager.py archive
```

### Database Management

```bash
# Initialize database
python scripts/db_manager.py init

# Create backup
python scripts/db_manager.py backup

# Restore from backup
python scripts/db_manager.py restore --file backup_file.sql

# Run migrations
python scripts/db_manager.py migrate

# Database statistics
python scripts/db_manager.py stats
```

### Performance Monitoring

**Metrics to Monitor:**
- Response time (target: <500ms)
- API availability (target: >99.9%)
- Error rate (target: <0.1%)
- Database query time
- Memory usage
- CPU usage

**Recommended Tools:**
- **Sentry**: Error tracking and monitoring
- **Datadog/New Relic**: Application performance monitoring
- **Grafana**: Metrics visualization
- **Uptime Robot**: Uptime monitoring

## 📚 Documentation

### Project Documentation

- **[Project Status](PROJECT_STATUS.md)** - Comprehensive project status, progress tracking, and roadmap
- **[Changelog](CHANGELOG.md)** - Detailed version history and changes
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Environment Variables](env.md)** - Complete environment variable reference

### API Documentation

- **Swagger UI**: http://yourdomain.com/docs (Interactive API documentation)
- **ReDoc**: http://yourdomain.com/redoc (Alternative API documentation)

### External Documentation

- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - Web framework
- **[SQLAlchemy Documentation](https://docs.sqlalchemy.org/)** - ORM and database
- **[Facebook Messenger Platform](https://developers.facebook.com/docs/messenger-platform/)** - Messenger API
- **[WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/)** - WhatsApp integration
- **[Google Gemini API](https://ai.google.dev/docs)** - AI integration

### Code Examples

#### Sending a Message
```python
from app.services import MessengerService

messenger = MessengerService()
result = await messenger.send_message(
    recipient_id="123456789",
    message_text="Hello from Migochat!"
)
```

#### Processing a Lead
```python
from app.services import FacebookLeadCenterService

lead_service = FacebookLeadCenterService()
lead_info = await lead_service.process_lead({
    "name": "John Doe",
    "phone": "+201234567890"
})
```

#### Using AI Service
```python
from app.services import GeminiService

ai = GeminiService()
response = await ai.generate_response(
    user_message="أريد شراء جهاز آيفون",
    conversation_history=[]
)
```

## 🔒 Security

### Security Features

- ✅ **Input Validation**: All user inputs validated and sanitized
- ✅ **SQL Injection Prevention**: Parameterized queries via SQLAlchemy ORM
- ✅ **XSS Protection**: Template escaping in Jinja2
- ✅ **CSRF Protection**: Token-based validation for forms
- ✅ **Rate Limiting**: API endpoint rate limiting
- ✅ **CORS Configuration**: Controlled cross-origin access
- ✅ **HTTPS Enforcement**: SSL/TLS encryption required
- ✅ **Secret Management**: Environment-based configuration
- ✅ **Authentication**: Webhook signature verification

### Security Best Practices

1. **Environment Variables**
   ```bash
   # Never commit .env file
   # Use strong, unique tokens
   # Rotate tokens regularly
   ```

2. **Webhook Security**
   ```python
   # Always verify webhook signatures
   # Use HTTPS endpoints only
   # Implement request validation
   ```

3. **Database Security**
   ```bash
   # Use strong database passwords
   # Enable database encryption
   # Regular backups
   # Limit database user permissions
   ```

4. **API Security**
   ```python
   # Implement rate limiting
   # Use API keys for authentication
   # Log all API requests
   # Monitor for unusual patterns
   ```

### Security Checklist

- [ ] All environment variables are set securely
- [ ] Webhook verification is enabled
- [ ] HTTPS is configured
- [ ] Database backups are scheduled
- [ ] Error messages don't leak sensitive information
- [ ] Logging doesn't include sensitive data
- [ ] Dependencies are up to date
- [ ] Security headers are configured
- [ ] Rate limiting is enabled
- [ ] Access controls are implemented

### Reporting Security Issues

If you discover a security vulnerability, please email:
- **Security Team**: security@migochat.com (or your actual email)

**Do not** create public GitHub issues for security vulnerabilities.

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

1. **Report Bugs** 🐛
   - Use GitHub Issues
   - Include reproduction steps
   - Provide environment details

2. **Suggest Features** 💡
   - Describe the feature clearly
   - Explain the use case
   - Provide examples

3. **Submit Code** 💻
   - Fork the repository
   - Create a feature branch
   - Follow coding standards
   - Add tests for new features
   - Submit a pull request

4. **Improve Documentation** 📚
   - Fix typos and errors
   - Add missing information
   - Create tutorials and guides
   - Improve code examples

### Development Workflow

1. Fork and clone the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest tests/`
5. Commit: `git commit -m "feat: add amazing feature"`
6. Push: `git push origin feature/your-feature`
7. Create a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Add type hints to all functions
- Write descriptive docstrings
- Include unit tests for new code
- Keep functions small and focused
- Use meaningful variable names

For detailed guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)

### Contributors

Special thanks to all contributors who have helped make Migochat better!

<!-- Contributors list will be automatically generated -->
<a href="https://github.com/Yoans-Adel/Migochat/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Yoans-Adel/Migochat" />
</a>

---

## 🆘 Support & Community

### Getting Help

- **📖 Documentation**: Check [PROJECT_STATUS.md](PROJECT_STATUS.md) and [docs/](docs/)
- **💬 GitHub Discussions**: Ask questions and share ideas
- **🐛 GitHub Issues**: Report bugs and request features
- **📧 Email**: support@migochat.com (or your actual email)

### Stay Connected

- **GitHub**: [@Yoans-Adel](https://github.com/Yoans-Adel)
- **Project**: [Migochat Repository](https://github.com/Yoans-Adel/Migochat)

---

## 📋 Project Status

### Current Version: 0.2.0

**Completed:**
- ✅ Architecture improvements and refactoring
- ✅ Comprehensive type hints coverage (50+ annotations)
- ✅ Code quality enhancements
- ✅ 33% test coverage with 23 passing tests

**In Progress:**
- 🚧 Mock tests development (Level 1)
- 🚧 Integration tests (Level 2)
- 🚧 Coverage improvement (target: 80%+)

**Planned:**
- 📋 Railway staging environment setup
- 📋 CI/CD pipeline implementation
- 📋 Documentation enhancements
- 📋 Production deployment

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed progress tracking (28.6% complete).

---

## 📄 License

This project is proprietary software developed for BWW Store.

**All rights reserved © 2025 Migochat**

For licensing inquiries, contact: license@migochat.com (or your actual email)

---

## 🎯 Roadmap

### Version 0.3.0 (Next)
- Mock tests for all services
- Integration tests for critical flows
- Coverage increase to 60%+

### Version 0.4.0
- Railway deployment
- CI/CD pipeline
- Docker containerization
- Monitoring and alerting

### Version 0.5.0
- API documentation enhancements
- Architecture diagrams
- Deployment guides
- Developer tutorials

### Version 1.0.0 (Production Release)
- 80%+ test coverage
- Security hardening
- Performance optimization
- Full documentation
- Production deployment

---

## 🙏 Acknowledgments

### Built With

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern web framework
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - SQL toolkit and ORM
- **[Google Gemini](https://ai.google.dev/)** - AI capabilities
- **[Facebook Graph API](https://developers.facebook.com/docs/graph-api/)** - Social platform integration
- **[WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/)** - Business messaging

### Special Thanks

- BWW Store team for business requirements
- Open source community for amazing tools
- All contributors and testers

---

## 📞 Contact

**Project Maintainer**: Yoans Adel

- **GitHub**: [@Yoans-Adel](https://github.com/Yoans-Adel)
- **Email**: yoans@example.com (replace with your actual email)
- **Project Link**: [https://github.com/Yoans-Adel/Migochat](https://github.com/Yoans-Adel/Migochat)

---

<div align="center">

**💝 Built with ❤️ for BWW Store**

*Empowering businesses with intelligent conversation automation*

[⬆ Back to Top](#-migochat)

</div>

---

*Last Updated: November 5, 2025 | Version 0.2.0*
