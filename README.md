# 🤖 Bww-AI-Assistant

## Professional Multi-Platform AI Assistant for BWW Store

A comprehensive, production-ready chatbot system supporting Facebook Messenger, WhatsApp Business, and Facebook Lead Center integration with AI-powered customer service.

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)](docs/README.md)

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Facebook Developer Account
- WhatsApp Business Account
- Gemini API Key (optional)

### Installation

1. **Clone and Setup**

   ```bash
   git clone <repository-url>
   cd Bww-AI-Assistant
   python scripts/setup.py
   ```

2. **Install Dependencies**

   ```bash
   # Install production dependencies
   pip install -r requirements.txt
   
   # Install testing dependencies (optional)
   pip install -r tests/requirements-test.txt
   ```

3. **Configure Environment**

   ```bash
   # Edit .env file with your credentials
   FB_APP_ID=your_facebook_app_id
   FB_PAGE_ACCESS_TOKEN=your_page_access_token
   WHATSAPP_TOKEN=your_whatsapp_token
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. **Start Application**

   ```bash
   python run.py
   ```

## ✨ Features

### Core Functionality

- **Multi-Platform Support**: Facebook Messenger, WhatsApp Business, Lead Center
- **AI-Powered Responses**: Gemini 2.5 Flash with rule-based fallback
- **Lead Management**: Automated scoring, staging, and customer classification
- **Product Integration**: Real-time BWW Store product search and recommendations
- **Multi-language Support**: Egyptian Arabic and English with cultural context

### Advanced Features

- **Contextual Conversations**: Multi-turn conversation management
- **Customer Classification**: 7 customer types, 4 labels, scoring system
- **Marketing Automation**: Dynamic messages and urgency creation
- **Human Agent Escalation**: Smart handover when needed

### Technical Features

- **Production-Ready**: Comprehensive error handling and logging
- **Scalable Architecture**: FastAPI with async support
- **Database Management**: SQLAlchemy ORM with SQLite/PostgreSQL
- **Web Dashboard**: Real-time monitoring and management interface

## 📁 Project Structure

```text
Bww-AI-Assistant/
├── app/                    # Main application code
│   ├── routes/            # API endpoints and web routes
│   ├── services/           # Business logic services
│   ├── models/             # Data models
│   └── database.py         # Database configuration
├── bww_store/              # BWW Store integration
├── tests/                  # Test suite
├── scripts/                # Management scripts
├── docs/                   # Documentation
├── templates/              # Web dashboard templates
├── static/                 # Static assets
└── requirements.txt         # Python dependencies
```

## 🧪 Testing

```bash
# Run all tests
python scripts/run_production_tests.py

# Run specific test types
python -m pytest tests/test_unit_tests.py -v
python -m pytest tests/test_integration_tests.py -v
```

## 🚀 Deployment

For detailed deployment instructions, see [docs/README.md](docs/README.md).

**Quick Production Setup:**

```bash
# Install dependencies
sudo apt update
sudo apt install python3.12 python3.12-venv nginx

# Setup application
python scripts/setup_environment.py

# Start services
python scripts/start_server.py
```

## 📊 Monitoring

### Web Dashboard

Access at `http://yourdomain.com/dashboard` to:

- Monitor conversations
- View lead analytics
- Manage users
- Check system status

### API Endpoints

- **Health Check**: `GET /api/stats`
- **System Status**: `GET /api/ai/status`
- **BWW Store Status**: `GET /api/bww-store/status`

## 📚 Documentation

- **[Complete Documentation](docs/README.md)** - Comprehensive setup and deployment guide
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Essential commands and troubleshooting

## 🔒 Security

- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting
- CORS configuration
- HTTPS enforcement

## 🤝 Support

- **Technical Support**: [support@company.com]
- **Documentation**: [docs.company.com]
- **Status Page**: [status.company.com]

## 📄 License

This project is proprietary software. All rights reserved.

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
- **v1.1.0**: Added AI integration and lead management
- **v1.2.0**: Enhanced BWW Store integration
- **v1.3.0**: Production-ready with comprehensive testing

---

## 💝 Built with ❤️ for BWW Store

For more information, visit our [documentation](docs/) or contact [support@company.com](mailto:support@company.com).
