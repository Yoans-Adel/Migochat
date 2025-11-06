from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import logging
import traceback

from database import get_session, User, Message, Conversation, MessageDirection, MessageStatus, LeadStage, CustomerLabel, CustomerType, LeadActivity, MessageSource, PostType, Post, AdCampaign, enum_to_value
from Server.config import settings
from Server.routes.service_helpers import (
    get_messenger_service,
    get_whatsapp_service,
    get_message_handler,
    get_facebook_lead_center_service,
    get_message_source_tracker,
    get_ai_service,
    get_gemini_service,
    get_settings_manager as get_settings_manager_helper
)

logger = logging.getLogger(__name__)

# Import BWW Store Integration (optional)
bww_store_available = False
BWWStoreAPIService = None

try:
    from bww_store import BWWStoreAPIService
    bww_store_available = True
    logger.info("BWW Store integration loaded successfully")
except ImportError:
    logger.warning("BWW Store integration not available")

router = APIRouter()

# Initialize BWW Store Integration (if available)
if bww_store_available and BWWStoreAPIService:
    bww_store_integration = BWWStoreAPIService(language="ar")
else:
    bww_store_integration = None


@router.get("/messages")
async def get_messages(
    skip: int = 0,
    limit: int = 50,
    user_id: Optional[int] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get messages with pagination and source filtering"""
    try:
        query = db.query(Message)

        if user_id:
            query = query.filter(Message.user_id == user_id)

        if source:
            query = query.filter(Message.message_source == MessageSource(source))

        messages = query.order_by(desc(Message.timestamp)).offset(skip).limit(limit).all()

        return {
            "messages": [
                {
                    "id": msg.id,
                    "user_id": msg.user_id,
                    "sender_id": msg.sender_id,
                    "message_text": msg.message_text,
                    "direction": msg.direction.value,
                    "status": msg.status.value,
                    "timestamp": msg.timestamp.isoformat(),
                    "message_type": msg.message_type,
                    "message_source": enum_to_value(msg.message_source),
                    "post_id": msg.post_id,
                    "post_type": enum_to_value(msg.post_type),
                    "ad_id": msg.ad_id,
                    "comment_id": msg.comment_id
                }
                for msg in messages
            ],
            "total": query.count()
        }

    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/messages/send")
async def send_message(
    request: Request,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Send message to user"""
    try:
        # Get message handler service
        message_handler = get_message_handler()
        if not message_handler:
            raise HTTPException(status_code=503, detail="Message handler service unavailable")

        # Get data from request body
        data = await request.json()
        recipient_id = data.get("recipient_id")
        message_text = data.get("message_text")
        platform = data.get("platform", "facebook")  # facebook or whatsapp

        if not recipient_id or not message_text:
            raise HTTPException(status_code=400, detail="recipient_id and message_text are required")

        # Send message via appropriate service
        success = message_handler.send_message(recipient_id, message_text, platform)

        if success:
            return {
                "success": True,
                "message": "Message sent successfully",
                "recipient_id": recipient_id,
                "platform": platform
            }
        else:
            return {
                "success": False,
                "error": "Failed to send message",
                "details": "Check server logs for details"
            }

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        traceback.print_exc()

        # Check if it's a Facebook API error
        if "400 Client Error" in str(e) and "graph.facebook.com" in str(e):
            return {
                "success": False,
                "error": "Facebook API Error: Cannot send message to test user ID. Use real Facebook user ID for testing.",
                "details": "Facebook API requires valid user IDs that have interacted with your page."
            }
        elif "401" in str(e):
            return {
                "success": False,
                "error": "Authentication Error: Invalid access token",
                "details": "Please check your Facebook Page Access Token"
            }
        else:
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/bulk")
async def send_bulk_message(
    request: Request,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Send bulk message to multiple users"""
    try:
        # Get message handler service
        message_handler = get_message_handler()
        if not message_handler:
            raise HTTPException(status_code=503, detail="Message handler service unavailable")

        # Get data from request body
        data = await request.json()
        campaign_name = data.get("campaign_name", "")
        audience = data.get("audience", "all")
        message_text = data.get("message", "")
        scheduled = data.get("scheduled", False)
        scheduled_time = data.get("scheduled_time")

        if not message_text:
            raise HTTPException(status_code=400, detail="message is required")

        # Get target users based on audience filter
        query = db.query(User).filter(User.is_active.is_(True))
        
        if audience == "leads":
            # Only users with lead stages
            from database import LeadStage
            query = query.filter(User.lead_stage.isnot(None))
        elif audience == "active":
            # Users with messages in last 7 days
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            query = query.filter(User.last_message_at >= seven_days_ago)
        elif audience == "new":
            # New leads in last 7 days
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            query = query.filter(User.created_at >= seven_days_ago)
        elif audience == "qualified":
            from database import LeadStage
            query = query.filter(User.lead_stage == LeadStage.QUALIFIED)

        users = query.all()
        
        if len(users) == 0:
            return {
                "success": False,
                "error": "No users found matching criteria",
                "sent_count": 0
            }

        # Send messages
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                # Personalize message
                personalized_message = message_text.replace("{name}", f"{user.first_name or ''} {user.last_name or ''}".strip())
                personalized_message = personalized_message.replace("{first_name}", user.first_name or "")
                personalized_message = personalized_message.replace("{last_name}", user.last_name or "")
                
                # Determine platform
                platform = "facebook"  # Default to facebook
                
                # Send message
                success = message_handler.send_message(user.psid, personalized_message, platform)
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Error sending bulk message to {user.psid}: {e}")
                failed_count += 1

        logger.info(f"Bulk message campaign '{campaign_name}': Sent {sent_count}/{len(users)}, Failed {failed_count}")

        return {
            "success": True,
            "campaign_name": campaign_name,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total_users": len(users)
        }

    except Exception as e:
        logger.error(f"Error sending bulk message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get users list"""
    try:
        users = db.query(User).order_by(desc(User.last_message_at)).offset(skip).limit(limit).all()

        return {
            "users": [
                {
                    "id": user.id,
                    "psid": user.psid,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profile_pic": user.profile_pic,
                    "governorate": enum_to_value(user.governorate),
                    "created_at": user.created_at.isoformat(),
                    "last_message_at": user.last_message_at.isoformat() if user.last_message_at is not None else None,
                    "is_active": user.is_active,
                    "lead_stage": enum_to_value(user.lead_stage),
                    "customer_type": enum_to_value(user.customer_type),
                    "customer_label": enum_to_value(user.customer_label),
                    "lead_score": user.lead_score
                }
                for user in users
            ],
            "total": db.query(User).count()
        }

    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users/{psid}")
async def get_user_profile(psid: str, db: Session = Depends(get_session)) -> Dict[str, Any]:
    """Get user profile and message history"""
    try:
        user = db.query(User).filter(User.psid == psid).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's messages
        messages = db.query(Message).filter(Message.user_id == user.id).order_by(desc(Message.timestamp)).limit(50).all()

        # Get lead activities
        activities = db.query(LeadActivity).filter(LeadActivity.user_id == user.id).order_by(desc(LeadActivity.timestamp)).limit(20).all()

        return {
            "user": {
                "id": user.id,
                "psid": user.psid,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_pic": user.profile_pic,
                "governorate": enum_to_value(user.governorate),
                "created_at": user.created_at.isoformat(),
                "last_message_at": user.last_message_at.isoformat() if user.last_message_at is not None else None,
                "is_active": user.is_active,
                "lead_stage": enum_to_value(user.lead_stage),
                "customer_type": enum_to_value(user.customer_type),
                "customer_label": enum_to_value(user.customer_label),
                "lead_score": user.lead_score,
                "last_stage_change": user.last_stage_change.isoformat() if user.last_stage_change is not None else None
            },
            "messages": [
                {
                    "id": msg.id,
                    "message_text": msg.message_text,
                    "direction": msg.direction.value,
                    "status": msg.status.value,
                    "timestamp": msg.timestamp.isoformat(),
                    "message_type": msg.message_type,
                    "message_source": enum_to_value(msg.message_source),
                    "post_id": msg.post_id,
                    "post_type": enum_to_value(msg.post_type),
                    "ad_id": msg.ad_id,
                    "comment_id": msg.comment_id
                }
                for msg in messages
            ],
            "activities": [
                {
                    "id": activity.id,
                    "activity_type": activity.activity_type,
                    "old_value": activity.old_value,
                    "new_value": activity.new_value,
                    "reason": activity.reason,
                    "timestamp": activity.timestamp.isoformat(),
                    "automated": activity.automated
                }
                for activity in activities
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/users/{psid}")
async def update_user(
    psid: str,
    request: Request,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Update user information"""
    try:
        # Get JSON body
        update_data = await request.json()

        user = db.query(User).filter(User.psid == psid).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Track changes for lead activity
        changes: List[tuple[str, Optional[str], str]] = []

        if "first_name" in update_data:
            user.first_name = update_data["first_name"]
        if "last_name" in update_data:
            user.last_name = update_data["last_name"]
        if "governorate" in update_data:
            from database import Governorate
            try:
                old_value = enum_to_value(user.governorate)
                setattr(user, 'governorate', Governorate(update_data["governorate"]))
                if old_value != update_data["governorate"]:
                    changes.append(("governorate", old_value, update_data["governorate"]))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid governorate")

        if "lead_stage" in update_data:
            try:
                old_value = enum_to_value(user.lead_stage)
                setattr(user, 'lead_stage', LeadStage(update_data["lead_stage"]))
                setattr(user, 'last_stage_change', datetime.now(timezone.utc))
                if old_value != update_data["lead_stage"]:
                    changes.append(("lead_stage", old_value, update_data["lead_stage"]))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid lead stage")

        if "customer_type" in update_data:
            try:
                old_value = enum_to_value(user.customer_type)
                setattr(user, 'customer_type', CustomerType(update_data["customer_type"]))
                if old_value != update_data["customer_type"]:
                    changes.append(("customer_type", old_value, update_data["customer_type"]))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid customer type")

        if "customer_label" in update_data:
            try:
                old_value = enum_to_value(user.customer_label)
                setattr(user, 'customer_label', CustomerLabel(update_data["customer_label"]))
                if old_value != update_data["customer_label"]:
                    changes.append(("customer_label", old_value, update_data["customer_label"]))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid customer label")

        db.commit()

        # Log changes to lead activities
        for activity_type, old_val, new_val in changes:
            activity = LeadActivity(
                user_id=user.id,
                activity_type=f"{activity_type}_change",
                old_value=old_val,
                new_value=new_val,
                reason="Manual update from dashboard",
                automated=False,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(activity)

        if changes:
            db.commit()

        logger.info(f"Updated user {psid}: {changes}")

        return {"success": True, "message": "User updated successfully", "changes": len(changes)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats")
async def get_stats(db: Session = Depends(get_session)) -> Dict[str, Any]:
    """Get dashboard statistics with message source analytics"""
    try:
        # Basic counts
        total_users = db.query(User).count()
        total_messages = db.query(Message).count()
        active_conversations = db.query(Conversation).filter(Conversation.is_active.is_(True)).count()

        # Messages by direction
        inbound_messages = db.query(Message).filter(Message.direction == MessageDirection.INBOUND).count()
        outbound_messages = db.query(Message).filter(Message.direction == MessageDirection.OUTBOUND).count()

        # Recent activity (last 24 hours)
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        recent_messages = db.query(Message).filter(Message.timestamp >= yesterday).count()
        recent_users = db.query(User).filter(User.last_message_at >= yesterday).count()

        # Messages by status
        sent_messages = db.query(Message).filter(Message.status == MessageStatus.SENT).count()
        delivered_messages = db.query(Message).filter(Message.status == MessageStatus.DELIVERED).count()
        read_messages = db.query(Message).filter(Message.status == MessageStatus.READ).count()

        # Lead analytics
        lead_automation = get_facebook_lead_center_service()
        lead_analytics = lead_automation.get_lead_analytics() if lead_automation else {}

        # Message source analytics
        source_tracker = get_message_source_tracker()
        source_analytics = source_tracker.get_message_source_analytics() if source_tracker else {}

        return {
            "total_users": total_users,
            "total_messages": total_messages,
            "active_conversations": active_conversations,
            "inbound_messages": inbound_messages,
            "outbound_messages": outbound_messages,
            "recent_messages_24h": recent_messages,
            "recent_users_24h": recent_users,
            "sent_messages": sent_messages,
            "delivered_messages": delivered_messages,
            "read_messages": read_messages,
            "lead_analytics": lead_analytics,
            "source_analytics": source_analytics
        }

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/conversations")
async def get_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get active conversations"""
    try:
        conversations = db.query(Conversation).join(User).filter(
            Conversation.is_active.is_(True)
        ).order_by(desc(Conversation.last_activity)).offset(skip).limit(limit).all()

        return {
            "conversations": [
                {
                    "id": conv.id,
                    "user_id": conv.user_id,
                    "user_name": f"{conv.user.first_name or ''} {conv.user.last_name or ''}".strip(),
                    "user_psid": conv.user.psid,
                    "started_at": conv.started_at.isoformat(),
                    "last_activity": conv.last_activity.isoformat(),
                    "message_count": conv.message_count,
                    "is_active": conv.is_active,
                    "lead_stage": conv.user.lead_stage.value if conv.user.lead_stage else None,
                    "customer_type": conv.user.customer_type.value if conv.user.customer_type else None,
                    "lead_score": conv.user.lead_score
                }
                for conv in conversations
            ],
            "total": db.query(Conversation).filter(Conversation.is_active.is_(True)).count()
        }

    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/leads")
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    stage: Optional[str] = None,
    customer_type: Optional[str] = None,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get leads with filtering"""
    try:
        query = db.query(User)

        if stage:
            query = query.filter(User.lead_stage == LeadStage(stage))

        if customer_type:
            query = query.filter(User.customer_type == CustomerType(customer_type))

        leads = query.order_by(desc(User.lead_score)).offset(skip).limit(limit).all()

        return {
            "leads": [
                {
                    "id": user.id,
                    "psid": user.psid,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profile_pic": user.profile_pic,
                    "governorate": enum_to_value(user.governorate),
                    "created_at": user.created_at.isoformat(),
                    "last_message_at": user.last_message_at.isoformat() if user.last_message_at is not None else None,
                    "is_active": user.is_active,
                    "lead_stage": enum_to_value(user.lead_stage),
                    "customer_type": enum_to_value(user.customer_type),
                    "customer_label": enum_to_value(user.customer_label),
                    "lead_score": user.lead_score,
                    "last_stage_change": user.last_stage_change.isoformat() if user.last_stage_change is not None else None
                }
                for user in leads
            ],
            "total": query.count()
        }

    except Exception as e:
        logger.error(f"Error getting leads: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/posts")
async def create_post(
    post_data: Dict[str, Any],
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Create a new post record"""
    try:
        # Get source tracker service
        source_tracker = get_message_source_tracker()
        if not source_tracker:
            raise HTTPException(status_code=503, detail="Message source tracker service unavailable")

        facebook_post_id = str(post_data.get("facebook_post_id", ""))
        post_type = str(post_data.get("post_type", ""))
        content = str(post_data.get("content", ""))
        price = post_data.get("price")
        data = post_data.get("data")

        post = source_tracker.create_post(
            facebook_post_id=facebook_post_id,
            post_type=PostType(post_type),
            content=content,
            price=str(price) if price else None,
            data=data if data else None
        )

        if post:
            return {
                "success": True,
                "post": {
                    "id": post.id,
                    "facebook_post_id": post.facebook_post_id,
                    "post_type": post.post_type.value,
                    "post_content": post.post_content,
                    "post_price": post.post_price,
                    "created_at": post.created_at.isoformat()
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create post")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid post type: {e}")
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/ad-campaigns")
async def create_ad_campaign(
    ad_data: Dict[str, Any],
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Create a new ad campaign record"""
    try:
        # Get source tracker service
        source_tracker = get_message_source_tracker()
        if not source_tracker:
            raise HTTPException(status_code=503, detail="Message source tracker service unavailable")

        facebook_ad_id = str(ad_data.get("facebook_ad_id", ""))
        campaign_name = str(ad_data.get("campaign_name", ""))
        content = str(ad_data.get("content", ""))
        target_audience = ad_data.get("target_audience")
        budget = ad_data.get("budget")

        ad = source_tracker.create_ad_campaign(
            facebook_ad_id=facebook_ad_id,
            campaign_name=campaign_name,
            content=content,
            target_audience=target_audience if target_audience else None,
            budget=str(budget) if budget else None
        )

        if ad:
            return {
                "success": True,
                "ad_campaign": {
                    "id": ad.id,
                    "facebook_ad_id": ad.facebook_ad_id,
                    "campaign_name": ad.campaign_name,
                    "ad_content": ad.ad_content,
                    "budget": ad.budget,
                    "status": ad.status,
                    "created_at": ad.created_at.isoformat()
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create ad campaign")

    except Exception as e:
        logger.error(f"Error creating ad campaign: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/posts")
async def get_posts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get posts list"""
    try:
        posts = db.query(Post).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()

        return {
            "posts": [
                {
                    "id": post.id,
                    "facebook_post_id": post.facebook_post_id,
                    "post_type": enum_to_value(post.post_type),
                    "post_content": post.post_content,
                    "post_price": post.post_price,
                    "post_data": post.post_data,
                    "created_at": post.created_at.isoformat(),
                    "is_active": post.is_active
                }
                for post in posts
            ],
            "total": db.query(Post).count()
        }

    except Exception as e:
        logger.error(f"Error getting posts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/ad-campaigns")
async def get_ad_campaigns(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Get ad campaigns list"""
    try:
        campaigns = db.query(AdCampaign).order_by(desc(AdCampaign.created_at)).offset(skip).limit(limit).all()

        return {
            "ad_campaigns": [
                {
                    "id": campaign.id,
                    "facebook_ad_id": campaign.facebook_ad_id,
                    "campaign_name": campaign.campaign_name,
                    "ad_content": campaign.ad_content,
                    "target_audience": campaign.target_audience,
                    "budget": campaign.budget,
                    "status": campaign.status,
                    "created_at": campaign.created_at.isoformat()
                }
                for campaign in campaigns
            ],
            "total": db.query(AdCampaign).count()
        }

    except Exception as e:
        logger.error(f"Error getting ad campaigns: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/ai/respond")
async def trigger_ai_response(
    request: Request,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Trigger AI response for a user with multimodal support

    Body:
        {
            "user_psid": "string",
            "message_text": "string",
            "media_files": [  // Optional
                {
                    "type": "image|audio",
                    "data": "base64_encoded_data",
                    "mime_type": "image/jpeg"
                }
            ],
            "use_quality_model": false  // Optional, default false
        }
    """
    try:
        # Parse request body
        data = await request.json()
        user_psid = data.get("user_psid")
        message_text = data.get("message_text")
        media_files = data.get("media_files", [])

        # Validate inputs
        if not user_psid:
            raise HTTPException(status_code=400, detail="user_psid is required")

        if not message_text:
            raise HTTPException(status_code=400, detail="message_text is required")

        logger.info(f"AI Response request for user: {user_psid}, message: {message_text}, media: {len(media_files)}")

        # Query user from database
        user = db.query(User).filter(User.psid == user_psid).first()

        if not user:
            logger.warning(f"User not found: {user_psid}")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"User found: {user.first_name} {user.last_name}")

        # Generate AI response
        logger.info("Initializing AI service...")
        ai_service = get_ai_service()
        if not ai_service:
            raise HTTPException(status_code=503, detail="AI service unavailable")

        logger.info("Generating AI response...")
        ai_response = ai_service.generate_response(message_text, user)
        logger.info(f"AI response generated: {ai_response is not None}")

        if ai_response:
            logger.info("Sending message to user...")
            # Send response to user (only if Facebook credentials are configured)
            if settings.FB_PAGE_ACCESS_TOKEN and settings.FB_PAGE_ACCESS_TOKEN != "":
                try:
                    # Get message handler
                    message_handler = get_message_handler()
                    if not message_handler:
                        logger.warning("Message handler unavailable")
                    else:
                        # Use correct method name: send_message instead of send_message_to_user
                        success = message_handler.send_message(user_psid, ai_response, platform="facebook")
                        logger.info(f"Message sent successfully: {success}")
                        response = {"message_id": "sent" if success else "failed"}
                except Exception as send_error:
                    logger.warning(f"Failed to send message via Facebook API: {send_error}")
                    # Continue without sending - just return the response
                    response = {"message_id": "local_response"}
            else:
                logger.info("Facebook credentials not configured - returning response only")
                response = {"message_id": "local_response"}

            return {
                "success": True,
                "response": ai_response,
                "message_id": response.get("message_id"),
                "note": "Facebook API not configured - response generated locally" if not settings.FB_PAGE_ACCESS_TOKEN else None
            }
        else:
            logger.warning("No AI response generated")
            return {
                "success": False,
                "message": "No AI response generated"
            }

    except HTTPException as he:
        logger.error(f"HTTP Exception in AI response: {he}")
        raise he
    except Exception as e:
        logger.error(f"Error triggering AI response: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/ai/status")
async def ai_status() -> Dict[str, Any]:
    """Get AI service status"""
    try:
        ai_service = get_ai_service()
        if not ai_service:
            return {
                "status": "unavailable",
                "message": "AI service not initialized"
            }

        status = ai_service.get_service_status()

        return {
            "status": "success",
            "ai_services": status
        }

    except Exception as e:
        logger.error(f"Error getting AI status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# BWW Store Enhanced Endpoints


@router.post("/bww-store/query")
async def bww_store_query(
    query: str,
    language: str = "ar",
    limit: int = 3
) -> Dict[str, Any]:
    """Enhanced BWW Store customer query handling"""
    try:
        if not bww_store_available or not bww_store_integration:
            raise HTTPException(status_code=503, detail="BWW Store integration not available")

        # Use search_and_format_products instead of handle_customer_query
        result = await bww_store_integration.search_and_format_products(
            search_text=query,
            limit=limit,
            language=language
        )

        return {
            "success": True,
            "query": query,
            "products": result,
            "count": len(result)
        }

    except Exception as e:
        logger.error(f"Error handling BWW Store query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bww-store/compare")
async def bww_store_compare(
    product_ids: List[str],
    language: str = "ar"
) -> Dict[str, Any]:
    """Compare BWW Store products"""
    try:
        if not bww_store_available or not bww_store_integration:
            raise HTTPException(status_code=503, detail="BWW Store integration not available")

        if len(product_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 products required for comparison")

        if len(product_ids) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 products can be compared")

        # Convert string IDs to integers
        try:
            product_ids_int = [int(pid) for pid in product_ids]
        except ValueError:
            raise HTTPException(status_code=400, detail="Product IDs must be numeric")

        result = await bww_store_integration.compare_products(
            product_ids=product_ids_int,
            language=language
        )

        return {
            "success": True,
            "comparison": result,
            "product_count": len(product_ids)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bww-store/suggestions")
async def bww_store_suggestions(
    query: str,
    language: str = "ar"
) -> Dict[str, Any]:
    """Get BWW Store search suggestions (simplified version)"""
    try:
        if not bww_store_available or not bww_store_integration:
            raise HTTPException(status_code=503, detail="BWW Store integration not available")

        # Use search to get suggestions
        suggestions = await bww_store_integration.search_and_format_products(
            search_text=query,
            limit=5,
            language=language
        )

        return {
            "success": True,
            "suggestions": suggestions,
            "query": query,
            "language": language
        }

    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bww-store/analytics")
async def bww_store_analytics() -> Dict[str, Any]:
    """Get BWW Store analytics - Basic cache stats"""
    try:
        if not bww_store_available or not bww_store_integration:
            raise HTTPException(status_code=503, detail="BWW Store integration not available")

        # Return basic analytics from cache
        return {
            "success": True,
            "analytics": {
                "service": "BWW Store API",
                "status": "operational",
                "note": "Full analytics not implemented yet"
            }
        }

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bww-store/status")
async def bww_store_status() -> Dict[str, Any]:
    """Get BWW Store integration status"""
    try:
        if not bww_store_available or not bww_store_integration:
            return {
                "success": False,
                "status": "BWW Store integration not available",
                "available": False
            }

        status = bww_store_integration.get_service_status()

        return {
            "success": True,
            "status": status,
            "available": True
        }

    except Exception as e:
        logger.error(f"Error getting BWW Store status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Facebook Lead Center Integration Endpoints


@router.post("/leads/sync-to-facebook")
async def sync_leads_to_facebook() -> Dict[str, Any]:
    """Sync all leads to Facebook Lead Center"""
    try:
        results = lead_automation.sync_all_leads_to_facebook()

        return {
            "success": True,
            "message": "Lead sync completed",
            "results": results
        }

    except Exception as e:
        logger.error(f"Error syncing leads to Facebook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/leads/analytics")
async def get_lead_analytics() -> Dict[str, Any]:
    """Get comprehensive lead analytics"""
    try:
        analytics = lead_automation.get_lead_analytics()

        return {
            "success": True,
            "analytics": analytics
        }

    except Exception as e:
        logger.error(f"Error getting lead analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/leads/{psid}/create-in-facebook")
async def create_lead_in_facebook(psid: str, db: Session = Depends(get_session)) -> Dict[str, Any]:
    """Create a specific lead in Facebook Lead Center"""
    try:
        user = db.query(User).filter(User.psid == psid).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        success = lead_automation.create_lead_in_facebook(user)

        return {
            "success": success,
            "message": "Lead creation completed" if success else "Lead creation failed",
            "user_psid": psid
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lead in Facebook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/whatsapp/send-message")
async def send_whatsapp_message(request: Request) -> Dict[str, Any]:
    """Send a message via WhatsApp"""
    try:
        data = await request.json()
        phone_number = data.get("phone_number")
        message = data.get("message")
        message_type = data.get("message_type", "text")

        if not phone_number or not message:
            raise HTTPException(status_code=400, detail="phone_number and message are required")

        whatsapp_service = get_whatsapp_service()
        if not whatsapp_service:
            raise HTTPException(status_code=503, detail="WhatsApp service unavailable")

        if message_type == "text":
            response = whatsapp_service.send_message(phone_number, message)
        elif message_type == "template":
            template_name = data.get("template_name")
            template_params = data.get("template_params", [])
            response = whatsapp_service.send_template_message(phone_number, template_name, template_params)
        elif message_type == "interactive":
            header_text = data.get("header_text", "")
            body_text = data.get("body_text", "")
            footer_text = data.get("footer_text")
            buttons = data.get("buttons", [])
            response = whatsapp_service.send_interactive_message(phone_number, header_text, body_text, footer_text, buttons)
        elif message_type == "list":
            header_text = data.get("header_text", "")
            body_text = data.get("body_text", "")
            button_text = data.get("button_text", "اختر")
            sections = data.get("sections", [])
            response = whatsapp_service.send_list_message(phone_number, header_text, body_text, button_text, sections)
        else:
            raise HTTPException(status_code=400, detail="Invalid message_type")

        return {
            "success": True,
            "response": response
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")

        # Check if it's a WhatsApp API error
        if "401" in str(e) and "graph.facebook.com" in str(e):
            return {
                "success": False,
                "error": "WhatsApp API Authentication Error: Invalid access token",
                "details": "Please check your WhatsApp Business API access token"
            }
        elif "400" in str(e) and "graph.facebook.com" in str(e):
            return {
                "success": False,
                "error": "WhatsApp API Error: Invalid phone number or message format",
                "details": "Please check the phone number format and message content"
            }
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/whatsapp/status")
async def whatsapp_status() -> Dict[str, Any]:
    """Check WhatsApp service status"""
    try:
        whatsapp_service = get_whatsapp_service()
        if not whatsapp_service:
            raise HTTPException(status_code=503, detail="WhatsApp service unavailable")

        # Check if WhatsApp is configured
        is_available = bool(whatsapp_service.access_token and whatsapp_service.phone_number_id)

        return {
            "success": True,
            "whatsapp_available": is_available,
            "phone_number_id": whatsapp_service.phone_number_id if is_available else None,
            "api_url": whatsapp_service.api_url if is_available else None
        }

    except Exception as e:
        logger.error(f"Error checking WhatsApp status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Enhanced Health Check Endpoints


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed system health check"""
    try:
        # Health monitor has been archived - return basic health status
        return {
            "status": "ok",
            "message": "Health monitoring has been archived. Basic health: operational"
        }
    except Exception as e:
        logger.error(f"Error in detailed health check: {e}")
        return {"error": "Health check failed", "status": "error"}


@router.get("/health/alerts")
async def health_alerts() -> Dict[str, Any]:
    """Get system health alerts"""
    try:
        # Health monitor has been archived - return empty alerts
        return {"alerts": [], "count": 0, "message": "Health monitoring has been archived"}
    except Exception as e:
        logger.error(f"Error getting health alerts: {e}")
        return {"error": "Failed to get alerts", "alerts": []}

# AI Service Testing Endpoint


@router.post("/ai/test")
async def test_ai_connection(request: Request) -> Dict[str, Any]:
    """Test AI service connection and response"""
    try:
        # Get test message from request
        data = await request.json()
        test_message = data.get("message", "مرحبا، هذه رسالة تجريبية")

        # Check if Gemini API key is configured
        if not settings.GEMINI_API_KEY or len(settings.GEMINI_API_KEY) == 0:
            return {
                "success": False,
                "error": "AI service not configured",
                "detail": "Gemini API key not found in environment variables",
                "instruction": "Add GEMINI_API_KEY to your environment or update from /dashboard/settings"
            }

        # Try to initialize and test Gemini service
        try:
            gemini_service = get_gemini_service()
            if not gemini_service:
                return {
                    "success": False,
                    "error": "AI service unavailable",
                    "instruction": "Service initialization failed"
                }

            # Test AI response
            response = gemini_service.generate_response(test_message, None)

            return {
                "success": True,
                "model": settings.GEMINI_MODEL or "gemini-2.5-flash",
                "test_message": test_message,
                "ai_response": response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as gemini_error:
            logger.error(f"Gemini service error: {gemini_error}")
            return {
                "success": False,
                "error": "AI service initialization failed",
                "detail": str(gemini_error),
                "instruction": "Check if GEMINI_API_KEY is valid"
            }

    except Exception as e:
        logger.error(f"Error testing AI connection: {e}")
        return {
            "success": False,
            "error": str(e),
            "detail": "Failed to test AI connection"
        }

# AI Model Configuration Endpoints


@router.get("/ai/models")
async def get_available_models() -> Dict[str, Any]:
    """Get list of available AI models"""
    try:
        models = [
            {
                "id": "gemini-2.5-flash",
                "name": "Gemini 2.5 Flash",
                "provider": "Google",
                "description": "Best price-performance ratio (Recommended)",
                "features": ["Multilingual", "Fast", "Cost-effective"],
                "max_tokens": 8192,
                "context_window": "1M tokens"
            },
            {
                "id": "gemini-2.5-pro",
                "name": "Gemini 2.5 Pro",
                "provider": "Google",
                "description": "Most powerful for complex reasoning",
                "features": ["Advanced reasoning", "Multimodal", "High accuracy"],
                "max_tokens": 8192,
                "context_window": "2M tokens"
            },
            {
                "id": "gemini-2.5-flash-lite",
                "name": "Gemini 2.5 Flash-Lite",
                "provider": "Google",
                "description": "Fastest and most cost-efficient",
                "features": ["Ultra fast", "Lowest cost", "High throughput"],
                "max_tokens": 8192,
                "context_window": "1M tokens"
            },
            {
                "id": "gemini-2.0-flash",
                "name": "Gemini 2.0 Flash",
                "provider": "Google",
                "description": "Previous generation (deprecated)",
                "features": ["Stable", "Proven"],
                "max_tokens": 8192,
                "context_window": "32K tokens"
            }
        ]

        return {
            "success": True,
            "models": models,
            "total": len(models)
        }

    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get models")


@router.get("/ai/current")
async def get_current_model() -> Dict[str, Any]:
    """Get currently active AI model"""
    try:
        # Check configuration directly from settings
        api_configured = bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 0)

        return {
            "success": True,
            "current_model": settings.GEMINI_MODEL or "gemini-2.5-flash",
            "available": api_configured,
            "provider": "Google Gemini",
            "api_configured": api_configured,
            "note": "Configure API key from /dashboard/settings" if not api_configured else None
        }

    except Exception as e:
        logger.error(f"Error getting current model: {e}")
        raise HTTPException(status_code=500, detail="Failed to get current model")


@router.post("/ai/model/change")
async def change_ai_model(request: Request) -> Dict[str, Any]:
    """Change AI model (requires environment variable update)"""
    try:
        data = await request.json()
        new_model = data.get("model")

        if not new_model:
            raise HTTPException(status_code=400, detail="Model name required")

        # Validate model name
        valid_models = [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash"
        ]

        if new_model not in valid_models:
            raise HTTPException(status_code=400, detail=f"Invalid model. Choose from: {', '.join(valid_models)}")

        # Note: This requires updating environment variable and restarting
        # For now, we return instructions
        return {
            "success": False,
            "message": "Model change requires environment update",
            "instructions": [
                "1. Go to Railway dashboard",
                "2. Add environment variable: GEMINI_MODEL={new_model}",
                "3. Restart the service",
                f"4. Model will be updated to: {new_model}"
            ],
            "requested_model": new_model,
            "note": "Dynamic model switching will be available in future updates"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing model: {e}")
        raise HTTPException(status_code=500, detail="Failed to change model")

# ============================================================
# Admin Settings Management
# ============================================================


@router.get("/settings")
async def get_settings(category: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all settings, optionally filtered by category

    Query params:
        category: Filter by category (facebook, whatsapp, ai, system)
    """
    try:
        settings_manager = get_settings_manager_helper()
        if not settings_manager:
            raise HTTPException(status_code=503, detail="Settings manager unavailable")

        settings = settings_manager.get_all_settings(category=category)

        return {
            "success": True,
            "settings": settings,
            "count": len(settings)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve settings")


@router.get("/settings/{key}")
async def get_setting(key: str) -> Dict[str, Any]:
    """Get a specific setting by key"""
    try:
        settings_manager = get_settings_manager_helper()
        if not settings_manager:
            raise HTTPException(status_code=503, detail="Settings manager unavailable")
        value = settings_manager.get_setting(key)

        if not value:
            raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")

        return {
            "success": True,
            "key": key,
            "value": value
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting setting {key}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve setting")


@router.put("/settings/{key}")
async def update_setting(key: str, request: Request) -> Dict[str, Any]:
    """
    Update a setting

    Body:
        {
            "value": "new_value",
            "category": "ai",  # Optional
            "is_sensitive": true,  # Optional
            "description": "Setting description"  # Optional
        }
    """
    try:
        settings_manager = get_settings_manager_helper()
        if not settings_manager:
            raise HTTPException(status_code=503, detail="Settings manager unavailable")

        data = await request.json()
        value = data.get("value", "")
        category = data.get("category", "system")
        is_sensitive = data.get("is_sensitive", False)
        description = data.get("description", "")

        if not value:
            raise HTTPException(status_code=400, detail="Value is required")

        success = settings_manager.set_setting(
            key=key,
            value=value,
            category=category,
            is_sensitive=is_sensitive,
            description=description,
            updated_by="admin"
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update setting")

        return {
            "success": True,
            "message": f"Setting '{key}' updated successfully",
            "key": key
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating setting {key}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update setting")


@router.post("/settings/bulk")
async def bulk_update_settings(request: Request) -> Dict[str, Any]:
    """
    Update multiple settings at once

    Body:
        {
            "settings": [
                {
                    "key": "GEMINI_API_KEY",
                    "value": "AIzaSy...",
                    "category": "ai",
                    "is_sensitive": true,
                    "description": "Google Gemini API Key"
                },
                ...
            ]
        }
    """
    try:
        settings_manager = get_settings_manager_helper()
        if not settings_manager:
            raise HTTPException(status_code=503, detail="Settings manager unavailable")

        data = await request.json()
        settings_list = data.get("settings", [])

        if not settings_list:
            raise HTTPException(status_code=400, detail="No settings provided")

        success_count = 0
        failed_settings = []

        for setting in settings_list:
            key = setting.get("key")
            value = setting.get("value", "")
            category = setting.get("category", "system")
            is_sensitive = setting.get("is_sensitive", False)
            description = setting.get("description", "")

            if not key or not value:
                failed_settings.append({"key": key, "reason": "Missing key or value"})
                continue

            success = settings_manager.set_setting(
                key=key,
                value=value,
                category=category,
                is_sensitive=is_sensitive,
                description=description,
                updated_by="admin"
            )

            if success:
                success_count += 1
            else:
                failed_settings.append({"key": key, "reason": "Database error"})

        return {
            "success": True,
            "message": f"Updated {success_count} out of {len(settings_list)} settings",
            "updated_count": success_count,
            "total_count": len(settings_list),
            "failed": failed_settings
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk updating settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")


@router.delete("/settings/{key}")
async def delete_setting(key: str) -> Dict[str, Any]:
    """Delete a setting"""
    try:
        settings_manager = get_settings_manager_helper()
        if not settings_manager:
            raise HTTPException(status_code=503, detail="Settings manager unavailable")

        success = settings_manager.delete_setting(key)

        if not success:
            raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")

        return {
            "success": True,
            "message": f"Setting '{key}' deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting setting {key}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete setting")


@router.post("/settings/initialize")
async def initialize_settings() -> Dict[str, Any]:
    """Initialize default settings from environment variables"""
    try:
        settings_manager = get_settings_manager_helper()
        if not settings_manager:
            raise HTTPException(status_code=503, detail="Settings manager unavailable")
        settings_manager.initialize_default_settings()

        return {
            "success": True,
            "message": "Default settings initialized from environment"
        }

    except Exception as e:
        logger.error(f"Error initializing settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize settings")


@router.post("/messages/bulk")
async def send_bulk_messages(
    request: Request,
    db: Session = Depends(get_session)
) -> Dict[str, Any]:
    """Send bulk messages to multiple users"""
    try:
        data = await request.json()
        message_text = data.get("message")
        audience = data.get("audience", "all")
        schedule_time = data.get("schedule_time")

        if not message_text:
            raise HTTPException(status_code=400, detail="Message text is required")

        # Get message handler
        message_handler = get_message_handler()
        if not message_handler:
            raise HTTPException(status_code=503, detail="Message handler service unavailable")

        # Build query based on audience filter
        query = db.query(User)

        if audience == "leads":
            query = query.filter(User.customer_type == CustomerType.LEAD)
        elif audience == "active":
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            query = query.filter(User.last_message_at >= week_ago)
        elif audience == "new":
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            query = query.filter(User.created_at >= week_ago)
        elif audience == "qualified":
            query = query.filter(
                User.customer_type == CustomerType.LEAD,
                User.lead_stage.in_([LeadStage.QUALIFIED, LeadStage.HOT])
            )

        users = query.all()

        if not users:
            return {
                "success": False,
                "message": "No users found matching the criteria",
                "sent_count": 0,
                "failed_count": 0
            }

        # Send messages
        sent_count = 0
        failed_count = 0
        failed_users = []

        for user in users:
            try:
                # Personalize message
                personalized_message = message_text
                if "{name}" in personalized_message:
                    personalized_message = personalized_message.replace("{name}", user.name or "")
                if "{first_name}" in personalized_message:
                    first_name = (user.name or "").split()[0] if user.name else ""
                    personalized_message = personalized_message.replace("{first_name}", first_name)
                if "{last_name}" in personalized_message:
                    last_name = " ".join((user.name or "").split()[1:]) if user.name and len(user.name.split()) > 1 else ""
                    personalized_message = personalized_message.replace("{last_name}", last_name)

                # Send message based on platform
                if user.platform_id:  # Facebook/Messenger
                    messenger_service = get_messenger_service()
                    if messenger_service:
                        messenger_service.send_message(user.platform_id, personalized_message)
                        sent_count += 1
                    else:
                        failed_count += 1
                        failed_users.append({"user_id": user.id, "reason": "Messenger service unavailable"})
                elif user.phone_number:  # WhatsApp
                    whatsapp_service = get_whatsapp_service()
                    if whatsapp_service:
                        whatsapp_service.send_message(user.phone_number, personalized_message)
                        sent_count += 1
                    else:
                        failed_count += 1
                        failed_users.append({"user_id": user.id, "reason": "WhatsApp service unavailable"})
                else:
                    failed_count += 1
                    failed_users.append({"user_id": user.id, "reason": "No platform ID or phone number"})

            except Exception as e:
                logger.error(f"Error sending message to user {user.id}: {e}")
                failed_count += 1
                failed_users.append({"user_id": user.id, "reason": str(e)})

        return {
            "success": True,
            "message": f"Sent {sent_count} messages successfully, {failed_count} failed",
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total_users": len(users),
            "failed_users": failed_users
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending bulk messages: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to send bulk messages")
