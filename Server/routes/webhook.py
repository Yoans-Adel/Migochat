from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
import logging

from app.database import get_session
from Server.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services directly to avoid circular imports
from app.services.messaging.message_handler import MessageHandler
from app.services.business.facebook_lead_center_service import FacebookLeadCenterService

message_handler = MessageHandler()
facebook_lead_center = FacebookLeadCenterService()

# Helper function for consistent error handling
def handle_webhook_error(error: Exception, action: str):
    """Handle webhook errors consistently with security logging"""
    logger.error(f"Error {action}: {error}")
    # Log security-relevant information
    if "verification" in action.lower():
        logger.warning(f"Security: Webhook verification failed - {action}")
    raise HTTPException(status_code=500, detail="Internal server error")

# Facebook Messenger Integration Endpoints
@router.get("/messenger")
async def messenger_webhook_get(request: Request):
    """Facebook Messenger webhook verification"""
    try:
        # Get query parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        logger.info(f"Messenger webhook verification attempt: mode={mode}, token={token}")
        
        # Verify the webhook
        if mode == "subscribe" and token == settings.FB_VERIFY_TOKEN:
            logger.info("Messenger webhook verified successfully")
            return Response(content=challenge, media_type="text/plain")
        else:
            logger.error(f"Messenger webhook verification failed: mode={mode}, token={token}, expected={settings.FB_VERIFY_TOKEN}")
            raise HTTPException(status_code=403, detail="Forbidden")
            
    except HTTPException:
        raise
    except Exception as e:
        handle_webhook_error(e, "verifying Messenger webhook")

@router.post("/messenger")
async def messenger_webhook_post(request: Request, db: Session = Depends(get_session)):
    """Facebook Messenger webhook for receiving messages"""
    try:
        # Get webhook data
        webhook_data = await request.json()
        logger.info(f"Messenger webhook received: {webhook_data}")
        
        # Parse Facebook webhook format
        if webhook_data.get("object") == "page":
            for entry in webhook_data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    # Extract message details
                    sender_id = messaging_event.get("sender", {}).get("id")
                    message = messaging_event.get("message", {})
                    message_text = message.get("text", "")
                    message_id = message.get("mid")
                    
                    if sender_id and message_text:
                        # Create properly formatted message data
                        message_data = {
                            "user_id": sender_id,
                            "text": message_text,
                            "message_id": message_id
                        }
                        
                        # Process the message
                        result = await message_handler._process_message_impl(message_data, platform="facebook")
                        logger.info(f"Message processing result: {result}")
        
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        handle_webhook_error(e, "processing Messenger webhook")

# WhatsApp Integration Endpoints
@router.get("/whatsapp")
async def whatsapp_webhook_get(request: Request):
    """WhatsApp webhook verification"""
    try:
        verify_token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        from app.services.messaging.whatsapp_service import WhatsAppService
        whatsapp_service = WhatsAppService()
        
        if whatsapp_service.verify_webhook(verify_token, challenge):
            return Response(content=challenge, media_type="text/plain")
        else:
            raise HTTPException(status_code=403, detail="Forbidden")
            
    except HTTPException:
        raise
    except Exception as e:
        handle_webhook_error(e, "verifying WhatsApp webhook")

@router.post("/whatsapp")
async def whatsapp_webhook_post(request: Request):
    """WhatsApp webhook for receiving messages"""
    try:
        webhook_data = await request.json()
        logger.info(f"WhatsApp webhook received: {webhook_data}")
        
        # Process with message handler - call async method directly
        result = await message_handler._process_message_impl(webhook_data, platform="whatsapp")
        logger.info(f"WhatsApp message processing result: {result}")
        
        return {"status": "ok"}
        
    except Exception as e:
        handle_webhook_error(e, "processing WhatsApp webhook")

# Telegram Integration Endpoints (for future use)
@router.get("/telegram")
async def telegram_webhook_get(request: Request):
    """Telegram webhook verification"""
    try:
        # Future Telegram integration
        return {"status": "not_implemented"}
    except Exception as e:
        handle_webhook_error(e, "verifying Telegram webhook")

@router.post("/telegram")
async def telegram_webhook_post(request: Request):
    """Telegram webhook for receiving messages"""
    try:
        # Future Telegram integration
        return {"status": "not_implemented"}
    except Exception as e:
        handle_webhook_error(e, "processing Telegram webhook")

# Instagram Integration Endpoints (for future use)
@router.get("/instagram")
async def instagram_webhook_get(request: Request):
    """Instagram webhook verification"""
    try:
        # Future Instagram integration
        return {"status": "not_implemented"}
    except Exception as e:
        handle_webhook_error(e, "verifying Instagram webhook")

@router.post("/instagram")
async def instagram_webhook_post(request: Request):
    """Instagram webhook for receiving messages"""
    try:
        # Future Instagram integration
        return {"status": "not_implemented"}
    except Exception as e:
        handle_webhook_error(e, "processing Instagram webhook")

# Facebook Lead Center Integration Endpoints
@router.get("/leadgen")
async def leadgen_webhook_get(request: Request):
    """Facebook Lead Center webhook verification"""
    try:
        # Get query parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        logger.info(f"Leadgen webhook verification attempt: mode={mode}, token={token}")
        
        # Verify the webhook
        if mode == "subscribe" and token == settings.FB_LEADCENTER_VERIFY_TOKEN:
            logger.info("Leadgen webhook verified successfully")
            return Response(content=challenge, media_type="text/plain")
        else:
            logger.error("Leadgen webhook verification failed")
            raise HTTPException(status_code=403, detail="Forbidden")
            
    except HTTPException:
        raise
    except Exception as e:
        handle_webhook_error(e, "verifying Leadgen webhook")

@router.post("/leadgen")
async def leadgen_webhook_post(request: Request):
    """Facebook Lead Center webhook for receiving lead data"""
    try:
        webhook_data = await request.json()
        logger.info(f"Received leadgen webhook: {webhook_data}")
        
        # Process the leadgen webhook
        results = facebook_lead_center.process_leadgen_webhook(webhook_data)
        
        logger.info(f"Leadgen webhook processed: {results}")
        return {"status": "ok", "results": results}
        
    except Exception as e:
        handle_webhook_error(e, "processing Leadgen webhook")
