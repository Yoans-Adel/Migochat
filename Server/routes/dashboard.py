from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta, timezone
import logging

from database import get_db_session, User, Message, Conversation
from Server.config import settings
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# Get absolute path to templates directory (app/templates)
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates_dir = os.path.join(base_dir, "app", "templates")
templates = Jinja2Templates(directory=templates_dir)

# Initialize services directly to avoid circular imports
from app.services.messaging.messenger_service import MessengerService  # noqa: E402
from app.services.business.facebook_lead_center_service import FacebookLeadCenterService  # noqa: E402

messenger_service = MessengerService()
lead_automation = FacebookLeadCenterService()

# Helper functions


def get_users_by_last_message(db: Session, limit: int = 100):
    """Get users ordered by last message timestamp"""
    return db.query(User).order_by(desc(User.last_message_at)).limit(limit).all()


def handle_dashboard_error(error: Exception, view_name: str):
    """Handle dashboard errors consistently"""
    logger.error(f"Error loading {view_name}: {error}")
    raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/crm", response_class=HTMLResponse)
async def crm_view(request: Request):
    """Unified CRM page for Leads, Users, and Bulk Operations"""
    try:
        return templates.TemplateResponse("crm.html", {
            "request": request
        })
    except Exception as e:
        logger.error(f"Error in CRM view: {e}")
        logger.exception("CRM view exception details:")
        handle_dashboard_error(e, "CRM view")


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page with lead analytics"""
    try:
        with get_db_session() as db:
            # Get statistics
            total_users = db.query(User).count()
            total_messages = db.query(Message).count()
            active_conversations = db.query(Conversation).filter(Conversation.is_active.is_(True)).count()

            # Lead analytics with error handling
            try:
                lead_analytics = lead_automation.get_lead_analytics()
            except Exception as e:
                logger.warning(f"Lead analytics failed: {e}")
                lead_analytics = {"total_leads": 0, "qualified_leads": 0, "converted_leads": 0}

            # Recent messages (last 24 hours)
            yesterday = datetime.now(timezone.utc) - timedelta(days=1)
            recent_messages = db.query(Message).join(User).filter(
                Message.timestamp >= yesterday
            ).order_by(desc(Message.timestamp)).limit(10).all()

            # Active users (messaged in last 7 days)
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            active_users = db.query(User).filter(
                User.last_message_at >= week_ago
            ).count()

            stats = {
                "total_users": total_users,
                "total_messages": total_messages,
                "active_conversations": active_conversations,
                "active_users": active_users,
                "recent_messages": recent_messages,
                "lead_analytics": lead_analytics
            }

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "stats": stats
        })

    except Exception as e:
        handle_dashboard_error(e, "dashboard")


@router.get("/settings", response_class=HTMLResponse)
async def settings_view(request: Request):
    """Unified settings page with comprehensive configuration management"""
    try:
        # Get Railway production URL
        railway_url = "https://migochat-production.up.railway.app"

        # Check if Gemini API key is configured (with safe access)
        try:
            gemini_key = settings.GEMINI_API_KEY
            gemini_available = bool(gemini_key and len(gemini_key) > 0)
        except Exception:
            gemini_available = False
            gemini_key = ""

        # Get model safely
        try:
            gemini_model = settings.GEMINI_MODEL or "gemini-2.5-flash"
        except Exception:
            gemini_model = "gemini-2.5-flash"

        # Don't mask tokens - show full values for editing
        # Users can see/hide them using the password toggle button
        settings_info = {
            # Facebook Settings
            "fb_app_id": settings.FB_APP_ID or "",
            "fb_page_id": settings.FB_PAGE_ID or "",
            "fb_verify_token": settings.FB_VERIFY_TOKEN or "",
            "fb_page_access_token": settings.FB_PAGE_ACCESS_TOKEN or "",

            # WhatsApp Settings
            "whatsapp_phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID or "",
            "whatsapp_verify_token": settings.WHATSAPP_VERIFY_TOKEN or "",
            "whatsapp_access_token": settings.WHATSAPP_ACCESS_TOKEN or "",

            # Webhook URLs (Railway)
            "messenger_webhook_url": f"{railway_url}/webhook/messenger",
            "whatsapp_webhook_url": f"{railway_url}/webhook/whatsapp",

            # AI Model Settings
            "ai_provider": "Gemini",
            "ai_model": gemini_model,
            "ai_available": gemini_available,
            "gemini_api_key": gemini_key or "",

            # System Info
            "environment": settings.ENVIRONMENT or "production",
            "debug_mode": settings.DEBUG,
            "timezone": settings.TIMEZONE or "UTC"
        }

        return templates.TemplateResponse("settings.html", {
            "request": request,
            "settings": settings_info
        })

    except Exception as e:
        logger.error(f"Error in settings view: {e}")
        logger.exception("Settings view exception details:")
        handle_dashboard_error(e, "settings view")
