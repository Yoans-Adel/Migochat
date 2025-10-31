from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.database import get_session, User, Message, Conversation, MessageDirection, MessageStatus, LeadStage, CustomerLabel, CustomerType, LeadActivity
from Server.config import settings
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# Get absolute path to templates directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(base_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)

# Initialize services directly to avoid circular imports
from app.services.messaging.messenger_service import MessengerService
from app.services.business.facebook_lead_center_service import FacebookLeadCenterService

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

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request, db: Session = Depends(get_session)):
    """Main dashboard page with lead analytics"""
    try:
        # Get statistics
        total_users = db.query(User).count()
        total_messages = db.query(Message).count()
        active_conversations = db.query(Conversation).filter(Conversation.is_active == True).count()
        
        # Lead analytics with error handling
        try:
            lead_analytics = lead_automation.get_lead_analytics()
        except Exception as e:
            logger.warning(f"Lead analytics failed: {e}")
            lead_analytics = {"total_leads": 0, "qualified_leads": 0, "converted_leads": 0}
        
        # Recent messages (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_messages = db.query(Message).join(User).filter(
            Message.timestamp >= yesterday
        ).order_by(desc(Message.timestamp)).limit(10).all()
        
        # Active users (messaged in last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
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

@router.get("/leads", response_class=HTMLResponse)
async def leads_view(request: Request, db: Session = Depends(get_session)):
    """Lead management page"""
    try:
        logger.info("Starting leads_view")
        
        # Get leads with pagination
        leads = get_users_by_last_message(db, 100)
        logger.info(f"Found {len(leads)} leads")
        
        # Get lead analytics
        lead_analytics = lead_automation.get_lead_analytics()
        logger.info(f"Lead analytics: {lead_analytics}")
        
        return templates.TemplateResponse("leads.html", {
            "request": request,
            "leads": leads,
            "analytics": lead_analytics
        })
        
    except Exception as e:
        logger.error(f"Error in leads_view: {e}", exc_info=True)
        handle_dashboard_error(e, "leads view")

@router.get("/messages", response_class=HTMLResponse)
async def messages_view(request: Request, db: Session = Depends(get_session)):
    """Messages management page"""
    try:
        # Get conversations with user info
        conversations = db.query(Conversation).join(User).filter(
            Conversation.is_active == True
        ).order_by(desc(Conversation.last_activity)).limit(50).all()
        
        return templates.TemplateResponse("messages.html", {
            "request": request,
            "conversations": conversations
        })
        
    except Exception as e:
        handle_dashboard_error(e, "messages view")

@router.get("/users", response_class=HTMLResponse)
async def users_view(request: Request, db: Session = Depends(get_session)):
    """Users management page"""
    try:
        # Get all users with message counts
        users = get_users_by_last_message(db, 100)
        
        return templates.TemplateResponse("users.html", {
            "request": request,
            "users": users
        })
        
    except Exception as e:
        handle_dashboard_error(e, "users view")

@router.get("/settings", response_class=HTMLResponse)
async def settings_view(request: Request):
    """Settings page"""
    try:
        settings_info = {
            "fb_app_id": settings.FB_APP_ID,
            "webhook_url": settings.MESSENGER_WEBHOOK_URL,
            "verify_token": settings.FB_VERIFY_TOKEN,
            "whatsapp_access_token": settings.WHATSAPP_ACCESS_TOKEN,
            "whatsapp_phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID,
            "whatsapp_verify_token": settings.WHATSAPP_VERIFY_TOKEN,
            "messenger_webhook_url": settings.MESSENGER_WEBHOOK_URL,
            "whatsapp_webhook_url": settings.WHATSAPP_WEBHOOK_URL
        }
        
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "settings": settings_info
        })
        
    except Exception as e:
        handle_dashboard_error(e, "settings view")
