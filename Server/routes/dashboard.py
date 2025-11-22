from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta, timezone
import logging
import os

from database import get_db_session, User, Message, Conversation
from config.settings import settings
from app.services.messaging.messenger_service import MessengerService
from app.services.business.facebook_lead_center_service import FacebookLeadCenterService

logger = logging.getLogger(__name__)
router = APIRouter()

# Get absolute path to templates directory (app/templates)
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates_dir = os.path.join(base_dir, "app", "templates")
templates = Jinja2Templates(directory=templates_dir)

# Initialize services directly to avoid circular imports

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
        # Initialize default values in case database is unavailable
        total_users = 0
        total_messages = 0
        active_conversations = 0
        active_users = 0
        recent_messages = []
        lead_analytics = {"total_leads": 0, "qualified_leads": 0, "converted_leads": 0}
        
        # Initialize system status with defaults
        system_status = {
            "webhook": {"status": "active", "label": "Active"},
            "database": {"status": "unknown", "label": "Checking..."},
            "messenger": {"status": "unknown", "label": "Checking..."},
            "ai_service": {"status": "unknown", "label": "Checking..."},
            "lead_automation": {"status": "unknown", "label": "Checking..."},
            "whatsapp": {"status": "unknown", "label": "Checking..."}
        }

        # Check Database Connection
        db_connected = False
        try:
            with get_db_session() as db:
                db.execute("SELECT 1").fetchone()
                system_status["database"] = {"status": "connected", "label": "Connected"}
                db_connected = True
                
                # Get statistics only if database is connected
                try:
                    total_users = db.query(User).count()
                    total_messages = db.query(Message).count()
                    active_conversations = db.query(Conversation).filter(Conversation.is_active.is_(True)).count()
                    
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
                except Exception as e:
                    logger.warning(f"Error getting database statistics: {e}")
                    
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            system_status["database"] = {"status": "error", "label": "Disconnected"}

        # Check Messenger Service
        try:
            # Verify Messenger API token and connection
            fb_token = settings.FB_PAGE_ACCESS_TOKEN
            if fb_token and len(fb_token) > 50:
                # Try to verify token is valid
                try:
                    import httpx
                    verify_url = f"https://graph.facebook.com/v24.0/me?access_token={fb_token}"
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.get(verify_url)
                        if response.status_code == 200:
                            system_status["messenger"] = {"status": "active", "label": "Active"}
                        else:
                            system_status["messenger"] = {"status": "error", "label": "Invalid Token"}
                except Exception as verify_error:
                    logger.warning(f"Messenger token verification failed: {verify_error}")
                    # If verification fails but token exists, mark as inactive
                    system_status["messenger"] = {"status": "inactive", "label": "Token Error"}
            else:
                system_status["messenger"] = {"status": "inactive", "label": "Not Configured"}
        except Exception as e:
            logger.error(f"Messenger check failed: {e}")
            system_status["messenger"] = {"status": "error", "label": "Error"}

        # Check AI Service (Gemini)
        try:
            gemini_key = settings.GEMINI_API_KEY
            if gemini_key and len(gemini_key) > 20:
                system_status["ai_service"] = {"status": "active", "label": "Active"}
            else:
                system_status["ai_service"] = {"status": "inactive", "label": "Not Configured"}
        except Exception as e:
            logger.warning(f"AI service check failed: {e}")
            system_status["ai_service"] = {"status": "error", "label": "Error"}

        # Check Lead Automation
        try:
            if db_connected:
                lead_analytics = lead_automation.get_lead_analytics()
                if lead_analytics.get("total_leads", 0) >= 0:
                    system_status["lead_automation"] = {"status": "active", "label": "Active"}
                else:
                    system_status["lead_automation"] = {"status": "inactive", "label": "Inactive"}
            else:
                system_status["lead_automation"] = {"status": "inactive", "label": "DB Required"}
        except Exception as e:
            logger.warning(f"Lead automation check failed: {e}")
            system_status["lead_automation"] = {"status": "error", "label": "Error"}

        # Check WhatsApp Integration
        try:
            whatsapp_token = settings.WHATSAPP_ACCESS_TOKEN
            whatsapp_phone = settings.WHATSAPP_PHONE_NUMBER_ID
            if whatsapp_token and whatsapp_phone and len(whatsapp_token) > 50:
                system_status["whatsapp"] = {"status": "active", "label": "Active"}
            else:
                system_status["whatsapp"] = {"status": "inactive", "label": "Not Configured"}
        except Exception as e:
            logger.warning(f"WhatsApp check failed: {e}")
            system_status["whatsapp"] = {"status": "error", "label": "Error"}

        # Prepare stats for template
        stats = {
            "total_users": total_users,
            "total_messages": total_messages,
            "active_conversations": active_conversations,
            "active_users": active_users,
            "recent_messages": recent_messages,
            "lead_analytics": lead_analytics,
            "system_status": system_status
        }

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "stats": stats
        })

    except Exception as e:
        logger.error(f"Critical error in dashboard: {e}")
        logger.exception("Dashboard exception details:")
        # Return error page with minimal data
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "stats": {
                "total_users": 0,
                "total_messages": 0,
                "active_conversations": 0,
                "active_users": 0,
                "recent_messages": [],
                "lead_analytics": {"total_leads": 0, "qualified_leads": 0, "converted_leads": 0},
                "system_status": {
                    "webhook": {"status": "error", "label": "Error"},
                    "database": {"status": "error", "label": "Error"},
                    "messenger": {"status": "error", "label": "Error"},
                    "ai_service": {"status": "error", "label": "Error"},
                    "lead_automation": {"status": "error", "label": "Error"},
                    "whatsapp": {"status": "error", "label": "Error"}
                }
            }
        })


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
