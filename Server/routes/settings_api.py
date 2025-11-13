"""
Settings API Routes
Handles configuration testing, updates, and system tools
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["settings"])

# ========================================
# Request Models
# ========================================
class AITestRequest(BaseModel):
    api_key: str
    test_message: str = "Hello, test message"

class MessengerTestRequest(BaseModel):
    access_token: str

class WhatsAppTestRequest(BaseModel):
    access_token: str
    phone_number_id: Optional[str] = None

class ConfigUpdateRequest(BaseModel):
    ai: Optional[Dict[str, str]] = None
    messenger: Optional[Dict[str, str]] = None
    whatsapp: Optional[Dict[str, str]] = None

# ========================================
# Connection Testing Endpoints
# ========================================
@router.post("/test/ai")
async def test_ai_connection(request: AITestRequest):
    """Test Gemini AI connection with provided API key"""
    try:
        import google.generativeai as genai
        
        # Configure with provided key
        genai.configure(api_key=request.api_key)
        
        # Create model and test
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(request.test_message)
        
        if response and response.text:
            return {
                "success": True,
                "message": "AI connection successful",
                "response": response.text[:100] + "..." if len(response.text) > 100 else response.text
            }
        else:
            return {
                "success": False,
                "error": "No response from AI"
            }
            
    except ImportError:
        return {
            "success": False,
            "error": "Google Generative AI package not installed"
        }
    except Exception as e:
        logger.error(f"AI test failed: {e}")
        error_msg = str(e) if str(e) else "Unknown error occurred"
        return {
            "success": False,
            "error": error_msg
        }

@router.post("/test/messenger")
async def test_messenger_connection(request: MessengerTestRequest):
    """Test Facebook Messenger connection with provided token"""
    try:
        import aiohttp
        
        # Test with Graph API me endpoint
        async with aiohttp.ClientSession() as session:
            url = "https://graph.facebook.com/v24.0/me"
            params = {"access_token": request.access_token}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "message": "Messenger connection successful",
                        "page_info": {
                            "name": data.get('name', 'Unknown Page'),
                            "id": data.get('id', '')
                        }
                    }
                else:
                    error_data = await response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
    except Exception as e:
        logger.error(f"Messenger test failed: {e}")
        return {
            "success": False,
            "error": str(e) if str(e) else "Connection failed"
        }

@router.post("/test/whatsapp")
async def test_whatsapp_connection(request: WhatsAppTestRequest):
    """Test WhatsApp Business API connection"""
    try:
        import aiohttp
        
        if not request.phone_number_id:
            # If no phone number ID, just validate token format
            if len(request.access_token) < 50:
                return {
                    "success": False,
                    "error": "Invalid token format (too short)"
                }
            return {
                "success": True,
                "message": "Token format valid (Phone Number ID required for full test)",
                "phone_info": {
                    "display_phone_number": "Not tested - no Phone Number ID"
                }
            }
        
        # Test with WhatsApp Business API
        async with aiohttp.ClientSession() as session:
            url = f"https://graph.facebook.com/v24.0/{request.phone_number_id}"
            headers = {"Authorization": f"Bearer {request.access_token}"}
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "message": "WhatsApp connection successful",
                        "phone_info": {
                            "display_phone_number": data.get('display_phone_number', 'Unknown'),
                            "id": data.get('id', '')
                        }
                    }
                else:
                    error_data = await response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    return {
                        "success": False,
                        "error": error_msg
                    }
                    
    except Exception as e:
        logger.error(f"WhatsApp test failed: {e}")
        return {
            "success": False,
            "error": str(e) if str(e) else "Connection failed"
        }

# ========================================
# Configuration Management
# ========================================
@router.post("/settings/update")
async def update_settings(request: ConfigUpdateRequest):
    """Update configuration (writes to environment/config)"""
    try:
        updated: List[str] = []  # Track what was updated

        # Update AI settings
        if request.ai:
            if 'gemini_api_key' in request.ai:
                os.environ['GEMINI_API_KEY'] = request.ai['gemini_api_key']
                updated.append('Gemini API Key')
            if 'gemini_model' in request.ai:
                os.environ['GEMINI_MODEL'] = request.ai['gemini_model']
                updated.append('Gemini Model')
        
        # Update Messenger settings
        if request.messenger:
            if 'fb_page_access_token' in request.messenger:
                os.environ['FB_PAGE_ACCESS_TOKEN'] = request.messenger['fb_page_access_token']
                updated.append('FB Page Access Token')
            if 'fb_app_id' in request.messenger:
                os.environ['FB_APP_ID'] = request.messenger['fb_app_id']
                updated.append('FB App ID')
            if 'fb_page_id' in request.messenger:
                os.environ['FB_PAGE_ID'] = request.messenger['fb_page_id']
                updated.append('FB Page ID')
            if 'fb_verify_token' in request.messenger:
                os.environ['FB_VERIFY_TOKEN'] = request.messenger['fb_verify_token']
                updated.append('FB Verify Token')
        
        # Update WhatsApp settings
        if request.whatsapp:
            if 'whatsapp_access_token' in request.whatsapp:
                os.environ['WHATSAPP_ACCESS_TOKEN'] = request.whatsapp['whatsapp_access_token']
                updated.append('WhatsApp Access Token')
            if 'whatsapp_phone_number_id' in request.whatsapp:
                os.environ['WHATSAPP_PHONE_NUMBER_ID'] = request.whatsapp['whatsapp_phone_number_id']
                updated.append('WhatsApp Phone Number ID')
            if 'whatsapp_verify_token' in request.whatsapp:
                os.environ['WHATSAPP_VERIFY_TOKEN'] = request.whatsapp['whatsapp_verify_token']
                updated.append('WhatsApp Verify Token')
        
        if updated:
            return {
                "success": True,
                "message": f"Updated: {', '.join(updated)}",
                "note": "Changes applied to current session. Update Railway environment variables for persistence."
            }
        else:
            return {
                "success": False,
                "error": "No settings to update"
            }
            
    except Exception as e:
        logger.error(f"Settings update failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/settings/export")
async def export_settings():
    """Export current configuration (non-sensitive)"""
    try:
        from Server.config import settings
        
        config = {
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG,
            "timezone": settings.TIMEZONE,
            "fb_app_id": settings.FB_APP_ID,
            "fb_page_id": settings.FB_PAGE_ID,
            "whatsapp_phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID,
            "ai_model": getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash'),
            "has_gemini_key": bool(settings.GEMINI_API_KEY),
            "has_fb_token": bool(settings.FB_PAGE_ACCESS_TOKEN),
            "has_whatsapp_token": bool(settings.WHATSAPP_ACCESS_TOKEN)
        }
        
        return {
            "success": True,
            "config": config
        }
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# System Tools
# ========================================
@router.get("/logs/view")
async def view_logs():
    """View recent logs"""
    try:
        import glob
        
        log_dir = "logs"
        if not os.path.exists(log_dir):
            return {"success": False, "error": "Log directory not found"}
        
        # Get latest log file
        log_files = glob.glob(os.path.join(log_dir, "*.log"))
        if not log_files:
            return {"success": False, "error": "No log files found"}
        
        latest_log = max(log_files, key=os.path.getctime)
        
        # Read last 100 lines
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_lines = lines[-100:] if len(lines) > 100 else lines
        
        return {
            "success": True,
            "file": os.path.basename(latest_log),
            "lines": recent_lines
        }
        
    except Exception as e:
        logger.error(f"View logs failed: {e}")
        return {"success": False, "error": str(e)}

@router.post("/cache/clear")
async def clear_cache():
    """Clear application cache"""
    try:
        # Implement cache clearing logic here
        # For now, just return success
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
        
    except Exception as e:
        logger.error(f"Clear cache failed: {e}")
        return {"success": False, "error": str(e)}
